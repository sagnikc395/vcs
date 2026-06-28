# type: ignore
import os
import configparser

from .vcs_repo import GitRepository


def repo_path(repo, *path):
    # made it variadic, so that be called with multiple path components
    # as seperate arguments
    # utility to compute path under repo's gitdir
    return os.path.join(repo.gitdir, *path)


def repo_file(repo, *path, mkdir=False):
    # same as repo_path, but will create a dirname(*path) if absent
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo, *path, mkdir=False):
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


def repo_create(path):
    ## create a new repo at path
    repo = GitRepository(path, True)

    # first make sure that the path either doesnt exist or is an empty dir
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


# create config
def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret


def repo_find(path=".", required=True):
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    # if we haven't returned, recurse in parent
    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # base case
        # no git
        if required:
            raise Exception("no git directory")
        else:
            return None

    return repo_find(parent, required)
