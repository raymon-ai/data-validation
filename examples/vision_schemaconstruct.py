#%%
%load_ext autoreload
%autoreload 2

from PIL import Image
from PIL import ImageFile

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.component import NumericComponent, NumericStats
from rdv.extractors.vision import FixedSubpatchSimilarity
from rdv.extractors.vision import AvgIntensity
from rdv.extractors.vision import Sharpness
from PIL import ImageFilter


ImageFile.LOAD_TRUNCATED_IMAGES = True

DATA_PATH = Path("/Users/kv/Raymon/Data/casting_data/train/ok_front/")
LIM = 150


def load_data(dpath, lim):
    files = dpath.glob('*.jpeg')
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        images.append(img)
    return images

#%%
extractor = FixedSubpatchSimilarity()
sim_component = NumericComponent(extractor=extractor)
components = [
    sim_component,
]
schema = Schema(components=components)
schema.save('./schema.json')


# %%
schema = Schema()
schema.load('./schema.json')
schema

# %%
def load_full_schema():
    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=["ae81b596d698da31"])
    stats = NumericStats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, hist=[10, 10])
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = Schema(name="Testing", version='1.0.0', components=[component, component])
    return schema

def load_empty_schema():
    schema=Schema(name="Testing", version='1.0.0', components=[
        NumericComponent(name="testcomponent", 
                         extractor=FixedSubpatchSimilarity()
                         ),

    ])
    return schema

#%% 
schema = load_empty_schema()
loaded_data = load_data(dpath=DATA_PATH, lim=LIM)
schema.configure(data=loaded_data)
# %%
schema.compile(data=load_data(dpath=DATA_PATH, lim=1000))
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
img_dark = Image.fromarray((np.array(img_dark) - np.array(img_dark)*0.3).astype(np.uint8))
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
