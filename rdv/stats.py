import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

from rdv.globals import (CCAble, NoneExtractor,
                         NotSupportedException, Serializable)


class NumericStats(Serializable, CCAble):
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

    def configure(self, data):
        self.min = float(np.min(data))
        self.max = float(np.max(data))

    def compile(self, data):
        data = pd.Series(data)
        self.mean = float(data.mean())
        self.std = float(data.std())
        hist, _ = np.histogram(data, bins=self.nbins, range=(self.min, self.max), density=True)
        self.hist = hist.tolist()
        invalids = np.logical_or(data > self.max,
                                 data < self.min,
                                 np.isnan(data.values))
        self.pinv = int(np.sum(invalids)) / len(data)

    def distance(self, other):
        if self.min != other.min or self.max != other.max:
            raise ValueError("Cannot compare Stats that have unequal min and/or max.")
        return wasserstein_distance(self.hist, other.hist)


class CategoricStats(Serializable, CCAble):
    _config_attrs = ['domain']
    _compile_attrs = ['domain_counts', 'pinv']
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, domain=None, domain_counts=None, pinv=None):
        self.domain = domain
        self.domain_counts = domain_counts  # TODO move to property, check whether does not include keys not in domain
        self.pinv = pinv

    def to_jcr(self):
        data = {}
        for attr in self._config_attrs + self._compile_attrs:
            value = getattr(self, attr)
            if attr == 'domain' and value is not None:
                data[attr] = list(value)
            else:
                data[attr] = value
        return data

    def load_jcr(self, jcr):
        for attr in self._config_attrs + self._compile_attrs:
            value = jcr[attr]
            if attr == 'domain' and value is not None:
                setattr(self, attr, set(value))
            else:
                setattr(self, attr, value)
        return self

    def configure(self, data):
        unique = data.unique()
        unique = unique[~pd.isnull(unique)]
        self.domain = list(set(unique))

    def compile(self, data):
        data = pd.Series(data)
        # Only use values in configured domain
        data_filt = data[data.isin(self.domain)]
        self.domain_counts = data_filt.value_counts(normalize=True).to_dict()
        # Invalids are data outside domain
        invalids = data[~data.isin(self.domain) | pd.isna(data)]
        self.pinv = len(invalids) / len(data)

    def distance(self, other):
        raise NotImplementedError
