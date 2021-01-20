import pytest

import pandas as pd
import numpy as np

import rdv
from rdv.extractors.structured import construct_features
from rdv.feature import CategoricFeature, FloatFeature
from rdv.schema import Schema
from rdv.globals import SchemaStateException, DataException
from rdv.stats import NumericStats, CategoricStats


def test_compile_nan():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_features(dtypes=df.dtypes)
    schema = Schema(features=components)
    schema.build(data=df)

    tags = schema.check(pd.Series([np.nan, np.nan], index=["num1", "cat1"]))
    assert len(tags) == 2
    for tag in tags:
        assert tag["type"] == "schema-error"
        assert tag["value"] == "Value NaN"


def test_compile_nan_2():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_features(dtypes=df.dtypes)
    schema = Schema(features=components)
    schema.build(data=df)
    components = schema.features

    tags = schema.check(pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2

    assert tags[0]["type"] == "schema-feature"
    assert tags[0]["name"] == "num1"
    assert tags[0]["value"] == 1
    assert tags[0]["group"] == "default@0.0.0"

    assert tags[1]["type"] == "schema-feature"
    assert tags[1]["name"] == "cat1"
    assert tags[1]["value"] == "b"
    assert tags[1]["group"] == "default@0.0.0"
