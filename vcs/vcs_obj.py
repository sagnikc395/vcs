
import os 
import zlib 
import hashlib

from .vcs_repo import repo_file
from .vcs_blob import VCSBlob
class VCSObject:
    def __init__(self, data=None) -> None:
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        # implemented by the subclasses
        # readsd the object's contents from self.data, which is a byte string and then do whatever it takes to convert
        # it to a meaningful representation, which is what depends on each subclass
        raise Exception("unimplemented")

    def deserialize(self, data):
        raise Exception("unimplemented")

    def init(self):
        pass
    

def object_read(repo, sha):
    # read an object sha from Git repository repo. return a gitobject whose exact type depends on the object.
    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # read the object type
        x = raw.find(b" ")
        fmt = raw[0:x]

        # read and validate the object size
        y = raw.find(b"\x00", x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw) - y - 1:
            raise Exception(f"Malformed object {sha}: bad length")

    # pick the construtor
    match fmt:
        case b"commit":
            c = VCSCommit
        case b"tree":
            c = VCSTree
        case b"tag":
            c = VCSTag
        case b"blob":
            c = VCSBlob
        case _:
            raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")
    
    # call the constructor and return object 
    return c(raw[y+1:])

def object_write(obj,repo=None):
    # serialize object data 
    data = obj.serialize()
    
    # add header 
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data 
    
    # compute hash 
    sha = hashlib.sha1(result).hexdigest()
    
    if repo:
        #compute again
        path = repo_file(repo,"objects",sha[0:2],sha[2:],mkdir=True)
        
        if not os.path.exists(path):
            with open(path,'wb') as f:
                # compress and write
                f.write(zlib.compress(result))
    
    return sha  

def object_find(repo,name,fmt=None,follow=True):
    return name 

def object_hash(fd,fmt,repo=None):
    # hash object , writing to repo if provided 
    data = fd.read()
    
    # choose the constructor according to fmt argument 
    match fmt:
        case b'commit': obj = VCSCommit(data)
        case b'tree': obj = VCSTree(data)
        case b'tag': obj = VCSTag(data)
        case b'blob': obj = VCSBlob(data)
    
    return object_write(obj,repo)