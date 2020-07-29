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


def create_image_fig(active_img_idx, patch_loc, patch_shape, editable=True):
    active_img = loaded_images[active_img_idx].copy()
    img_width, img_height = active_img.size

    fig = go.Figure(go.Image(z=np.array(active_img)))
    fig.add_shape(
        editable=editable,
        xref="x",
        yref="y",
        layer="above",
        line={"color": "cyan"},
        #     "width": 2,
        #     "dash": "solid"
        # },
        opacity=0.7,
        fillcolor="cyan",
        type="rect",
        x0=patch_loc[0],
        y0=patch_loc[1],
        x1=patch_loc[0] + patch_shape[0],
        y1=patch_loc[0] + patch_shape[1]
    )
    fig.update_xaxes(showgrid=False, range=(0, img_width))
    fig.update_yaxes(showgrid=False, scaleanchor='x', range=(img_height, 0))

    fig.update_layout(
        autosize=False,
        width=800,
        height=800,)
    return fig


def render_staging_page(active_img_idx, patch_loc, patch_shape):
    col = [
        html.H5('Staging controls'),
        html.Label("Select the image to view:"),
        dcc.Input(
            id="img-selector-2", type="number", value=0,
            min=0, max=len(loaded_images)-1, step=1,
        ),
        html.Label("Images in staging:"),
        html.Pre(str(set(range(25))), id="staging-images"),

        html.Button("Remove", id="remove-img", n_clicks=0)

    ]
    return html.Div([
        html.Div([
            html.H5('Staging controls'),
            html.Label("Select the image to view:"),
            dcc.Input(
                id="img-selector-staging", type="number", value=0,
                min=0, max=len(loaded_images)-1, step=1,
            ),
            html.Label("Images in staging:"),
            html.Pre(str(set(range(25))), id="staging-images"),

            html.Button("Remove", id="remove-img", n_clicks=0)
            ], className="three columns", id="left-column-staging"),
        html.Div([
            html.H5('Example'),
            dcc.Graph(id='graph-image-staging',
                      figure=create_image_fig(active_img_idx, patch_loc=patch_loc,
                                              patch_shape=patch_shape, editable=False),
                    ),
        ], className="nine columns"),
    ], className="row")


def render_patch_page(active_img_idx, patch_loc, patch_shape):
    return html.Div([
        html.Div([
            html.H5('Global controls'),
            html.Label("Select the image to view:"),
            dcc.Input(
                id="img-selector", type="number", value=0,
                min=0, max=len(loaded_images)-1, step=1,
            ),
            html.Label("Patch Location:"),
            html.Pre(str(patch_loc), id="patch-loc", style=styles['pre']),
            html.Label("Patch Shape:"),
            html.Pre(str(patch_shape), id="patch-shape", style=styles['pre']),
            html.Button("Continue", id="patch-setup-complete", n_clicks=0)

        ], className="three columns", id="left-column-div"),
        html.Div([
            html.H5('Example'),
            dcc.Graph(id='graph-image',
                      figure=create_image_fig(active_img_idx, patch_loc=patch_loc,
                                              patch_shape=patch_shape),
                        ),
        ], className="nine columns"),
        ], className="row")


def parse_state(state):
    if state is None:
        raise PreventUpdate()
    state = json.loads(state)
    patch_loc = state['x0'], state['y0']
    patch_shape = state['w'], state['h']
    return patch_loc, patch_shape


def register_callbacks(app):

    # @app.callback(
    #     Output('hidden-state', 'children'),
    #     [Input('patch-setup-complete', 'n_clicks')],
    #     [State('img-selector-staging', 'value'),
    #      State(component_id="patch-loc", component_property='children'),
    #      State(component_id="patch-shape", component_property='children')]
    #     )
    # def update_output(patch_n_clicks, patch_loc, patch_shape):
    #     print(f"State: {state}")
    #     if patch_n_clicks == 0:
    #         state = json.dumps({
    #             'x0': patch_loc[0],
    #             'y0': patch_loc[1],
    #             'w': patch_shape[0],
    #             'h': patch_shape[1]
    #         })

    #         return json.dumps(state)
    #     else:
    #         json.dumps({})

    @app.callback(
        [Output(component_id="patch-loc", component_property='children'),
         Output(component_id="patch-shape", component_property='children')],
         Input(component_id="graph-image", component_property="relayoutData")
         )
    def update_patch_data(shape_data):
        if shape_data is not None and 'shapes[0].x0' in shape_data:
            x0= int(shape_data['shapes[0].x0'])
            x1= int(shape_data['shapes[0].x1'])
            y0= int(shape_data['shapes[0].y0'])
            y1= int(shape_data['shapes[0].y1'])

            patch_width= x1-x0
            patch_height= y1-y0

            return str((x0, y0)), str((patch_width, patch_height))
        else:
            dash.no_update
        return str(default_location), str(default_shape)
        # return json.dumps(input_data, indent=4)


    @app.callback(
        Output(component_id="graph-image", component_property='figure'),
        [Input(component_id="img-selector", component_property="value")],
        [State('patch-loc', 'children'),
        State('patch-shape', 'children')]
    )
    def update_fig(active_image_idx, patch_loc, patch_shape):
        if patch_loc is None:
            patch_loc= str(default_location)
        if patch_shape is None:
            patch_shape= str(default_shape)

        dash.no_update

        active_image_idx= int(active_image_idx)
        patch_loc= eval(patch_loc)
        patch_shape= eval(patch_shape)

        return create_image_fig(active_img_idx=active_image_idx,
                                patch_loc=patch_loc,
                                patch_shape=patch_shape)

    @ app.callback(
        Output(component_id="graph-image-staging", component_property='figure'),
        [Input(component_id="img-selector-staging", component_property="value")],
        [State('hidden-state', 'children')]
    )
    def update_fig_staging(active_image_idx, state):
        print(f"State: {state}")
        patch_loc, patch_shape= parse_state(state)
        return create_image_fig(active_img_idx=active_image_idx,
                                patch_loc=patch_loc,
                                patch_shape=patch_shape, editable=False)




if __name__ == '__main__':

    loaded_images= load_data(DATA_PATH, LIM)
    active_img_idx= 0
    default_shape= 64, 64
    default_location= 0, 0

    app= dash.Dash("Data Schema Config", external_stylesheets=external_stylesheets)
    app.layout= html.Div([
        html.H2("Configuring Extractor"),
        html.Div(render_patch_page(active_img_idx=active_img_idx,
                                   patch_loc=default_location,
                                   patch_shape=default_shape), id="patch-page"),
        # html.Div(render_staging_page(active_img_idx=active_img_idx,
        #                              patch_loc=default_location,
        #                              patch_shape=default_shape), id="staging-page"),

        html.Div(None, id="hidden-state") #, style=styles['hidden'])
    ])
    register_callbacks(app)

    app.run_server(debug=True)
