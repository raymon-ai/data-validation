from collections.abc import Iterable
from pydoc import locate
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from plotly import graph_objects as go
from scipy.stats import chisquare, ks_2samp
import plotly.express as px
from plotly.subplots import make_subplots


PLOTLY_COLORS = px.colors.qualitative.Plotly

from rdv.globals import (
    Buildable,
    Configurable,
    Serializable,
    DataException,
    SchemaStateException,
)
from rdv.stats import CategoricStats, NumericStats
from rdv.tags import Tag, SCHEMA_ERROR, SCHEMA_FEATURE
from rdv.extractors.structured import ElementExtractor
from rdv.extractors import NoneExtractor


class Feature(Serializable, Buildable, ABC):
    def __init__(self, name="default_name", extractor=None):
        self.name = str(name)
        if extractor is None:
            self.extractor = NoneExtractor()
        else:
            self.extractor = extractor
        if isinstance(self.extractor, Configurable):
            self.extractor.idfr = self.name

        self.stats = None

    """Serializable interface """

    def to_jcr(self):
        data = {
            "name": self.name,
            "extractor_class": self.extractor.class2str(),
            "extractor_state": self.extractor.to_jcr(),
            "stats": self.stats.to_jcr(),
        }
        return data

    def build_extractor(self, loaded_data):
        self.extractor.build(loaded_data)

    def build_stats(self, loaded_data):
        print(f"Compiling stats for {self.name}")
        features = self.extract_features(loaded_data)
        self.stats.build(features)

    def extract_features(self, loaded_data):
        features = []
        if isinstance(loaded_data, pd.DataFrame):
            features = self.extractor.extract_feature(loaded_data)
        elif isinstance(loaded_data, Iterable):
            for data in loaded_data:
                features.append(self.extractor.extract_feature(data))
        else:
            raise DataException("loaded_data should be a DataFrame or Iterable")
        return features

    def build(self, data):
        # Compile extractor
        self.build_extractor(data)
        # Configure stats
        self.build_stats(data)

    def is_built(self):
        return self.extractor.is_built() and self.stats.is_built()

    def requires_config(self):
        return isinstance(self.extractor, Configurable) and not self.extractor.is_configured()

    def check(self, data):

        feature = self.extractor.extract_feature(data)
        # Make a tag from the feature
        feat_tag = self.feature2tag(feature)
        # Check min, max, nan or None and raise data error
        err_tag = self.check_invalid(feature)
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @abstractmethod
    def feature2tag(self, feature):
        pass

    @abstractmethod
    def check_invalid(self, feature):
        pass

    def __repr__(self):
        return str(self)

    @abstractmethod
    def plot(self, poi, size, hist):
        pass


class FloatFeature(Feature):
    def __init__(self, name="default_name", extractor=None, stats=None):
        super().__init__(name=name, extractor=extractor)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = NumericStats()
        elif isinstance(value, NumericStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type NumericStats, not {type(value)}")

    def feature2tag(self, feature):
        if not np.isnan(feature):
            return Tag(name=self.name, value=float(feature), type=SCHEMA_FEATURE)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=SCHEMA_ERROR)
        elif np.isnan(feature):
            return Tag(name=tagname, value="Value NaN", type=SCHEMA_ERROR)
        elif feature > self.stats.max:
            return Tag(name=tagname, value="Value > max", type=SCHEMA_ERROR)
        elif feature < self.stats.min:
            return Tag(name=tagname, value="Value < min", type=SCHEMA_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = NumericStats.from_jcr(jcr["stats"])
        name = jcr["name"]
        return cls(name=name, extractor=extractor, stats=stats)

    def __str__(self):
        return f"FloatFeature(name={self.name}, extractor={self.extractor})"

    def plot(self, poi=None, size=(800, 500), hist=True):
        if not self.is_built():
            raise SchemaStateException(f"Feature {self.name} has not been built. Cannot plot unbuilt components.")
        fig = go.Figure()

        # fig = go.Figure()
        fig.add_trace(get_cdf(self.stats.percentiles))
        if hist:
            fig.add_trace(get_histogram(self.stats.percentiles))

        fig.update_xaxes(range=[self.stats.percentiles[0], self.stats.percentiles[-1]])
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            height=size[1],
            width=size[0],
            template="plotly_white",
            # title_text=f"cdf for {self.name}",
            xaxis_title=self.name,
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
        )

        if poi and (isinstance(poi, float) or isinstance(poi, int)):
            fig.add_shape(
                type="line",
                x0=poi,
                y0=0,
                x1=poi,
                y1=100,
                line=dict(color=PLOTLY_COLORS[-1], width=1),
                name="poi",
            )
        return fig


class IntFeature(Feature):
    def __init__(self, name="default_name", extractor=None, stats=None):
        super().__init__(name=name, extractor=extractor)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = NumericStats()
        elif isinstance(value, NumericStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type NumericStats, not {type(value)}")

    def feature2tag(self, feature):
        if not np.isnan(feature):
            return Tag(name=self.name, value=float(feature), type=SCHEMA_FEATURE)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=SCHEMA_ERROR)
        elif np.isnan(feature):
            return Tag(name=tagname, value="Value NaN", type=SCHEMA_ERROR)
        elif feature > self.stats.max:
            return Tag(name=tagname, value="Value > max", type=SCHEMA_ERROR)
        elif feature < self.stats.min:
            return Tag(name=tagname, value="Value < min", type=SCHEMA_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = NumericStats.from_jcr(jcr["stats"])
        name = jcr["name"]
        return cls(name=name, extractor=extractor, stats=stats)

    def __str__(self):
        return f"IntFeature(name={self.name}, extractor={self.extractor})"

    def plot(self, poi=None, size=(800, 500), hist=True):
        if not self.is_built():
            raise SchemaStateException(f"Feature {self.name} has not been built. Cannot plot unbuilt components.")
        fig = go.Figure()

        # fig = go.Figure()
        fig.add_trace(get_cdf(self.stats.percentiles))
        if hist:
            fig.add_trace(get_histogram(self.stats.percentiles))

        fig.update_xaxes(range=[self.stats.percentiles[0], self.stats.percentiles[-1]])
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            height=size[1],
            width=size[0],
            template="plotly_white",
            # title_text=f"cdf for {self.name}",
            xaxis_title=self.name,
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
        )

        if poi and (isinstance(poi, float) or isinstance(poi, int)):
            fig.add_shape(
                type="line",
                x0=poi,
                y0=0,
                x1=poi,
                y1=100,
                line=dict(color=PLOTLY_COLORS[-1], width=1),
                name="poi",
            )
        return fig


class CategoricFeature(Feature):

    # Domain, domain distribution
    def __init__(self, name="default_name", extractor=None, stats=None):
        super().__init__(name=name, extractor=extractor)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = CategoricStats()
        elif isinstance(value, CategoricStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type CategoricStats, not {type(value)}")

    def feature2tag(self, feature):
        return Tag(name=self.name, value=feature, type=SCHEMA_FEATURE)

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=SCHEMA_ERROR)
        elif pd.isnull(feature):
            return Tag(name=tagname, value="Value NaN", type=SCHEMA_ERROR)
        elif feature not in self.stats.domain_counts:
            return Tag(name=tagname, value="Domain Error", type=SCHEMA_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = CategoricStats.from_jcr(jcr["stats"])
        name = jcr["name"]

        return cls(name=name, extractor=extractor, stats=stats)

    def __str__(self):
        return f"CategoricFeature(name={self.name}, extractor={self.extractor})"

    def plot(self, poi=None, size=(800, 500), hist=True):
        if not self.is_built():
            raise SchemaStateException(f"Feature {self.name} has not been built. Cannot plot unbuilt components.")

        domain = sorted(list(self.stats.domain_counts.keys()))
        # Let's be absolutely sure the domain is always in the same order
        p = [self.stats.domain_counts[k] * 100 for k in domain]
        cdf = np.cumsum(p).astype("int")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=domain, y=cdf, name="cdf"))
        if hist:
            fig.add_trace(go.Bar(x=domain, y=p, name="value freq"))

        # fig.update_xaxes(range=[self.stats.percentiles[0], self.stats.percentiles[-1]])
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            height=size[1],
            width=size[0],
            template="plotly_white",
            # title_text=f"cdf for {self.name}",
            xaxis_title=self.name,
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
        )

        if poi and isinstance(poi, str):
            fig.add_shape(
                type="line",
                x0=poi,
                y0=0,
                x1=poi,
                y1=100,
                line=dict(color=PLOTLY_COLORS[-1], width=1),
                name="poi",
            )
        return fig

    # def plot(self, poi=None):
    #     if not self.is_built():
    #         raise SchemaStateException(f"Feature {self.name} has not been built. Cannot plot unbuilt components.")

    #     domain = sorted(list(self.stats.domain_counts.keys()))
    #     colors = [PLOTLY_COLORS[0] if e != poi else PLOTLY_COLORS[-1] for e in domain]
    #     # Let's be absolutely sure the domain is always in the same order
    #     p = [self.stats.domain_counts[k] for k in domain]
    #     cdf = np.cumsum(p).astype("int")
    #     fig = go.Figure()
    #     fig.add_trace(go.Bar(x=domain, y=p, marker_color=colors, name="value freq"))
    #     fig.add_trace(go.Scatter(x=domain, y=cdf, name="cdf"))

    #     fig.update_layout(
    #         # height=500,
    #         # width=800,
    #         title_text=f"Value frequencies for {self.name}",
    #         xaxis_title="Category",
    #         yaxis_title="pdf",
    #     )

    #     return fig

    def plot_compare(self, other):
        def get_bartrace(domain_counts, name):
            return go.Bar(x=list(domain_counts.keys()), y=list(domain_counts.values()), name=name)

        domain_f1, domain_f2, full_domain = equalize_domains(self.stats.domain_counts, other.stats.domain_counts)

        fig = go.Figure()
        fig.add_trace(get_bartrace(domain_f1, name="self"))
        fig.add_trace(get_bartrace(domain_f2, name="other"))
        # ddof = (len(domain) - 1) ** 2
        stat, pvalue = self.drift(other)
        # If pvalue small enough -> H0 does not hold -> drift
        fig.update_layout(
            # height=500,
            # width=800,
            title_text=f"stat: {stat}, pvalue: {pvalue}",
            xaxis_title="Category",
            yaxis_title="pdf",
        )

        return fig

    def drift(self, other):
        domain_f1, domain_f2, full_domain = equalize_domains(self.stats.domain_counts, other.stats.domain_counts)
        sample_size = min(self.stats.samplesize, other.stats.samplesize)
        sampled_1 = sample_counts(domain_f1, keys=full_domain, n=sample_size)
        sampled_2 = sample_counts(domain_f2, keys=full_domain, n=sample_size)

        stat, pvalue = chisquare(f_obs=sampled_1, f_exp=sampled_2)
        return stat, pvalue


def construct_components(dtypes):
    components = []
    for key in dtypes.index:
        # Check type: Numeric or categoric
        extractor = ElementExtractor(element=key)
        if np.issubdtype(dtypes[key], np.floating):
            component = FloatFeature(name=key, extractor=extractor)
        elif np.issubdtype(dtypes[key], np.integer):
            component = IntFeature(name=key, extractor=extractor)
        elif dtypes[key] == np.dtype("O"):
            component = CategoricFeature(name=key, extractor=extractor)
        else:
            raise ValueError(f"dtype {dtypes[key]} not supported.")

        components.append(component)

    return components


# Helper functions # TODO: move somewhere
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


def normalize(d):
    total = sum(d.values())
    return {k: v / total for k, v in d.items()}


def sample_counts(domain_freq, keys, n=1000):
    domain = sorted(list(keys))
    # Le's be absolutely sure the domain is always in the same order
    p = [domain_freq[k] for k in domain]
    counts = (np.array(p) * (n - len(domain))).astype("int")
    counts += 1  # make sure there are no zeros
    return counts


def sample_cdf(percentiles, n_samples, dtype="float"):
    percentiles = np.array(percentiles)
    # Sample floats in range 0 - len(percentiles)
    samples = np.random.random(n_samples) * 100

    # We will lineraly interpolate the sample between the percentiles, so get their integer floor and ceil percentile, and the relative diztance from the floor (between 0 and 1)
    floor_percentiles = np.floor(samples).astype("int")
    ceil_percentiles = np.ceil(samples).astype("int")
    percentiles_alpha = samples - np.floor(samples)

    px = percentiles[floor_percentiles] * (1 - percentiles_alpha) + percentiles[ceil_percentiles] * (percentiles_alpha)

    if dtype == "int":
        return px.astype(np.int)
    else:
        return px


def get_histogram(percentiles, dtype="float"):
    px = sample_cdf(percentiles=percentiles, n_samples=1000, dtype=dtype)
    hist, edges = np.histogram(px, bins=100, range=(percentiles[0], percentiles[-1]))
    hist = hist / hist.sum() * 100
    widths = np.diff(edges)
    bin_centers = (edges[:-1] + edges[1:]) / 2

    return go.Bar(x=bin_centers, y=hist, width=widths, name="histogram")


def get_cdf(percentiles):
    return go.Scatter(x=percentiles, y=list(range(len(percentiles))), name="cdf")
