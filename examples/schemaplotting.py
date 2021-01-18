#%%
# %load_ext autoreload
# %autoreload 2
from rdv.schema import Schema
from plotly import graph_objects as go
import dash_bootstrap_components as dbc
from flask import request

fullschema_path = "/Users/kv/Raymon/Code/rdv/examples/houses-cheap-built.json"
schema = Schema().load(fullschema_path)
#%%
# schema.view()
#%%

# %%
from rdv.feature import construct_features
import pandas as pd

cheap_data = pd.read_csv("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv").drop("Id", axis="columns")
exp_data = pd.read_csv("/Users/kv/Raymon/Code/rdv/examples/subset-exp.csv").drop("Id", axis="columns")


def build_schema(data, name):
    features = construct_features(data.dtypes)
    schema = Schema(features=features)
    schema.build(data=data)
    return schema


schema_cheap = build_schema(cheap_data, name="cheap-houses")
schema_exp = build_schema(exp_data, name="exp-houses")

#%%
# schema_cheap.view(mode="external")

# #%%
# schema_cheap.view(poi=exp_data.iloc[0, :])


# %%
schema_cheap.compare(schema_exp)

# %%
