from vcs_obj import VCSObject


class VCSBlob(VCSObject):
    fmt = b'blob'
    
    def serialize(self, repo):
        super().serialize(repo)
        return self.blobdata 

    def deserialize(self, data):
        super().deserialize(data)
        self.blobdata = data 