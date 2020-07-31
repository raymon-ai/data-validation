import abc
import imagehash

from rdv.extractors import FeatureExtractor, NoneExtractor



class FixedSubpatchSimilarity(FeatureExtractor):

    _config_attrs = ['patch']
    _compile_attrs = ['refs']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, patch=None, refs=None):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self.patch = patch
        self.refs = refs

    def to_jcr(self):
        data = {
            'patch': self.patch,
            'refs': self.refs
        }
        return data

    def load_jcr(self, jcr):
        pass
    
    def configure_dash(self, app, data_path, lim):
        pass

    def extract(self, data):
        ahash = imagehash.average_hash(data)
        dist = min(abs(ref - ahash) for ref in self.refs)
        return dist
