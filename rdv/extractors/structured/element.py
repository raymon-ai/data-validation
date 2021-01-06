from PIL import Image
import numpy as np

from rdv.extractors import FeatureExtractor


class ElementExtractor(FeatureExtractor):
    """
    Extract one element from a vector
    """

    def __init__(self, element):
        self.element = element

    """ELEMENT"""

    @property
    def element(self):
        return self._element

    @element.setter
    def element(self, value):
        if not (isinstance(value, str) or isinstance(value, int)):
            raise DataException("element ot extract must be int or str")
        self._element = value

    def extract_feature(self, data):
        return data[self.element]

    """Serializable interface """

    def to_jcr(self):
        data = {
            "element": self.element,
        }
        return data

    def load_jcr(self, jcr):
        if "element" in jcr:
            self.element = jcr["element"]

        return self

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True
