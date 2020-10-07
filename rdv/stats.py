import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

from rdv.globals import (CCAble, NoneExtractor,
                         NotSupportedException, Serializable, DataException)




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

    """MIN"""  
    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        if value is np.nan:
            raise DataException("stats.min cannot be NaN")
        self._min = value
    """MAX"""  
    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        if value is np.nan:
            raise DataException("stats.max cannot be NaN")
        self._max = value
    
    """MEAN"""
    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, value):
        if value is np.nan:
            raise DataException("stats.mean cannot be NaN")
        self._mean = value
        
    """STD"""
    @property
    def std(self):
        return self._std

    @std.setter
    def std(self, value):
        if value is np.nan:
            raise DataException("stats.std cannot be NaN")
        self._std = value
    
    """PINV"""
    @property
    def pinv(self):
        return self._pinv

    @pinv.setter
    def pinv(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._pinv = value
        

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
        hist, edges = np.histogram(data, bins=self.nbins, range=(self.min, self.max))
        hist = hist / np.sum(hist)
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
        
    """domain"""
    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        if value is None:
            self._domain = value
        elif isinstance(value, list):
            self._domain = list(set(value))
        else:
            raise DataException("stats.domain should be a list")
        
        
    """domain_counts"""
    @property
    def domain_counts(self):
        return self._domain_counts

    @domain_counts.setter
    def domain_counts(self, value):
        if value is None:
            self._domain_counts = value
        elif isinstance(value, dict):
            for key, value in value.items():
                if key not in self.domain:
                    raise DataException(f"{key} is not in domain but is in domain_counts")
                if value < 0:
                    raise DataException(f"Domain count for {key} is  < 0")
            self._domain_counts = value
        else:
            raise DataException(f"stats.domain_counts should be a dict, not {type(value)}")
        

    """PINV"""
    @property
    def pinv(self):
        return self._pinv

    @pinv.setter
    def pinv(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._pinv = value
        
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
