import argparse
import configparser

from datetime import datetime

import grp,pwd 
from fnmatch import fnmatch

import hashlib

from math import ceil

import os


import re

import sys


import zlib


def repo_path(repo,*path):
    # utility function to compute path under the repo's gitdir
    return os.path.join(repo.gitdir,*path)


class GITRepo():
    # we need a way to create such objects even from (still) invalid filesystem locations

    work_tree = None
    vcs_dir = None
    conf = None

    def __init__(self,path,force=False):
        self.work_tree = path
        self.git_dir = os.path.join(path,".git")

        if not(force or os.path.isdir(self.git_dir)):
            raise Exception(f"Not a VCS repo {path}")

        # read the config file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self,"config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])

        elif not force:
            raise Exception("Configuration file missing !")

        if not force:
            vers = int(self.conf.get("core","repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion: {vers}")
        



def main(argv=sys.argv[1:]):
    print("welcome to the vcs")
    argparser = argparse.ArgumentParser(description="probably the stupidest content tracker")
    argsubparsers = argparser.add_subparsers(title="Commands",dest="command")

    argsubparsers.required = True
    args = argparser.parse_args(argv)
    match args.command:
        case "add":
            cmd_add(args)
        case "cat-file":
            cmd_cat_file(args)
        case "check-ignore":
            cmd_check_ignore(args)
        case "checkout":
            cmd_checkout(args)
        case "commit":
            cmd_commit(args)
        case "hash-object":
            cmd_hash_object(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
        case "ls-files":
            cmd_ls_files(args)
        case "ls-tree":
            cmd_ls_tree(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "rm":
            cmd_rm(args)
        case "show-ref":
            cmd_show_ref(args)
        case "status":
            cmd_status(args)
        case "tag":
            cmd_tag(args)
        case _:
            print("cmd not supported! ")             

    

if __name__ == '__main__':
    main()
