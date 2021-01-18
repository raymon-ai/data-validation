#%%
import pandas as pd
import numpy as np

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.feature import construct_features

DATA_PATH = Path("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv")
all_data = pd.read_csv(DATA_PATH).drop("Id", axis="columns")
row = all_data.iloc[0, :]
row

#%%

features = construct_features(all_data.dtypes)
schema = Schema(features=features)
schema.build(data=all_data)
schema.save("houses-cheap-built.json")

#%%


#%%
row = all_data.iloc[-1, :]
tags = schema.check(row)
tags
# %%

# %%
# schema.view()

#%%
schema.view(poi=row)
#%%
