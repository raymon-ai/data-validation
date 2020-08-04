import json
from pydoc import locate
import tempfile
from multiprocessing import Process
import time
import webbrowser
import numpy as np


from rdv.globals import Serializable, CCAble, ClassNotFoundError
from rdv.extractors import NoneExtractor


class Stats(Serializable, CCAble):
    _config_attrs = ['min', 'max']
    _compile_attrs = ['mean', 'std', 'pinv', 'hist']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, min=None, max=None, mean=None, std=None, pinv=None, nbins=10, hist=None):
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.pinv = pinv
        self.nbins = nbins
        self.hist = hist

    def to_jcr(self):
        data = {}
        for attr in self._config_attrs + self._compile_attrs:
            data[attr] = getattr(self, attr)
        return data

    def load_jcr(self, jcr):
        for attr in self._config_attrs + self._compile_attrs:
            setattr(self, attr, jcr[attr])
        return self

    def configure(self, features):
        self.min = float(np.min(features))
        self.max = float(np.max(features))
        
    def compile(self, features):
        features = np.array(features)
        self.mean = float(np.mean(features))
        self.std = float(np.std(features))
        hist, _ = np.histogram(features, bins=self.nbins, range=(self.min, self.max), density=True)
        self.hist = hist.tolist()
        invalids = np.logical_or(features > self.max, 
                                 features < self.min, 
                                 np.isnan(features))
        self.pinv = int(np.sum(invalids)) / len(features)

class NumericComponent(Serializable, CCAble):
    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = ['extractor', 'stats']
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, name="default_name", extractor=None, stats=None):
        self.name = str(name)
        if extractor is None:
            self.extractor = NoneExtractor()
        else:
            self.extractor = extractor
        if stats is None:
            self.stats = Stats()

        else:
            self.stats = stats

    def to_jcr(self):
        data = {
            'name': self.name,
            'extractor_class': self.class2str(self.extractor),
            'extractor_config': self.extractor.to_jcr(),
            'stats': self.stats.to_jcr(),
        }
        return data

    def load_jcr(self, jcr):

        classpath = jcr['extractor_class']
        config = jcr['extractor_config']
        extr_class = locate(classpath)
        if extr_class is None:
            raise ClassNotFoundError(f"Could not locate {classpath}")

        self.extractor = extr_class(**config)
        self.stats = Stats().load_jcr(jcr['stats'])
        self.name = jcr['name']
        return self
    
    def configure_extractor(self, loaded_data):
        _, output_fpath = tempfile.mkstemp()
        print(f"Configure extractor for {self.name}")
        print(f"Saving to: {output_fpath}")
        # Crease new process
        p = Process(target=self.extractor.__class__.configure_interactive, args=(loaded_data, output_fpath, False))
        p.start()
        time.sleep(0.5)
        webbrowser.open_new('http://127.0.0.1:8050/')
        p.join()
        # Load saved config and save to extractor
        with open(output_fpath, 'r') as f:
            loaded = json.load(f)
            print(f"loaded: {loaded}")
            self.extractor.load_config(loaded)
    
    def compile_extractor(self, loaded_data):
        self.extractor.compile(loaded_data)
    
    def configure_stats(self, loaded_data):
        features = []
        for data in loaded_data:
            features.append(self.extractor.extract_feature(data))
        self.stats.configure(features)
        
    def compile_stats(self, loaded_data):
        features = []
        for data in loaded_data:
            features.append(self.extractor.extract_feature(data))
        self.stats.compile(features)
        
        
    def validate(self, data):
        feature = self.extractor.extract_feature(data)


class CategoricComponent:

    # Domain, domain distribution
    pass

