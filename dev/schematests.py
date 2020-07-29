#%%
%load_ext autoreload
%autoreload 2
from pathlib import Path
from PIL import Image, ImageDraw

DATA_PATH = Path("/Users/kv/stack/Startup/Raymon/Data/casting_data/train/def_front/")
LIM = 10


# TODO: Parameters here are only x,y, w, h. Compilation will then take the avg vhash. No need to save this to staging?
staging = []


def load_data(dpath, lim):
    print("Func execution")
    files = dpath.glob('*.jpeg')
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        images.append(img)
    return images

loaded_images = load_data(DATA_PATH, LIM)
active_img_idx = 0
active_img = loaded_images[active_img_idx].copy()
img_size = active_img.size

active_img




# %%
import imagehash

ahash = imagehash.average_hash(active_img)


# %%
from rdv import similarity as sim

child = sim.FixedSubpatchSimilarity()
child.is_compiled()

# %%
child = sim.FixedSubpatchSimilarity(patch=None, refs=['3'])
child.is_compiled()

# %%
