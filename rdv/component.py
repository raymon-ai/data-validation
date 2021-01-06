from collections.abc import Iterable
from pydoc import locate
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from rdv.globals import (
    Buildable,
    ClassNotFoundError,
    Configurable,
    NotSupportedException,
    Serializable,
)
from rdv.stats import CategoricStats, NumericStats
from rdv.tags import Tag, SEG, ERR, IND
from rdv.extractors.structured import ElementExtractor
from rdv.extractors import NoneExtractor


class Component(Serializable, Buildable, ABC):
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
            raise NotSupportedException("loaded_data should be a DataFrame or Iterable")
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


class NumericComponent(Component):
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
            raise NotSupportedException(
                f"stats for a NumericComponant should be of type NumericStats, not {type(value)}"
            )

    def feature2tag(self, feature):
        if not np.isnan(feature):
            return Tag(name=self.name, value=float(feature), type=IND)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=ERR)
        elif np.isnan(feature):
            return Tag(name=tagname, value="Value NaN", type=ERR)
        elif feature > self.stats.max:
            return Tag(name=tagname, value="Value > max", type=ERR)
        elif feature < self.stats.min:
            return Tag(name=tagname, value="Value < min", type=ERR)
        else:
            return None

    def load_jcr(self, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            raise ClassNotFoundError(f"Could not locate {classpath}")

        self.extractor = extr_class().load_jcr(jcr["extractor_state"])
        self.stats = NumericStats().load_jcr(jcr["stats"])
        self.name = jcr["name"]
        return self


class CategoricComponent(Component):

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
            raise NotSupportedException(
                f"stats for a NumericComponant should be of type CategoricStats, not {type(value)}"
            )

    def feature2tag(self, feature):
        return Tag(name=self.name, value=feature, type=SEG)

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=ERR)
        elif pd.isnull(feature):
            return Tag(name=tagname, value="Value NaN", type=ERR)
        elif feature not in self.stats.domain_counts:
            return Tag(name=tagname, value="Domain Error", type=ERR)
        else:
            return None

    def load_jcr(self, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            raise ClassNotFoundError(f"Could not locate {classpath}")

        self.extractor = extr_class().load_jcr(jcr["extractor_state"])
        self.stats = CategoricStats().load_jcr(jcr["stats"])
        self.name = jcr["name"]
        return self


def construct_components(dtypes):
    components = []
    for key in dtypes.index:
        # Check type: Numeric or categoric
        extractor = ElementExtractor(element=key)
        if dtypes[key] == np.dtype("O"):
            component = CategoricComponent(name=key, extractor=extractor)
        else:
            component = NumericComponent(name=key, extractor=extractor)
        components.append(component)
    return components
