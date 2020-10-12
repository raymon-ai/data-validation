#%%
%load_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np
from pathlib import Path

from rdv.schema import Schema
from rdv.component import construct_components


DATA_PATH = Path("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv")
all_data = pd.read_csv(DATA_PATH).drop("Id", axis='columns')

components = construct_components(all_data.dtypes)
schema = Schema(components=components)
schema.configure(data=all_data)
schema.compile(data=all_data)
schema.save("houses-cheap-compiled.json")

#%%
tags = schema.check(row)
ray.log(tags)
tags
# %%

tags[0].to_jcr()
# %%
ray.log(tags)
