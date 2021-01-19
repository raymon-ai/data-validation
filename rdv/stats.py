import numpy as np
import pandas as pd
from scipy.stats import chisquare, ks_2samp
from abc import ABC, abstractmethod

from rdv.globals import (
    Buildable,
    Serializable,
    DataException,
)


class Stats(Serializable, Buildable, ABC):
    @abstractmethod
    def sample(self, n):
        raise NotImplementedError

    @abstractmethod
    def test_drift(self, other):
        raise NotImplementedError


class NumericStats(Stats):

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

    """Testing and sampling functions"""

    def test_drift(self, other, pthresh=0.05):
        sample_self = self.sample(n=1000)
        sample_other = other.sample(n=1000)
        stat, pvalue = ks_2samp(data1=sample_self, data2=sample_other, alternative="two-sided", mode="auto")
        drift = pvalue < pthresh
        return stat, pvalue, drift

    def sample(self, n=1000, dtype="float"):
        # Sample floats in range 0 - len(percentiles)
        samples = np.random.random(n) * 100

        # We will lineraly interpolate the sample between the percentiles, so get their integer floor and ceil percentile, and the relative diztance from the floor (between 0 and 1)
        floor_percentiles = np.floor(samples).astype("uint8")
        ceil_percentiles = np.ceil(samples).astype("uint8")
        percentiles_alpha = samples - np.floor(samples)

        percentiles = np.array(self.percentiles)
        px = percentiles[floor_percentiles] * (1 - percentiles_alpha) + percentiles[ceil_percentiles] * (
            percentiles_alpha
        )

        if dtype == "int":
            return px.astype(np.int)
        else:
            return px


class CategoricStats(Stats):

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

    """Testing and sampling functions"""

    def test_drift(self, other, pthresh=0.05):
        domain_f1, domain_f2, full_domain = equalize_domains(self.domain_counts, other.domain_counts)
        sample_size = min(self.samplesize, other.samplesize)
        sampled_1 = self.sample_counts(domain_f1, keys=full_domain, n=sample_size)
        sampled_2 = self.sample_counts(domain_f2, keys=full_domain, n=sample_size)

        stat, pvalue = chisquare(f_obs=sampled_1, f_exp=sampled_2)
        drift = pvalue < pthresh
        return stat, pvalue, drift

    def sample(self, n):
        domain = sorted(list(self.domain_counts.keys()))
        # Let's be absolutely sure the domain is always in the same order
        p = [self.domain_counts[k] for k in domain]
        return np.random.choice(a=domain, size=n, p=p)

    def sample_counts(self, domain_freq, keys, n=1000):
        domain = sorted(list(keys))
        # Le's be absolutely sure the domain is always in the same order
        p = [domain_freq.get(k, 0) for k in domain]
        counts = (np.array(p) * (n - len(domain))).astype("int")
        counts += 1  # make sure there are no zeros
        return counts


def add_missing(domain_counts, full_domain):
    for key in full_domain:
        if key not in domain_counts:
            domain_counts[key] = 0
    return domain_counts


def equalize_domains(a, b):
    full_domain = sorted(list(set(set(a.keys()) | set(b.keys()))))
    a = add_missing(a, full_domain)
    b = add_missing(b, full_domain)
    return a, b, full_domain
