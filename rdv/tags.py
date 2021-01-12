from enum import Enum

from rdv.globals import Serializable


SEG = "seg"
IND = "ind"
ERR = "err"


class Tag(Serializable):
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

    def to_jcr(self):
        jcr = {
            "type": self.type,
            "name": self.name,
            "value": self.value,
        }
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    def __str__(self):
        return f"'{self.name}:{self.value}"

    def __repr__(self):
        return f"Tag(name='{self.name}, value={self.value}, type={self.type}"
