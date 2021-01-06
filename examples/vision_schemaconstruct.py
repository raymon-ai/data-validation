#%%
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


#%%


def load_data(dpath, lim):
    files = dpath.glob("*.jpeg")
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        images.append(img)
    return images


# %%
def load_full_schema():
    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=["ae81b596d698da31"])
    stats = NumericStats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, hist=[10, 10])
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = Schema(name="Testing", version="1.0.0", components=[component, component])
    return schema


def load_empty_schema():
    schema = Schema(
        name="Testing",
        version="1.0.0",
        components=[
            NumericComponent(name="patch_similarity", extractor=FixedSubpatchSimilarity()),
            NumericComponent(name="sharpness", extractor=Sharpness()),
            NumericComponent(name="intensity", extractor=AvgIntensity()),
        ],
    )
    return schema


#%%
schema = load_empty_schema()
loaded_data = load_data(dpath=DATA_PATH, lim=LIM)
schema.configure(data=loaded_data)
# %%
schema.build(data=load_data(dpath=DATA_PATH, lim=1000))
# %%
fullschema_path = "schema-compiled.json"
schema.save(fullschema_path)

# %%
schema = Schema().load(fullschema_path)
tags = schema.check(loaded_data[-1])
tags

# %%

img_blur = loaded_data[-10].copy().filter(ImageFilter.GaussianBlur(radius=5))
img_blur
#%%
tags = schema.check(img_blur)
tags
# %%
import numpy as np

img_dark = loaded_data[-20].copy()
img_dark = Image.fromarray((np.array(img_dark) - np.array(img_dark) * 0.3).astype(np.uint8))
img_dark

tags = schema.check(img_dark)
tags


#%%
nc = NumericComponent(name="patch_similarity", extractor=FixedSubpatchSimilarity())
# %%
nc.extractor.configure(data=loaded_data)
# %%
