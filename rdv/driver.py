import streamlit as st
from pathlib import Path
from PIL import Image, ImageDraw

DATA_PATH = Path("/Users/kv/stack/Startup/Raymon/Data/casting_data/train/def_front/")
LIM = 10


# TODO: Parameters here are only x,y, w, h. Compilation will then take the avg vhash. No need to save this to staging?
staging = []
def clear_staging():
    staging = []
    
f"{len(staging)} elements in staging"

@st.cache(persist=True)
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


st.sidebar.header("Testing")

loaded_images = load_data(DATA_PATH, LIM)
st.write("Active Image: ")
active_img_idx = st.sidebar.number_input(label="Image index", min_value=0, max_value=len(loaded_images)-1, value=0, step=None, format="%d")
active_img = loaded_images[active_img_idx].copy()
img_size = active_img.size
"Image dimensions: ", img_size
# img = st.image(active_img)
config_complete = st.sidebar.button("Config Complete")

if not config_complete:
    x0 = st.sidebar.slider(label="Mask x0", min_value=0, max_value=img_size[0], value=0, step=1, format="%d", key=None)
    y0 = st.sidebar.slider(label="Mask y0", min_value=0, max_value=img_size[0], value=0, step=1, format="%d", key=None)
    sizex = st.sidebar.slider(label="Mask width", min_value=0,
                            max_value=img_size[0], v alue=64, step=1, format="%d", key=None)
    sizey = st.sidebar.slider(label="Mask height", min_value=0,
                            max_value=img_size[0], value=64, step=1, format="%d", key=None)

else:
    st.sidebar.subheader("Add or remove sample from staging")
    add_button = st.sidebar.button(label="Add")
    rm_button = st.sidebar.button(label="Remove")
    if add_button:
        st.write("Save here")
    img = None

    if rm_button:
        st.write("Remove here")


x1 = x0+sizex
y1 = y0+sizey



draw = ImageDraw.Draw(active_img)
draw.rectangle(xy=[x0, y0, x1, y1], fill=None, outline=(0, 255, 0), width=1)
img = st.image(active_img, use_column_width=True)



"""
# Instructions:
1. First, go through you image samples and configure the mask for you feature extractor. 
2. Lock the config using the lock button
3. Go thorugh you images again and select the ones you want to use for the feature extractor compilation
"""
