# type: ignore
import os 

from .git_repo import GitRepository

def repo_find(path=".", required=True):
    path = os.path.realpath(path)
    
    if os.path.isdir(os.path.join(path,".git")):
        return GitRepository(path)
    
    # if we haven't returned, recurse in parent 
    parent = os.path.realpath(os.path.join(path,".."))
    
    if parent == path:
        # base case 
        # no git 
        if required:
            raise Exception("no git directory")
        else:
            return None 
        
    return repo_find(parent,required)
