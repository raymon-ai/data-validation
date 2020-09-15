from PIL import Image
import numpy as np

from rdv.globals import FeatureExtractor


class ElementExtractor(FeatureExtractor):
    """
    Extract one element from a vector
    """
    # Configure attributes that are required for configuratio and compilation
    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, element=None):
        self.element = element

    def to_jcr(self):
        data = {
            'element': self.element,
        }
        return data

    def load_jcr(self, jcr):
        if 'element' in jcr:
            self.element = jcr['element']
        
        return self

    def configure(self, data):
        pass

    def compile(self, data):
        pass

    def extract_feature(self, data):
        return data[self.element]
