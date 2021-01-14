from enum import Enum

from rdv.globals import Serializable


SCHEMA_ERROR = "schema-error"
SCHEMA_FEATURE = "schema-feature"
SCHEMA_FEATURE_LH = "schema-feature-lh"
SCHEMA_GLOBAL_LH = "schema-global-lh"
LABEL = "label"
METRIC = "metric"
VECTOR = "vector"
ERROR = "error"


class Tag(Serializable):
    def __init__(self, name, value, type, group=None):
        self.name = name
        self.value = value
        self.type = type
        self.group = group

    def to_jcr(self):
        jcr = {
            "type": self.type,
            "name": self.name,
            "value": self.value,
            "group": self.group,
        }
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    def __str__(self):
        return f"'{self.name}:{self.value}"

    def __repr__(self):
        return f"Tag(name='{self.name}, value={self.value}, type={self.type}, group={self.group}"
