import json

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from rdv.dash_helpers import register_shutdown, register_close, styles


def dash_fsps(app, loaded_images, output_path):
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
            **patch,
        )
        fig.update_xaxes(showgrid=False, range=(0, img_width))
        fig.update_yaxes(showgrid=False, scaleanchor="x", range=(img_height, 0))

        fig.update_layout(autosize=False, width=800, height=800)
        return fig

    def render_patch_page(loaded_images, active_img_idx, state):
        return html.Div(
            [
                html.Div(
                    [
                        html.H5("Global controls"),
                        html.Label("Select the image to view:"),
                        dcc.Input(
                            id="img-selector",
                            type="number",
                            value=0,
                            min=0,
                            max=len(loaded_images) - 1,
                            step=1,
                        ),
                        html.Label("Patch Location:"),
                        html.Pre(
                            json.dumps(state, indent=4),
                            id="raymon-state",
                            style=styles["pre"],
                        ),
                        html.Label("Patch Shape:"),
                        html.Pre(
                            str(state2shape(state)),
                            id="patch-shape",
                            style=styles["pre"],
                        ),
                        html.Button("Continue", id="patch-setup-complete", n_clicks=0),
                    ],
                    className="three columns",
                    id="left-column-div",
                ),
                html.Div(
                    [
                        html.H5("Example"),
                        dcc.Graph(
                            id="graph-image",
                            figure=create_image_fig(active_img_idx=active_img_idx, patch=state),
                        ),
                        html.Div(id="hidden-dummy"),
                    ],
                    className="nine columns",
                ),
            ],
            className="row",
        )

    def state2shape(state):
        if state is None:
            raise PreventUpdate()
        x0, y0 = state["x0"], state["y0"]
        x1, y1 = state["x1"], state["y1"]
        return x1 - x0, y1 - y0

    def register_callbacks(app):
        register_close(
            app,
            dash_input=[Input("patch-setup-complete", "n_clicks")],
            dash_output=Output("hidden-dummy", "value"),
        )

        register_shutdown(
            app,
            fpath=output_path,
            dash_input=[Input("patch-setup-complete", "n_clicks")],
            dash_output=Output("page-body", "children"),
            dash_state=[State("raymon-state", "children")],
        )

        @app.callback(
            [
                Output(component_id="raymon-state", component_property="children"),
                Output(component_id="patch-shape", component_property="children"),
            ],
            [Input(component_id="graph-image", component_property="relayoutData")],
        )
        def update_patch_data(shape_data):
            if shape_data is None or not "shapes[0].x0" in shape_data:
                raise PreventUpdate()

            keys = ["x0", "y0", "x1", "y1"]
            data = {key: int(shape_data[f"shapes[0].{key}"]) for key in keys}
            patch_width = int(data["x1"] - data["x0"])
            patch_height = int(data["y1"] - data["y0"])

            return f"{json.dumps(data, indent=4)}", str((patch_width, patch_height))

        @app.callback(
            Output(component_id="graph-image", component_property="figure"),
            [Input(component_id="img-selector", component_property="value")],
            [State("raymon-state", "children")],
        )
        def swap_img(active_image_idx, state):
            if state is None:
                raise PreventUpdate()
            if isinstance(state, str):
                state = json.loads(state)
            active_image_idx = int(active_image_idx)

            return create_image_fig(active_img_idx=active_image_idx, patch=state)

    register_callbacks(app)
    app.layout = html.Div(
        [
            html.H2("Configuring Extractor"),
            html.Div(
                render_patch_page(
                    loaded_images=loaded_images,
                    active_img_idx=0,
                    state={"x0": 0, "y0": 0, "x1": 64, "y1": 64},
                )
            ),
        ],
        id="page-body",
    )

    app.run_server(debug=False)
