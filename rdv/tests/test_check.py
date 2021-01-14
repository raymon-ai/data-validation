import pytest

import pandas as pd
import numpy as np

import rdv
from rdv.feature import construct_components
from rdv.feature import CategoricFeature, FloatFeature
from rdv.schema import Schema
from rdv.globals import SchemaStateException, DataException
from rdv.stats import NumericStats, CategoricStats


def test_conmpile_nan():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(features=components)
    schema.configure(data=df)
    schema.compile(data=df)
    components = schema.components

    tags = schema.check(pd.Series([np.nan, np.nan], index=["num1", "cat1"]))
    assert len(tags) == 2
    for tag in tags:
        assert tag["type"] == "err"
        assert tag["value"] == "Value NaN"


def test_conmpile_nan():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(features=components)
    schema.configure(data=df)
    schema.compile(data=df)
    components = schema.components

    tags = schema.check(pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 4

    assert tags[0]["type"] == "ind"
    assert tags[1]["name"].endswith("-dev")
    assert tags[1]["type"] == "ind"

    assert tags[2]["type"] == "seg"
    assert tags[3]["name"].endswith("-dev")
    assert tags[3]["type"] == "ind"
