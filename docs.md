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

## repository abstraction
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