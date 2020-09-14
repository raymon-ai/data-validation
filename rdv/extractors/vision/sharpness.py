from PIL import ImageFilter
import numpy as np

from rdv.globals import FeatureExtractor


class Sharpness(FeatureExtractor):
    """Measures the blurryness or sharpness of an iamge. Based on
     https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    """

    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, ):
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
        filtered = img.filter(ImageFilter.Kernel((3, 3), (0, 1, 0,
                                                          1, -4, 1,
                                                          0, 1, 0), scale=1, offset=0))
        return float(np.array(filtered).var())
