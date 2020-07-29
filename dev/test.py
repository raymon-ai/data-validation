import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

import mymod

DATE_TIME = "date/time"
DATA_URL = (
    "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

st.title("Uber Pickups in New York City")
st.markdown(
    """
This is a demo of a Streamlit app that shows the Uber pickups
geographical distribution in New York City. Use the slider
to pick a specific hour and look at how the charts change.
[See source code](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py)
""")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data


data = load_data(100000)
"Raw Data: "
data


mymod.add_colorpicker(st)

clr = st.beta_color_picker(label="Colorpicker2")
color = st.beta_color_picker('Pick A Color', '#00f900')
st.write('The current color is', color)
