from __future__ import annotations

import os
import zlib
import hashlib
import re
from typing import BinaryIO, ClassVar

from .vcs_repo import VCSRepository, repo_file


class VCSObject:
    fmt: ClassVar[bytes] = b""

    def __init__(self, data: bytes | None = None) -> None:
        if data is not None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self) -> bytes:
        # implemented by the subclasses
        # readsd the object's contents from self.data, which is a byte string and then do whatever it takes to convert
        # it to a meaningful representation, which is what depends on each subclass
        raise Exception("unimplemented")

    def deserialize(self, data: bytes) -> None:
        raise Exception("unimplemented")

    def init(self) -> None:
        pass


class VCSRawObject(VCSObject):
    """Raw passthrough object for formats that are not parsed yet."""

    data: bytes

    def serialize(self) -> bytes:
        return self.data

    def deserialize(self, data: bytes) -> None:
        self.data = data

    def init(self) -> None:
        self.data = b""


class VCSTree(VCSRawObject):
    fmt: ClassVar[bytes] = b"tree"


class VCSTag(VCSRawObject):
    fmt: ClassVar[bytes] = b"tag"


def object_class(fmt: bytes) -> type[VCSObject] | None:
    match fmt:
        case b"commit":
            from .vcs_commit import VCSCommit

            return VCSCommit
        case b"tree":
            return VCSTree
        case b"tag":
            return VCSTag
        case b"blob":
            from .vcs_blob import VCSBlob

            return VCSBlob
        case _:
            return None


def object_read(repo: VCSRepository, sha: str) -> VCSObject | None:
    # read an object sha from Git repository repo. return a gitobject whose exact type depends on the object.
    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not path or not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # read the object type
        x = raw.find(b" ")
        if x < 0:
            raise Exception(f"Malformed object {sha}: missing type")
        fmt = raw[0:x]

        # read and validate the object size
        y = raw.find(b"\x00", x + 1)
        if y < 0:
            raise Exception(f"Malformed object {sha}: missing size terminator")
        size = int(raw[x + 1 : y].decode("ascii"))
        if size != len(raw) - y - 1:
            raise Exception(f"Malformed object {sha}: bad length")

    # pick the construtor
    c = object_class(fmt)
    if not c:
        raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")

    # call the constructor and return object
    return c(raw[y + 1 :])


def object_write(obj: VCSObject, repo: VCSRepository | None = None) -> str:
    # serialize object data
    data = obj.serialize()

    # add header
    result = obj.fmt + b" " + str(len(data)).encode() + b"\x00" + data

    # compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # compute again
        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)
        assert path is not None

        if not os.path.exists(path):
            with open(path, "wb") as f:
                # compress and write
                f.write(zlib.compress(result))

    return sha


def ref_resolve(repo: VCSRepository, ref: str) -> str | None:
    path = repo_file(repo, *ref.split("/"))
    if not path or not os.path.isfile(path):
        return None

    with open(path, "r") as fp:
        data = fp.read().strip()

    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])

    return data


def object_resolve(repo: VCSRepository, name: str) -> list[str]:
    candidates: list[str] = list()
    hash_re = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if not name:
        return candidates

    if name == "HEAD":
        head = ref_resolve(repo, "HEAD")
        if head:
            candidates.append(head)

    if hash_re.match(name):
        name = name.lower()
        prefix = name[0:2]
        path = repo_file(repo, "objects", prefix)

        if len(name) == 40:
            object_path = repo_file(repo, "objects", prefix, name[2:])
            if object_path and os.path.isfile(object_path):
                candidates.append(name)
        elif path and os.path.isdir(path):
            rest = name[2:]
            for obj in os.listdir(path):
                if obj.startswith(rest):
                    candidates.append(prefix + obj)

    for ref in (
        name,
        f"refs/{name}",
        f"refs/tags/{name}",
        f"refs/heads/{name}",
    ):
        sha = ref_resolve(repo, ref)
        if sha:
            candidates.append(sha)

    # Preserve resolution order while removing duplicate candidates.
    return list(dict.fromkeys(candidates))


def object_find(
    repo: VCSRepository, name: str, fmt: bytes | None = None, follow: bool = True
) -> str:
    candidates = object_resolve(repo, name)

    if not candidates:
        raise Exception(f"No such reference: {name}")

    if len(candidates) > 1:
        raise Exception(
            f"Ambiguous reference {name}: candidates are {', '.join(candidates)}"
        )

    sha = candidates[0]

    if not fmt:
        return sha

    while True:
        obj = object_read(repo, sha) # type: ignore
        if not obj:
            raise Exception(f"Object {sha} not found")

        if obj.fmt == fmt:
            return sha # type: ignore

        if not follow:
            break

        if obj.fmt == b"commit" and fmt == b"tree":
            from .vcs_commit import VCSCommit

            if not isinstance(obj, VCSCommit):
                break
            tree = obj.kvlm.get(b"tree")
            if tree is None or isinstance(tree, list):
                raise Exception(f"Malformed commit object {sha}: missing tree")
            sha = tree.decode("ascii") # type: ignore
        else:
            break

    raise Exception(
        f"Object {name} resolved to {sha}, but expected type {fmt.decode('ascii')}"
    )


def object_hash(fd: BinaryIO, fmt: bytes, repo: VCSRepository | None = None) -> str:
    # hash object , writing to repo if provided
    data = fd.read()

    # choose the constructor according to fmt argument
    c = object_class(fmt)
    if not c:
        raise Exception(f"Unknown type {fmt.decode('ascii')}")

    obj = c(data)

    return object_write(obj, repo)
