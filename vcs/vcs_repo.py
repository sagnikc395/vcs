import os
import configparser


class VCSRepository:
    # define and create a new git repository

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):  # type: ignore
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")  # type: ignore

        if not (force or os.path.isdir(self.gitdir)):
            # check if gitdir or not
            raise Exception(f"Not a git repository {path}")

        # read the configuration from .git/config , parse the ini reader
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")  # type: ignore

        if cf and os.path.exists(cf):  # type: ignore
            self.conf.read([cf])  # type: ignore
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            versions = int(self.conf.get("core", "repositoryformatversion"))
            if versions != 0:
                raise Exception(f"Unsupported repositoryformatversions: {versions}")
