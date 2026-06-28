import os
import configparser
from typing import Literal, overload


class VCSRepository:
    # define and create a new git repository

    worktree: str
    gitdir: str
    conf: configparser.ConfigParser

    def __init__(self, path: str, force: bool = False) -> None:
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            # check if gitdir or not
            raise Exception(f"Not a git repository {path}")

        # read the configuration from .git/config , parse the ini reader
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            versions = int(self.conf.get("core", "repositoryformatversion"))
            if versions != 0:
                raise Exception(f"Unsupported repositoryformatversions: {versions}")


def repo_path(repo: VCSRepository, *path: str) -> str:
    # made it variadic, so that be called with multiple path components
    # as seperate arguments
    # utility to compute path under repo's gitdir
    return os.path.join(repo.gitdir, *path)


def repo_file(repo: VCSRepository, *path: str, mkdir: bool = False) -> str | None:
    # same as repo_path, but will create a dirname(*path) if absent
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo: VCSRepository, *path: str, mkdir: bool = False) -> str | None:
    # same as repo_path, but mkdir *path if absent if mkdir
    full_path = repo_path(repo, *path)

    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            return full_path
        else:
            raise Exception(f"Not a directory {full_path}")

    if mkdir:
        os.makedirs(full_path)
        return full_path
    else:
        return None


def repo_create(path: str) -> VCSRepository:
    ## create a new repo at path
    repo = VCSRepository(path, True)

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
    description_path = repo_file(repo, "description")
    assert description_path is not None
    with open(description_path, "w") as f:
        f.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    # .git/HEAD
    head_path = repo_file(repo, "HEAD")
    assert head_path is not None
    with open(head_path, "w") as f:
        f.write("ref: refs/heads/master\n")

    config_path = repo_file(repo, "config")
    assert config_path is not None
    with open(config_path, "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


# create config
def repo_default_config() -> configparser.ConfigParser:
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret


@overload
def repo_find(path: str = ".", required: Literal[True] = True) -> VCSRepository: ...


@overload
def repo_find(
    path: str = ".", required: Literal[False] = False
) -> VCSRepository | None: ...


def repo_find(path: str = ".", required: bool = True) -> VCSRepository | None:
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return VCSRepository(path)

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
