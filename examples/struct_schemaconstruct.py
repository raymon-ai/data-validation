#%%
%load_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.component import NumericComponent, CategoricComponent, NumericStats, CategoricStats, construct_components
from rdv.extractors.structured import ElementExtractor
pd.set_option('display.max_rows', 500)


DATA_PATH = Path("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv")

all_data = pd.read_csv(DATA_PATH).drop("Id", axis='columns')
row = all_data.iloc[0, :]
row

#%%
def print_status(scehma):
    print(f"Schema configured? {schema.is_configured()}")
    print(f"Schema compiled? {schema.is_compiled()}")



components = construct_components(all_data.dtypes)
schema = Schema(components=components)
schema.save("houses-cheap-empty.json")
print_status(schema)


# %%
schema.configure(data=all_data)
schema.save("houses-cheap-configured.json")
print_status(schema)

#%%
schema.compile(data=all_data)
schema.save("houses-cheap-compiled.json")
print_status(schema)

#%%
row = all_data.iloc[-1, :]
tags = schema.check(row)
tags
# %%

