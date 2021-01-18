#%%
from PIL import Image
from PIL import ImageFile

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.feature import FloatFeature, NumericStats
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


loaded_data = load_data(dpath=DATA_PATH, lim=LIM)

# %%
def load_empty_schema():
    schema = Schema(
        name="Testing",
        version="1.0.0",
        features=[
            FloatFeature(name="patch_similarity", extractor=FixedSubpatchSimilarity(patch=[93, 65, 232, 221])),
            FloatFeature(name="sharpness", extractor=Sharpness()),
            FloatFeature(name="intensity", extractor=AvgIntensity()),
        ],
    )
    return schema


schema = load_empty_schema()
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

# %%
