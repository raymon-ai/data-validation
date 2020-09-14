from enum import Enum

from rdv.globals import Serializable


class TagType(Enum):
    SEGM = 0
    IND = 1
    ERROR = 2


class Tag(Serializable):
    def __init__(self, name, value, tagtype, msg=None):
        self.name = name
        self.value = value
        self.tagtype = tagtype
        self.msg = msg

    def to_jcr(self):
        jcr = {
            'tagtype': self.tagtype,
            'name': self.name,
            'value': self.value,
            'msg': self.msg
        }
        return jcr

    def load_jcr(self, jcr):
        self.__init__(**jcr)
        return self

    def __str__(self):
        return f"'{self.name}:{self.value}"

    def __repr__(self):
        return f"Tag(name='{self.name}, value={self.value}, tagtype={self.tagtype}, msg={self.msg}"
