#%%
import pytest

import pandas as pd
import numpy as np

import rdv
from rdv.extractors.structured import construct_features
from rdv.feature import CategoricFeature, FloatFeature, IntFeature
from rdv.schema import Schema
from rdv.globals import SchemaStateException, DataException
from rdv.stats import NumericStats, CategoricStats

#%%
def test_constuct_components():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = construct_features(dtypes=df.dtypes)
    assert len(components) == 4
    assert isinstance(components[0], IntFeature)
    assert isinstance(components[1], CategoricFeature)
    assert isinstance(components[2], CategoricFeature)
    assert isinstance(components[3], FloatFeature)


def test_conmpile():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_features(dtypes=df.dtypes)
    schema = Schema(features=components)
    assert not schema.is_built()
    schema.build(data=df)
    components = schema.features
    assert isinstance(components["num1"].stats, NumericStats)
    assert components["num1"].stats.min == 0
    assert components["num1"].stats.max == 9
    assert components["num1"].stats.mean == 4.5
    assert components["num1"].is_built()

    assert isinstance(components["cat1"].stats, CategoricStats)
    assert sorted(components["cat1"].stats.domain_counts.keys()) == sorted(["a", "b"])
    assert components["cat1"].stats.pinv == 0
    assert components["cat1"].is_built()

    assert schema.is_built()


def test_all_nan():
    cols = {
        "num1": [np.nan] * 10,
        "cat1": [np.nan] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = construct_features(dtypes=df.dtypes)
    schema = Schema(features=components)
    try:
        schema.build(data=df)
    except ValueError:
        pass
    else:
        pytest.fail("Feature with all nans should throw a DataException")


# %%
