import abc
import imagehash
import os
import sys
import dash
import random
from rdv.globals import FeatureExtractor, NoneExtractor
from rdv.extractors.vision.dashapps.similarity import dash_fsps


class FixedSubpatchSimilarity(FeatureExtractor):

    _config_attrs = ['patch']
    _compile_attrs = ['refs']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    patch_keys = ['x0', 'y0', 'x1', 'y1']

    def __init__(self, patch=None, refs=None, nrefs=10):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self._nrefs = None
        self._patch = None
        self._refs = None
        
        self.patch = patch
        self.nrefs = nrefs
        self.refs = refs
    """
    PROPERTIES
    """
    @property
    def patch(self):
        return self._patch
    
    @patch.setter
    def patch(self, value):
        if value is None:
            self._patch = None
            return
        
        if not isinstance(value, dict):
            raise ValueError(f"patch must be a dict, not {type(value)}")
        # make sure the correct keys are there
        self._patch = {key: value[key] for key in self.patch_keys}
    
    @property    
    def refs(self):
        return self._refs
    
    @refs.setter
    def refs(self, value):
        if value is None:
            self._refs = None
            return 
        
        if not (isinstance(value, list) and len(value) == self.nrefs):
            raise ValueError(f"refs should be a list of length {self.nrefs}")

        
        parsed_refs = []
        for ref in value:
            if isinstance(ref, imagehash.ImageHash):
                parsed_refs.append(ref)
            elif isinstance(ref, str):
                parsed_refs.append(imagehash.hex_to_hash(ref))
            else:
                raise ValueError(f"refs should either be str or ImageHash, not {type(ref)}")
        
        self._refs = parsed_refs
        
    @property
    def nrefs(self):
        return self._nrefs

    @nrefs.setter
    def nrefs(self, value):
        value = int(value)
        if not (isinstance(value, int) and value > 0):
            self._nrefs = None
            raise ValueError(f"nrefs should be a an int > 0")
        self._nrefs = value
        
    
    """
    SERIALISATION
    """
    def to_jcr(self):
        data = {
            'patch': self.patch,
            'refs': [str(ref) for ref in self.refs] if self.refs is not None else None,
            'nrefs': self.nrefs
        }
        return data

    def load_jcr(self, jcr):
        if 'patch' in jcr:
            self.patch = jcr['patch']
        if 'nrefs' in jcr:
            self.nrefs = jcr['nrefs']
        if 'refs' in jcr:
            self.refs = jcr['refs']

        return self

    def configure(self, data):
        jcr = {
            'patch': data,
        }
        self.load_jcr(jcr)

    def compile(self, data):
        refs = []
        chosen_samples = random.choices(data, k=self.nrefs)
        for sample in chosen_samples:
            ref = self._extract(sample)
            refs.append(ref)
        self.refs = refs

    def extract_feature(self, data):
        phash = self._extract(data)
        dist = min(abs(ref - phash) for ref in self.refs)
        return dist

    def _extract(self, data):
        patch = [self.patch['x0'], self.patch['y0'], self.patch['x1'], self.patch['y1']]
        crop = data.crop(box=patch)
        phash = imagehash.phash(crop)
        return phash
    
    def configure_interactive(self, loaded_data, raymon_output, null_stderr=True):
        print(f"null_strerr: {null_stderr}")
        if null_stderr:
            f = open(os.devnull, 'w')
            sys.stderr = f
        app = dash.Dash("Data Schema Config",
                        external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        dash_fsps(app, loaded_images=loaded_data, output_path=raymon_output)
