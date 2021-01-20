from abc import ABC, abstractmethod

from rdv.globals import (
    Buildable,
    Serializable,
)


class FeatureExtractor(Serializable, Buildable, ABC):
    @abstractmethod
    def extract_feature(self, data):
        """Extracts a feature from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a feature from. The type is up to you.

        """
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


class NoneExtractor(FeatureExtractor):
    def to_jcr(self):
        data = {}
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls()

    def extract(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        return 0

    def build(self, data):
        pass

    def is_built(self):
        return True

    def extract_feature(self, data):
        pass
