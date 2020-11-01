from PIL import Image, ImageFilter
import numpy as np

from rdv.globals import FeatureExtractor


class AvgIntensity(FeatureExtractor):

    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(
        self,
    ):
        pass

    def to_jcr(self):
        return {}

    def load_jcr(self, jcr):
        return self

    def configure(self, data):
        pass

    def compile(self, data):
        pass

    def extract_feature(self, data):
        img = data
        img = img.convert("L")
        return float(np.array(img).mean())
