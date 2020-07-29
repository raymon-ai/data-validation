import os
import random
import sys
from pathlib import Path
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from PIL import Image, ImageDraw
import numpy as np

from dash.exceptions import PreventUpdate
from flask import request

DATA_PATH = Path("/Users/kv/stack/Startup/Raymon/Data/casting_data/train/ok_front/")
LIM = 50
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    },
    'hidden': {
        'display': 'none'
    }
}


def load_data(dpath, lim):
    files = dpath.glob('*.jpeg')
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        images.append(img)
    return images

def default_state():
    return {
        'x0': 0,
        'y0': 0,
        'x1': 64,
        'y1': 64
    }

    
    
def create_image_fig(active_img_idx, patch, editable=True):
    active_img = loaded_images[active_img_idx].copy()
    img_width, img_height = active_img.size

    fig = go.Figure(go.Image(z=np.array(active_img)))
    fig.add_shape(
        editable=editable,
        xref="x",
        yref="y",
        layer="above",
        line={"color": "cyan"},
        opacity=0.7,
        fillcolor="cyan",
        type="rect",
        **patch
    )
    fig.update_xaxes(showgrid=False, range=(0, img_width))
    fig.update_yaxes(showgrid=False, scaleanchor='x', range=(img_height, 0))

    fig.update_layout(
        autosize=False,
        width=800,
        height=800,)
    return fig



def render_patch_page(active_img_idx, state):
    patch_loc, patch_shape = format_state(state)
    return html.Div([
        html.Div([
            html.H5('Global controls'),
            html.Label("Select the image to view:"),
            dcc.Input(
                id="img-selector", type="number", value=0,
                min=0, max=len(loaded_images)-1, step=1,
            ),
            html.Label("Patch Location:"),
            html.Pre(json.dumps(state, indent=4), id="raymon-state", style=styles['pre']),
            html.Label("Patch Shape:"),
            html.Pre(str(patch_shape), id="patch-shape", style=styles['pre']),
            html.Button("Continue", id="patch-setup-complete", n_clicks=0)

        ], className="three columns", id="left-column-div"),
        html.Div([
            html.H5('Example'),
            dcc.Graph(id='graph-image',
                      figure=create_image_fig(active_img_idx, patch=state),
                      ),
        ], className="nine columns"),
    ], className="row")


def format_state(state):
    if state is None:
        raise PreventUpdate()
    x0, y0 = state['x0'], state['y0']
    x1, y1 = state['x1'], state['y1']

    patch_shape = x1 - x0, y1 - y0
    patch_loc = x0, y0
    return patch_loc, patch_shape


def register_callbacks(app):

    @app.callback(
        Output('page-body', 'children'),
        [Input('patch-setup-complete', 'n_clicks')],
        [State('raymon-state', 'children')]
    )
    def shutdown(n_clicks, state):
        if n_clicks == 0:
            raise PreventUpdate()
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        # func()
        print(f"State: \n{state}", flush=True)
        return "Setup complete."
    
    @app.callback(
        [Output(component_id="raymon-state", component_property='children'),
        Output(component_id="patch-shape", component_property='children')],
        [Input(component_id="graph-image", component_property="relayoutData")]
    )
    def update_patch_data(shape_data):
        if shape_data is None or not 'shapes[0].x0' in shape_data:
            raise PreventUpdate()

        keys = ['x0', 'y0', 'x1', 'y1']
        data = {key: int(shape_data[f"shapes[0].{key}"]) for key in keys}
        patch_width = int(data['x1'] - data['x0'])
        patch_height = int(data['y1'] - data['y0'])
        
        return f"{json.dumps(data, indent=4)}", str((patch_width, patch_height))
    

    @app.callback(
        Output(component_id="graph-image", component_property='figure'),
        [Input(component_id="img-selector", component_property="value")],
        [State('raymon-state', 'children')]
    )
    def swap_img(active_image_idx, state):
        if state is None:
            raise PreventUpdate()
        if isinstance(state, str):
            state = json.loads(state)
        active_image_idx = int(active_image_idx)

        return create_image_fig(active_img_idx=active_image_idx,
                                patch=state)

    

if __name__ == '__main__':

    loaded_images = load_data(DATA_PATH, LIM)
    active_img_idx = 0
    default_shape = 64, 64
    default_location = 0, 0

    app = dash.Dash("Data Schema Config", external_stylesheets=external_stylesheets)
    register_callbacks(app)

    app.layout = html.Div([
        html.H2("Configuring Extractor"),
        html.Div(render_patch_page(active_img_idx=active_img_idx,
                                   state=default_state())),
    ], id="page-body")

    app.run_server(debug=True)
