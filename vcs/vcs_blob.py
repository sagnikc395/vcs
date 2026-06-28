from typing import ClassVar

from .vcs_obj import VCSObject


class VCSBlob(VCSObject):
    fmt: ClassVar[bytes] = b"blob"
    blobdata: bytes

    def serialize(self) -> bytes:
        return self.blobdata

    def deserialize(self, data: bytes) -> None:
        self.blobdata = data

    def init(self) -> None:
        self.blobdata = b""
