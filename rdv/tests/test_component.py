#%%
import pytest

import pandas as pd
import numpy as np

import rdv
from rdv.component import construct_components
from rdv.component import CategoricComponent, NumericComponent
from rdv.schema import Schema
from rdv.globals import SchemaBuildingException, DataException
from rdv.stats import NumericStats, CategoricStats

#%%
def test_constuct_components():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": list(range(0, 20, 2)),
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    assert len(components) == 4
    assert isinstance(components[0], NumericComponent)
    assert isinstance(components[1], CategoricComponent)
    assert isinstance(components[2], CategoricComponent)
    assert isinstance(components[3], NumericComponent)


def test_compile_unconfigured_numeric():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": list(range(0, 20, 2)),
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(components=components)
    try:
        schema.compile(data=df)
    except SchemaBuildingException:
        pass
    else:
        pytest.fail("Compilation of unconfigured schema should fail")


def test_configure():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(components=components)
    schema.configure(data=df)
    components = schema.components
    assert isinstance(components[0].stats, NumericStats)
    assert components[0].stats.min == 0
    assert components[0].stats.max == 9
    assert components[0].stats.mean is None
    assert components[0].is_configured()
    assert not components[0].is_compiled()

    assert isinstance(components[1].stats, CategoricStats)
    assert sorted(components[1].stats.domain) == sorted(["a", "b"])
    assert components[1].stats.pinv is None
    assert components[1].is_configured()
    assert not components[1].is_compiled()


def test_conmpile():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(components=components)
    schema.configure(data=df)
    schema.compile(data=df)
    components = schema.components
    assert isinstance(components[0].stats, NumericStats)
    assert components[0].stats.min == 0
    assert components[0].stats.max == 9
    assert components[0].stats.mean == 4.5
    assert components[0].is_configured()
    assert components[0].is_compiled()

    assert isinstance(components[1].stats, CategoricStats)
    assert sorted(components[1].stats.domain) == sorted(["a", "b"])
    assert components[1].stats.pinv == 0
    assert components[1].is_configured()
    assert components[1].is_compiled()


def test_all_nan():
    cols = {
        "num1": [np.nan] * 10,
        "cat1": [np.nan] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = construct_components(dtypes=df.dtypes)
    schema = Schema(components=components)
    try:
        schema.configure(data=df)
    except DataException:
        pass
    else:
        pytest.fail("Component with all nans should throw a DataException")


# %%
