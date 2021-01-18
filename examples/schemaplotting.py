#%%
import pandas as pd
from rdv.schema import Schema
from rdv.feature import construct_features

# Load some data
cheap_data = pd.read_csv("./data_sample/subset-cheap.csv").drop("Id", axis="columns")
# Build a schema
schema = Schema(name="cheap-houses", features=construct_features(cheap_data.dtypes))
schema.build(data=cheap_data)
# Save it
schema.save("schema-cheap.json")

#%%
schema.check(cheap_data.iloc[0, :])

#%%
schema.view(mode="external")

#%%
schema.view(poi=cheap_data.iloc[0, :], mode="external")


#%%
exp_data = pd.read_csv("./data_sample/subset-exp.csv").drop("Id", axis="columns")
schema_exp = Schema(name="exp-houses", features=construct_features(exp_data.dtypes))
schema_exp.build(data=exp_data)

schema.compare(schema_exp, mode="external")


#%%


import pandas as pd
from rdv.schema import Schema
from rdv.feature import construct_features

cheap_data = pd.read_csv("./data_sample/subset-cheap.csv").drop("Id", axis="columns")
exp_data = pd.read_csv("./data_sample/subset-exp.csv").drop("Id", axis="columns")


def build_schema(data, name):
    features = construct_features(data.dtypes)
    schema = Schema(name=name, features=features)
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
