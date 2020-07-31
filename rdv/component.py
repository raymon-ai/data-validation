import abc
import json
from pydoc import locate
import imagehash

from rdv.globals import Serializable, CCAble, ClassNotFoundError
from rdv.extractors import NoneExtractor


class Stats(Serializable, CCAble):
    _config_attrs = ['min', 'max', 'nbins']
    _compile_attrs = ['mean', 'std', 'pinv', 'bins']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, min=None, max=None, mean=None, std=None, pinv=None, nbins=None, bins=None):
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.pinv = pinv
        self.nbins = nbins
        self.bins = bins

    def to_jcr(self):
        data = {}
        for attr in self._config_attrs + self._compile_attrs:
            data[attr] = getattr(self, attr)
        return data

    def load_jcr(self, jcr):
        for attr in self._config_attrs + self._compile_attrs:
            setattr(self, attr, jcr[attr])
        return self


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

    def validate(self, data):
        feature = self.extractor.extract(data)


class CategoricComponent:

    # Domain, domain distribution
    pass

