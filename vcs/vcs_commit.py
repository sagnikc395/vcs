from typing import ClassVar

from .vcs_obj import VCSObject, object_read
from .vcs_repo import VCSRepository


KvlmValue = bytes | list[bytes]
KvlmDict = dict[bytes | None, KvlmValue]


class VCSCommit(VCSObject):
    fmt: ClassVar[bytes] = b"commit"
    kvlm: KvlmDict

    def deserialize(self, data: bytes) -> None:
        self.kvlm = kvlm_parse(data)

    def serialize(self) -> bytes:
        return kvlm_serialize(self.kvlm)

    def init(self) -> None:
        self.kvlm = dict()


def kvlm_serialize(kvlm: KvlmDict) -> bytes:
    ret = b""

    # Output fields
    for k, val in kvlm.items():
        # Skip the message itself
        if k is None:
            continue
        # Normalize to a list
        values = val if isinstance(val, list) else [val]

        for v in values:
            ret += k + b" " + (v.replace(b"\n", b"\n ")) + b"\n"

    # Append message
    message = kvlm.get(None, b"")
    if isinstance(message, list):
        raise Exception("Malformed commit: message cannot have multiple values")
    ret += b"\n" + message

    return ret


def kvlm_parse(raw: bytes, start: int = 0, dct: KvlmDict | None = None) -> KvlmDict:
    if dct is None:
        dct = dict()
        # You CANNOT declare the argument as dct=dict() or all call to
        # the functions will endlessly grow the same dict.

    # This function is recursive: it reads a key/value pair, then call
    # itself back with the new position.  So we first need to know
    # where we are: at a keyword, or already in the messageQ

    # We search for the next space and the next newline.
    spc = raw.find(b" ", start)
    nl = raw.find(b"\n", start)

    # If space appears before newline, we have a keyword.  Otherwise,
    # it's the final message, which we just read to the end of the file.

    # Base case
    # =========
    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line.  A blank line
    # means the remainder of the data is the message.  We store it in
    # the dictionary, with None as the key, and return.
    if (spc < 0) or (0 <= nl < spc):
        if nl != start:
            raise Exception("Malformed commit: missing message separator")
        dct[None] = raw[start + 1 :]
        return dct

    # Recursive case
    # ==============
    # we read a key-value pair and recurse for the next.
    key = raw[start:spc]

    # Find the end of the value.  Continuation lines begin with a
    # space, so we loop until we find a "\n" not followed by a space.
    end = start
    while True:
        end = raw.find(b"\n", end + 1)
        if end < 0:
            raise Exception("Malformed commit: unterminated header")
        if end + 1 >= len(raw) or raw[end + 1] != ord(" "):
            break

    # Grab the value
    # Also, drop the leading space on continuation lines
    value = raw[spc + 1 : end].replace(b"\n ", b"\n")

    # Don't overwrite existing data contents
    if key in dct:
        existing = dct[key]
        if isinstance(existing, list):
            existing.append(value)
        else:
            dct[key] = [existing, value]
    else:
        dct[key] = value

    return kvlm_parse(raw, start=end + 1, dct=dct)


def log_graphviz(repo: VCSRepository, sha: str, seen: set[str]) -> None:
    if sha in seen:
        return
    seen.add(sha)

    commit = object_read(repo, sha)
    if not isinstance(commit, VCSCommit):
        raise Exception(f"Object {sha} is not a commit")

    raw_message = commit.kvlm.get(None, b"")
    if isinstance(raw_message, list):
        raise Exception(f"Malformed commit object {sha}: multiple messages")
    message = raw_message.decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace('"', '\\"')

    if "\n" in message:  # Keep only the first line
        message = message[: message.index("\n")]

    print(f'  c_{sha} [label="{sha[0:7]}: {message}"]')

    if b"parent" not in commit.kvlm:
        # Base case: the initial commit.
        return

    parents = commit.kvlm[b"parent"]

    if not isinstance(parents, list):
        parents = [parents]

    for p in parents:
        p = p.decode("ascii")
        print(f"  c_{sha} -> c_{p};")
        log_graphviz(repo, p, seen)
