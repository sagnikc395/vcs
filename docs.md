## features

- add
- cat-file
- check-ignore
- checkout
- commit
- hash-object
- init
- log
- ls-files
- ls-tree
- rev-parse
- rm
- show-ref
- status
- tag


etc. either things that is perfectly compatible with git itself.

### repository abstraction
- almost every time we run a git command, we are trying to do something to a repo, to create it, read from it or modify it.
- git repo made of 2 things:
    - a work tree -> where the files are meant to be in version control lives. worktree is a regular directory and the git directory is a child directory of the worktree called .git
    - a git directory -> where git stores its own data.

- git actually supports much more cases (bare repo, seperated gitdir), but supporting the basic approach of worktree/git. Our repository object will then just hold two paths:
    - worktree and the gitdir 

- for creating a new Repoisotry object, we only need to make a few checks:
    - we must verify that the directory exists, and contains a subdirectory called .git
    - we then read its configuration in .git/config -> an INI file, and checks that core.repositoryformatversion is 0. 

-`repo_path`:
    - utility function to compute paths and create missing directory structures if needed.
- `repo_file`:
    - return and optionally create a path to a file 
- `repo_dir`:
    - return and optionally create a path to a dir. File versions only creates the directories upto the last component.

- to create a new repo, we start with a directory, that directory is called .git and contains:
    - .git/objects/ -> the object store
    - .git/refs/ -> reference store
    - .git/HEAD -> a reference to the current HEAD 
    - .git/config > repo's config file
    
- config file is very simple, a INI like file with a single section ([core]) and 3 fields:
    - repositoryformatversion = 0 -> the version of the gitdir format. 0 means the initial format, 1 the same with extensions. if > 1, we ignore, we accept only 0
    - filemode=false, disables tracking of the file modes (permissions) changes in the work tree 
    - base=false; indicates that this repo has a worktree.Git supports an optional worktree key which indicates the location of the worktree.

### objects:
- git at its core is a content-addressed filesystem.
- unlike regular filesystems, where the name of a file is arbitary and unrelated to that file's contents, the names of files are stored by Git are mathematically derived from their contents.
- if a single byte of text file changes,its internal name will change too. 
- we dont simply modify a file in git, we create a new file in a different location.
- objects are files in git repo, whose paths are determined by their contents.
- git uses objects to store quite a lot of things : 
    - the actual files it keeps in version conttrol - source code for example
    - commit are objects too, as well as tags.
    - almost everything in git, is stored as an object.

-  An object starts with a header that specifies its type: blob, commit, tag or tree (more on that in a second). This header is followed by an ASCII space (0x20), then the size of the object in bytes as an ASCII number, then null (0x00) (the null byte), then the contents of the object.
- objects (headers and contents) are stored compressed with zlib. 

- the path where git stores a given object is computed by calculating the SHA-1 hash of its content, renders the hash as a lowercase hexadecimal string, and splits it in 2 parts:
    - first two characters and the rest 
    - first part as a directory name and the rest as the file name down to a crawl.
    - this creates 256 possible intermediate directories, hence dividing the average number of files per directory by 256.

### Generic Object Object
- objects can be of multiple types, but they all share the same storage/retrieval mechanism and the same general header format.
- before we dive into the details of various types of objects, we need to abstract over these common features.
- easiest way is to create a generic `GitObject` with 2 methods : serialize() and deserialize() and a default init() to create a new emtpy object if needed.
- the `__init__` either loads the object from the provided data or calls the subclasses provided `init()` to create a new.empty object.

#### Reading Objects:
- To read a object, we need to know its SHA-1 hash. 
- We then compute its path from this hash , and look it up inside of the "objects" directory in the gitdir.
- We then read that file as a binary file, and decompress it using zlib.
- From the decompressed data, we extract the two header components: the object type and its size. From the type, we determine the actual class to use. We convert the size to a Python integer, and check if it matches.
- When done, we just cacll the correct constructer for that object's format.

#### Writing Objects:
- Writing a object is reading it in reverse: we compute the hash, insert the header, zlib-compress everything and write the result in the current location.
- hash is just computed after the header is added (so its the hash of the object itself ,uncompressed ,not just its contents).

#### Working with blobs:
- type header could be one of 4:
    - blob
    - commit
    - tag 
    - tree
- blobs are the simplest of those 4 types , because they have no actual format.
- blobs are user data: the content of every file we put in git is stored as a blob. 
- makes them easy to manipulate as they have no actual syntax or constraints beyond the basic object storage mechanism: they are just unspecified data.
- `VCSBlob` is trivial: serialize and deserialize functions just have to store and return their input unmodified.

### cat file command:
- simply prints the raw content of an object to stdout , uncompressed and without the git header.
- just take two positional arguments: a type and aobject identifier.
`vcs cat-file TYPE OBJECT`
- `object_find` is introduced because Git has a lot of ways to refer to objects: full hash, short hash, tags. 
- this is used as our name resolution function.

### hash-object command:
- want to put our own data in our repo, though , hash-object is basically the opposite of `cat-file`: it reads a file, computes its hash as an object, either storing it in the repo or just printing its hash.
`wyag hash-object [-w] [-t TYPE] FILE`

### parsing commits:
- format is simplified version of mail messages. it begins with a series of key-value pairs, with space as the k/v seperator and ends with the commit message, that may span over multiple lines.
- values may continue over multiple lines, subsequent lines start with a space which the parser must drop.
- fields:
    - tree -> reference to a tree object. A tree map blobs IDs to filesystem locations. and describes a state of the work tree. Put simply, it is the actual content of the commit : file contents, and where they go.
    - parent -> reference to the parent of this commit . it may be repeated: merge cmmits, for ex: have multiple parents. It may also be absent, the very first commit in a repo obviously doesnt have a parent.
    - author and committer -> seperate, because the author of a commit is not necessarily the person who can commit it.
    - gpgsig -> PGP signature of this object.

- So what makes a commit? To sum it up:

A tree object, which we’ll discuss in detail in the next section, that describes the contents of the commit: files and directories;
Zero, one or more parents;
An author identity (name and email), and a timestamp;
A committer identity (name and email), and a timestamp;
An optional PGP signature
A message;
All this hashed together in a unique SHA-1 identifier.