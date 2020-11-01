#%%
%load_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np
from pathlib import Path

from rdv.schema import Schema
from rdv.component import construct_components

#%%

DATA_PATH = Path("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv")
all_data = pd.read_csv(DATA_PATH).drop("Id", axis='columns')
all_data
#%%

components = construct_components(all_data.dtypes)
schema = Schema(components=components)
schema.configure(data=all_data)
schema.compile(data=all_data)
schema.save("houses-cheap-compiled.json")

#%%
import json
sample = all_data.iloc[0, :]
with open("houses-cheap-compiled.json", 'r') as f:
    schema = Schema.from_json(json.load(f))

tags = schema.check(sample)
tags
# %%
with open("tags.json", 'w') as f:
    json.dump(tags, f, indent=4)
# %%
ray.log(tags)
