# type: ignore

import os
import zlib
from .repo import repo_file


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
