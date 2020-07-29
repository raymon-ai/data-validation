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
        'overflowWrap': 'break-word'
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


def default_staging(loaded_images):
    return set(range(len(loaded_images)))


def create_image_fig(active_img_idx, patch):
    active_img = loaded_images[active_img_idx].copy()
    img_width, img_height = active_img.size

    fig = go.Figure(go.Image(z=np.array(active_img)))
    fig.add_shape(
        editable=False,
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


def add_rm_button(active_image_idx, staging):
    if active_image_idx in staging:
        msg = "Img is in staging"
        but = "Remove"
    else:
        msg = "Img is NOT in staging"
        but = "Add"
    layout = html.Div([
        html.Label(msg),
        html.Button(but, id="add-rm-button", n_clicks=0)
    ], className="row")
    return layout


def render_staging_page(loaded_images, active_img_idx, staging, patch):
    # staging = parse_state(staging)
    return html.Div([
        html.H2("Configuring Compilation Context for ..."),
        html.Div([
            html.Div([
                html.H5('Global controls'),
                html.Label("Select the image to view:"),
                dcc.Input(
                    id="img-selector", type="number", value=active_img_idx,
                    min=0, max=len(loaded_images)-1, step=1,
                ),
                html.Div(add_rm_button(active_img_idx, staging), id='add-rm-div'),
                html.Label("Staging:"),
                dcc.Markdown(str(staging), id="raymon-state"),
                html.Button("Continue", id="setup-complete", n_clicks=0)

            ], className="three columns", id="left-column-div"),
            html.Div([
                html.H5('Example'),
                dcc.Graph(id='graph-image',
                          figure=create_image_fig(active_img_idx, patch=patch),
                          ),
            ], className="nine columns"),
            html.Div(children=json.dumps(patch), id="patch-state", style=styles['hidden'])
        ], className="row")])


def parse_state(state):
    if state is None:
        raise PreventUpdate()
    state = eval(state)
    return state


def register_callbacks(app):

    @app.callback(
        Output('outerdiv', 'children'),
        [Input('setup-complete', 'n_clicks')],
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
        [Output('raymon-state', 'children'),
         Output("add-rm-div", 'children')],
        [Input('add-rm-button', 'n_clicks'),
         Input("img-selector", "value"), ],
        [State('raymon-state', 'children')]
    )
    def addrm(n_clicks, active_img_idx, staging):
        staging = eval(staging)
        if n_clicks == 0:
            raise PreventUpdate()
        if active_img_idx in staging:
            staging.remove(active_img_idx)
        else:
            staging.add(active_img_idx)
        return str(staging), add_rm_button(active_img_idx, staging)

    @app.callback(
        Output(component_id="page-body", component_property='children'),
        [Input(component_id="img-selector", component_property="value")],
        [State('patch-state', 'children'),
         State('raymon-state', 'children')]
    )
    def swap_img(active_image_idx, patch, staging):
        if patch is None:
            raise PreventUpdate()
        if isinstance(patch, str):
            print(f"Patch: {patch}, {type(patch)}")
            patch = json.loads(patch)
        active_image_idx = int(active_image_idx)

        return render_staging_page(loaded_images=loaded_images,
                                   active_img_idx=active_image_idx,
                                   staging=eval(staging),
                                   patch=patch)

    # create_image_fig(active_img_idx=active_image_idx,
    #                             patch=patch)


def configure(app, loaded_images, patch):
    register_callbacks(app)

    app.layout = html.Div(
        html.Div(render_staging_page(loaded_images=loaded_images,
                                     active_img_idx=0,
                                     staging=default_staging(loaded_images),
                                     patch=patch), id="page-body"),
        id="outerdiv")


if __name__ == '__main__':

    loaded_images = load_data(DATA_PATH, LIM)
    patch = {
        "x0": 0,
        "y0": 0,
        "x1": 128,
        "y1": 128
    }
    app = dash.Dash("Data Schema Config", external_stylesheets=external_stylesheets)

    configure(app=app, loaded_images=loaded_images, patch=patch)

    app.run_server(debug=True)
