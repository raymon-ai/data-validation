import abc
import json
from pydoc import locate
import os
import sys
import time
import webbrowser
from multiprocessing import Process
from pathlib import Path
import dash
import tempfile

from rdv.extractors.vision.dashapps.similarity import dash_fsps
from rdv.globals import Serializable, CCAble, ClassNotFoundError


class Schema(Serializable, CCAble):
    _config_attrs = ['name', 'version']
    _compile_attrs = []
    _ccable_deps = ['components']
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, name='default', version='0.0.0', components=[]):
        self.name = str(name)
        self.version = str(version)
        self.components = components

    def to_jcr(self):
        jcr = {
            'name': self.name,
            'version': self.version,
            'components': []
        }
        components = []
        for comp in self.components:
            components.append({'component_class': self.class2str(comp),
                               'component': comp.to_jcr()})
        jcr['components'] = components
        return jcr

    def load_jcr(self, jcr):
        self.name = jcr['name']
        self.version = jcr['version']
        components = []
        for comp_dict in jcr['components']:
            classpath = comp_dict['component_class']
            comp_jcr = comp_dict['component']
            compclass = locate(classpath)
            if compclass is None:
                raise ClassNotFoundError("Could not locate classpath")
            component = compclass().load_jcr(comp_jcr)
            components.append(component)

        self.components = components
        return self

    def save(self, fpath):
        with open(fpath, 'w') as f:
            json.dump(self.to_jcr(), f, indent=4)

    def load(self, fpath):
        with open(fpath, 'r') as f:
            jcr = json.load(f)
        self.load_jcr(jcr)

    def get_unconfigured(self):
        unconfigureds = []
        for component in self.components:
            if not component.is_configured():
                unconfigureds.append(component)

        return unconfigureds

    def configure_components(self, loaded_data):
        """This will configure the components extractors and stats, and will compile the extracotrs using the loaded data.
        Steps: 
        1. Find components with unconfigured extractors
        2. Select component to configure
            1. Config extractor
            2. Compile extractor & propose stats config
            3. Inspect stat config

        Args:
            loaded_data ([type]): [description]
        """
        # Find unconfigured components
        
        # Configure extractor, process loaded data (compile extractor), configure stats
        unconfigs = self.get_unconfigured()
        for comp in unconfigs:
            # Configure extractor
            comp.configure_extractor(loaded_data)
            # Compile extractor
            comp.compile_extractor(loaded_data)
            
            # Configure stats
            comp.configure_stats(loaded_data)
            
            # Compile stats
            comp.compile_stats(loaded_data)
            

    def warmup_compile(self, sample):
        """With a configured schema, this will add a sample to it's compilation.

        Args:
            sample ([type]): [description]
        """
        
        pass
    
    def compile(self):
        """Compile the schema.
        """
        pass
    

# def load_data(dpath, lim):
#     from PIL import Image

#     files = dpath.glob('*.jpeg')
#     images = []
#     for n, fpath in enumerate(files):
#         if n == lim:
#             break
#         img = Image.open(fpath)
#         images.append(img)
#     return images


def dash_process(loaded_data, raymon_output, null_stderr=True):
    if null_stderr:
        f = open(os.devnull, 'w')
        sys.stderr = f

    app = dash.Dash("Data Schema Config", external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
    dash_fsps(app, loaded_images=loaded_data, output_path=raymon_output)


# DATA_PATH = Path("/Users/kv/Raymon/Data/casting_data/train/ok_front/")
# LIM = 50
# if __name__ == '__main__':

#     loaded_data = load_data(DATA_PATH, LIM)
#     print(len(loaded_data))
#     p = Process(target=dash_process, args=(loaded_data, 'output.json'))
#     p.start()
#     time.sleep(0.5)
#     webbrowser.open_new('http://127.0.0.1:8050/')
#     p.join()

#     print("Continuing...")
