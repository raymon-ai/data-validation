import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

from rdv.globals import (
    Buildable,
    Serializable,
    DataException,
)


class NumericStats(Serializable, Buildable):

    _attrs = ["min", "max", "mean", "std", "pinv", "percentiles"]

    def __init__(self, min=None, max=None, mean=None, std=None, pinv=None, percentiles=None):

        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.pinv = pinv
        self.percentiles = percentiles

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

    """Percentiles"""

    @property
    def percentiles(self):
        return self._percentiles

    @percentiles.setter
    def percentiles(self, value):
        if value is None:
            self._percentiles = None
        elif len(value) == 101:
            self._percentiles = list(value)
        else:
            raise DataException("stats.percentiles must be None or a list of length 101.")

    """Size of the sample that was analyzed"""

    @property
    def samplesize(self):
        return self._samplesize

    @samplesize.setter
    def samplesize(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._samplesize = value

    """Serializable Interface"""

    def to_jcr(self):
        data = {}
        for attr in self._attrs:
            data[attr] = getattr(self, attr)
        return data

    @classmethod
    def from_jcr(cls, jcr):
        d = {}
        for attr in cls._attrs:
            d[attr] = jcr[attr]
        return cls(**d)

    """Buildable Interface"""

    def build(self, data):
        data = np.array(data)
        invalids = data[np.isnan(data)]
        data = data[~np.isnan(data)]

        self.min = float(np.min(data))
        self.max = float(np.max(data))
        self.mean = float(data.mean())
        self.std = float(data.std())

        # Build cdf estimate based on percentiles
        q = np.arange(start=0, stop=101, step=1)
        self.percentiles = np.percentile(a=data, q=q)

        # Check the invalid
        self.pinv = len(invalids) / len(data)
        self.samplesize = len(data)

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)


class CategoricStats(Serializable, Buildable):

    _attrs = ["domain_counts", "pinv", "samplesize"]

    def __init__(self, domain_counts=None, pinv=None, samplesize=None):

        self.domain_counts = domain_counts
        self.pinv = pinv
        self.samplesize = samplesize

    """domain_counts"""

    @property
    def domain_counts(self):
        return self._domain_counts

    @domain_counts.setter
    def domain_counts(self, value):
        if value is None:
            self._domain_counts = value
        elif isinstance(value, dict):
            for key, keyvalue in value.items():
                if keyvalue < 0:
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

    @property
    def samplesize(self):
        return self._samplesize

    @samplesize.setter
    def samplesize(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._samplesize = value

    def to_jcr(self):
        data = {}
        for attr in self._attrs:
            value = getattr(self, attr)
            data[attr] = value
        return data

    @classmethod
    def from_jcr(cls, jcr):
        d = {}
        for attr in cls._attrs:
            d[attr] = jcr[attr]
        return cls(**d)

    def build(self, data):
        data = pd.Series(data)
        self.domain_counts = data[~pd.isna(data)].value_counts(normalize=True).to_dict()
        invalids = data[pd.isna(data)]
        self.pinv = len(invalids) / len(data)
        self.samplesize = len(data)

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)
