import abc
import imagehash
import os
import sys
import dash
import numpy as np

from rdv.extractors import FeatureExtractor, NoneExtractor
from rdv.extractors.vision.dashapps.similarity import dash_fsps


class FixedSubpatchSimilarity(FeatureExtractor):

    _config_attrs = ['patch']
    _compile_attrs = ['refs']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps
    
    patch_keys = ['x0', 'y0', 'x1', 'y1']

    def __init__(self, patch=None, refs=None):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self.patch = patch
        self.refs = refs
        self.nrefs = 10

    def to_jcr(self):
        data = {
            'patch': self.patch,
            'refs': [str(ref) for ref in self.refs] if self.refs is not None else None
        }
        return data

    def load_jcr(self, jcr):
        if 'patch' in jcr and jcr['patch'] is not None:
            self.patch = {key: jcr['patch'][key] for key in self.patch_keys                
            }
        else:
            self.patch = None
        if 'refs' in jcr and jcr['refs'] is not None:
            self.refs = [imagehash.ImageHash(imagehash.hex_to_hash(ref)) for ref in jcr['refs']]
        else:
            self.refs = None
    
    @staticmethod
    def configure_interactive(loaded_data, raymon_output, null_stderr=True):
        if null_stderr:
            f = open(os.devnull, 'w')
            sys.stderr = f
        app = dash.Dash("Data Schema Config", 
                        external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        dash_fsps(app, loaded_images=loaded_data, output_path=raymon_output)

    def load_config(self, patch):
        jcr = {
            'patch': patch,
        }
        self.load_jcr(jcr)
    
    def compile(self, loaded_data):
        refs = []
        for data in loaded_data[:self.nrefs]:
            ref = self._extract(data)
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
    
