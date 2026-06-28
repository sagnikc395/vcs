# type: ignore


class VCSObject:
    def __init__(self, data=None) -> None:
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        # implemented by the subclasses
        # readsd the object's contents from self.data, which is a byte string and then do whatever it takes to convert
        # it to a meaningful representation, which is what depends on each subclass
        raise Exception("unimplemented")

    def deserialize(self, data):
        raise Exception("unimplemented")

    def init(self):
        pass
