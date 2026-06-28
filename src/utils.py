# type: ignore
import os 

def repo_path(repo, *path): 
    # made it variadic, so that be called with multiple path components 
    # as seperate arguments 
    # utility to compute path under repo's gitdir 
    return os.path.join(repo.gitdir,*path) 

def repo_file(repo,*path, mkdir=False):
    # same as repo_path, but will create a dirname(*path) if absent
    if repo_dir(repo,*path[:-1],mkdir=mkdir):
        return repo_path(repo,*path)
    
def repo_dir(repo,*path,mkdir=False):
    # same as repo_path, but mkdir *path if absent if mkdir 
    path = repo_path(repo, *path)
    
    if os.path.exists(path):
        if os.path.isdir(path):
            return path 
        else:
            raise Exception(f"Not a directory {path}")
    
    if mkdir:
        os.makedirs(path)
        return path 
    else:
        return None 
    
