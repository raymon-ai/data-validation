import json
import tempfile
import time
import webbrowser
from collections.abc import Iterable
from enum import Enum
from multiprocessing import Process
from pydoc import locate

import numpy as np
import pandas as pd

from rdv.globals import (CCAble, ClassNotFoundError, NoneExtractor,
                         NotSupportedException, Serializable)
from rdv.stats import CategoricStats, NumericStats


class TagType(Enum):
    SEGM = 0
    IND = 1
    ERROR = 2


class Tag(Serializable):
    def __init__(self, name, value, tagtype, msg=None):
        self.name = name
        self.value = value
        self.tagtype = tagtype
        self.msg = msg

    def to_jcr(self):
        jcr = {
            'tagtype': self.tagtype,
            'name': self.name,
            'value': self.value,
            'msg': self.msg
        }
        return jcr

    def load_jcr(self, jcr):
        self.__init__(**jcr)
        return self

    def __str__(self):
        return f"'{self.name}:{self.value}"

    def __repr__(self):
        return f"Tag(name='{self.name}, value={self.value}, tagtype={self.tagtype}, msg={self.msg}"


class Component(Serializable, CCAble):

    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = ['extractor', 'stats']
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, name="default_name", extractor=None):
        self.name = str(name)
        if extractor is None:
            self.extractor = NoneExtractor()
        else:
            self.extractor = extractor
        self.stats = None

    def to_jcr(self):
        data = {
            'name': self.name,
            'extractor_class': self.class2str(self.extractor),
            'extractor_state': self.extractor.to_jcr(),
            'stats': self.stats.to_jcr(),
        }
        return data

    def configure_extractor(self, loaded_data):
        if hasattr(self.extractor, 'configure_interactive'):
            print(f"Configure extractor for {self.name}")
            loaded = self.interact_config(loaded_data)
            self.extractor.configure(loaded)
        else:
            print(f"No configuration interaction available for {self.name}")
            self.extractor.configure(loaded_data)

    def interact_config(self, loaded_data):
        _, output_fpath = tempfile.mkstemp()
        print(f"Saving to: {output_fpath}")
        # Crease new process
        p = Process(target=self.extractor.configure_interactive, args=(loaded_data, output_fpath))
        p.start()
        time.sleep(0.5)
        webbrowser.open_new('http://127.0.0.1:8050/')
        p.join()
        # Load saved config and save to extractor
        with open(output_fpath, 'r') as f:
            loaded = json.load(f)
        return loaded

    def compile_extractor(self, loaded_data):
        self.extractor.compile(loaded_data)

    def configure_stats(self, loaded_data):
        print(f"Configuring {self.name}")
        features = self.extract_features(loaded_data)
        self.stats.configure(features)

    def compile_stats(self, loaded_data):
        print(f"Compiling {self.name}")
        features = self.extract_features(loaded_data)
        self.stats.compile(features)

    def extract_features(self, loaded_data):
        features = []
        if isinstance(loaded_data, pd.DataFrame):
            features = self.extractor.extract_feature(loaded_data)
        elif isinstance(loaded_data, Iterable):
            for data in loaded_data:
                features.append(self.extractor.extract_feature(data))
        else:
            raise NotSupportedException("loaded_data should be a DataFrame of Iterable")
        return features

    def configure(self, data):
        # Configure extractor
        self.configure_extractor(data)
        # Compile extractor
        self.compile_extractor(data)
        # Configure stats
        self.configure_stats(data)

    def compile(self, data):
        self.compile_stats(data)


class NumericComponent(Component):

    def __init__(self, name="default_name", extractor=None, stats=None):
        super().__init__(name=name, extractor=extractor)
        # TODO: make stats a property and check type before setting!
        if stats is None:
            self.stats = NumericStats()
        else:
            self.stats = stats

    def check(self, data):
        feature = self.extractor.extract_feature(data)
        # Check min, max, nan or None and raise data error
        tag = self.check_invalid(feature)
        # If all pass, calc z score
        if tag is None:
            zscore = (feature - self.stats.mean) / self.stats.std
            tag = Tag(name=self.name, value=zscore, tagtype=TagType.IND, msg="Valid Sample with given zscore")
        return tag

    def check_invalid(self, feature):
        if feature is None:
            return Tag(name=self.name, value='invalid', tagtype=TagType.ERROR, msg="Value is None")
        elif np.isnan(feature):
            return Tag(name=self.name, value='invalid', tagtype=TagType.ERROR, msg="Value is NaN")
        elif feature > self.stats.max:
            return Tag(name=self.name, value='invalid', tagtype=TagType.ERROR, msg=f"Value {feature} above schema max")
        elif feature < self.stats.min:
            return Tag(name=self.name, value='invalid', tagtype=TagType.ERROR, msg=f"Value {feature} below schema min")
        else:
            return None

    def load_jcr(self, jcr):
        classpath = jcr['extractor_class']
        extr_class = locate(classpath)
        if extr_class is None:
            raise ClassNotFoundError(f"Could not locate {classpath}")

        self.extractor = extr_class().load_jcr(jcr['extractor_state'])
        self.stats = NumericStats().load_jcr(jcr['stats'])
        self.name = jcr['name']
        return self


class CategoricComponent(Component):

    # Domain, domain distribution
    def __init__(self, name="default_name", extractor=None, stats=None):
        super().__init__(name=name, extractor=extractor)
        if stats is None:
            self.stats = CategoricStats()
        else:
            self.stats = stats

    def check(self, data):
        feature = self.extractor.extract_feature(data)
        # Check min, max, nan or None and raise data error
        tag = self.check_invalid(feature)
        # If all pass, calc z score
        raise NotImplementedError
        if tag is None:
            zscore = (feature - self.stats.mean) / self.stats.std
            tag = Tag(name=self.name, value=zscore, tagtype=TagType.IND, msg="Valid Sample with given zscore")
        return tag

    def check_invalid(self, feature):
        raise NotImplementedError

    def load_jcr(self, jcr):
        classpath = jcr['extractor_class']
        extr_class = locate(classpath)
        if extr_class is None:
            raise ClassNotFoundError(f"Could not locate {classpath}")

        self.extractor = extr_class().load_jcr(jcr['extractor_state'])
        self.stats = CategoricStats().load_jcr(jcr['stats'])
        self.name = jcr['name']
        return self
