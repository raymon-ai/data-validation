import streamlit as st
from pathlib import Path
from PIL import Image, ImageDraw
import os
import sys
import random
import argparse
import streamlit as st
import st_state_patch


DATA_PATH = Path("/Users/kv/stack/Startup/Raymon/Data/casting_data/train/def_front/")
LIM = 50
state = st.State()
default_size = 64

cfg_complete_pressed = st.sidebar.empty()
print(cfg_complete_pressed)
if cfg_complete_pressed:
    state.bounds_set = True

if not state:
    # Initialize it here!
    state.bounds_set = False
    state.staging = set()


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


def draw_box(st):
    draw = ImageDraw.Draw(active_img)
    draw.rectangle(xy=state.patch, fill=None, outline=(0, 255, 0), width=1)
    st.image(active_img, use_column_width=True)

loaded_images = load_data(DATA_PATH, LIM)
active_img_idx = st.number_input(label="Image index", min_value=0,
                                         max_value=len(loaded_images)-1, value=0, step=None, format="%d")
active_img = loaded_images[active_img_idx].copy()
img_size = active_img.size


# img = st.image(active_img)

if not state.bounds_set:
    cont_text = "Done"
    st.sidebar.header("Step 1: configure location properties")
    st.sidebar.markdown = f"""
    Edit the location of the patch you want to check, then press the {cont_text} button to continue.
    """

    x0 = st.sidebar.number_input(label="Mask x0", min_value=0,
                                 max_value=img_size[0], value=0, format="%d")
    y0 = st.sidebar.number_input(label="Mask y0", min_value=0,
                                 max_value=img_size[0], value=0, format="%d")
    x1 = st.sidebar.number_input(label="Mask x1", min_value=x0,
                                 max_value=img_size[0], value=x0+default_size, format="%d")
    y1 = st.sidebar.number_input(label="Mask y1", min_value=y0,
                                 max_value=img_size[0], value=y0+default_size, format="%d")
    state.patch = [x0, y0, x1, y1]
    cfg_complete_pressed = cfg_complete_pressed.button(cont_text)
    draw_box(st)
    

else:
    st.sidebar.subheader("Step 2: Select samples for compilation")
    st.write(state.staging)

    draw_box(st)
    if active_img_idx in state.staging:
        st.write("This sample is currently in your staging area")
        rm_button = st.button(label="Remove from staging")
        if rm_button:
            state.staging.discard(active_img_idx)
    else:
        st.write("This sample is currently NOT your staging area")
        add_button = st.button(label="Add to staging")
        if add_button:
            state.staging.add(active_img_idx)
       




"Image dimensions: ", img_size

"""
# Instructions:
1. First, go through your image samples and configure the mask for you feature extractor. Lock the config using the lock button
2. Go thorugh you images again and select the ones you want to use for the feature extractor compilation
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This drives schema configuration and compilation')
    parser.add_argument('--data')
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # This exception will be raised if --help or invalid command line arguments
        # are used. Currently streamlit prevents the program from exiting normally
        # so we have to do a hard exit.
        os._exit(e.code)

    st.title("Command line example app")
    st.markdown(f"Your current command line is: {sys.argv}")
