from abc import ABC, abstractmethod

from rdv.globals import (
    Buildable,
    Serializable,
)


class FeatureExtractor(Serializable, Buildable, ABC):
    @abstractmethod
    def extract_feature(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        raise NotImplementedError


class NoneExtractor(FeatureExtractor):
    def to_jcr(self):
        data = {}
        return data

    def load_jcr(self, jcr):
        return self

    def extract(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        return 0

    def build(self, data):
        pass

    def is_built(self, data):
        return True

    def extract_feature(self, data):
        pass
