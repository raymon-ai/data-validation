#%%
%load_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.component import NumericComponent, CategoricComponent, NumericStats, CategoricStats
from rdv.extractors.structured import ElementExtractor
pd.set_option('display.max_rows', 500)


DATA_PATH = Path("/Users/kv/Raymon/Code/rdv/dev/subset-cheap.csv")

all_data = pd.read_csv(DATA_PATH).drop("Id", axis='columns')
row = all_data.iloc[0, :]
row

#%%
def construct_components(dtypes):
    components = []
    for key in dtypes.index:
        # Check type: Numeric or categoric
        extractor = ElementExtractor(element=key)
        if dtypes[key] == np.dtype('O'):
            component = CategoricComponent(name=key, extractor=extractor) 
        else:
            component = NumericComponent(name=key, extractor=extractor)
        components.append(component)
    return components

components = construct_components(all_data.dtypes)
schema = Schema(components=components)
schema.save("houses-cheap-empty.json")


# %%
schema.configure(data=all_data)
schema.save("houses-cheap-configured.json")

#%%
schema.compile(data=all_data)
schema.save("houses-cheap-compiled.json")
# %%

fullschema_path = "schema-compiled.json"
schema.save(fullschema_path)

# %%
schema = Schema().load(fullschema_path)
tags = schema.check(loaded_data[-1])
tags
# %%
str(tags[0])


# %%


def load_configured_schema():
    schema = Schema(name="Testing", version='1.0.0', components=[
        NumericComponent(name="patch_similarity",
                         extractor=FixedSubpatchSimilarity(
                             patch={'x0': 0, 'y0': 0, 'x1': 64, 'y1': 64},
                             refs=["adf8d224cb8786cc"], nrefs=1)
                         ),
        NumericComponent(name="sharpness", extractor=Sharpness()),
        NumericComponent(name='intensity', extractor=AvgIntensity())

    ])
    return schema
#%%


loaded_data = load_data(dpath=DATA_PATH, lim=LIM)
schema = load_configured_schema()
schema.configure(data=loaded_data)
schema.compile(data=load_data(dpath=DATA_PATH, lim=1000))

# %%
schema.save('schema-extended.json')
# %%

img_blur = loaded_data[-10].copy().filter(ImageFilter.GaussianBlur(radius=5))
img_blur
#%%
schema.check(img_blur)

# %%
import numpy as np
img_dark = loaded_data[-20].copy()
img_dark = Image.fromarray((np.array(img_dark) - np.array(img_dark) * 0.3).astype(np.uint8))
img_dark

schema.check(img_dark)

# %%
loaded_data[-20]


# %%
# Tutorial

# Construct schema
schema = Schema(
    name="Testing", version='1.0.0',
    components=[
        NumericComponent(name="patch_similarity",
                            extractor=FixedSubpatchSimilarity()),
        NumericComponent(name="sharpness", extractor=Sharpness()),
        NumericComponent(name='intensity', extractor=AvgIntensity())
    ])
# Start interactive configuration wizard
schema.configure(data=loaded_data[:1000])
# Compile stats
schema.compile(data=loaded_data[1000:])
# Check a data sample
tags = schema.check(img)


# %%
class Deployment:

    def process(self, data):
        ray = Ray(logger=self.raymon)
        ray.tag({
            'machine': 'casting_5'
        })
        ray.log(peephole='network_input_img',
                data=rt.ImageGrayscale(np.squeeze(data.numpy())))

        output = other_processing(data, ray=ray)
        return output
