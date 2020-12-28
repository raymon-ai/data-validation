import json
import os
import random
import sys
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import imagehash
import numpy as np
import plotly.graph_objects as go
import rdv.dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


from rdv.dash.helpers import register_close, register_shutdown, styles
from rdv.globals import FeatureExtractor


class FixedSubpatchSimilarity(FeatureExtractor):

    _config_attrs = ["patch"]
    _compile_attrs = ["refs"]
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    patch_keys = ["x0", "y0", "x1", "y1"]

    def __init__(self, patch=None, refs=None, nrefs=10):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self._nrefs = None
        self._patch = None
        self._refs = None

        self.patch = patch
        self.nrefs = nrefs
        self.refs = refs

    """
    PROPERTIES
    """

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, value):
        if value is None:
            self._patch = None
            return

        if not isinstance(value, dict):
            raise ValueError(f"patch must be a dict, not {type(value)}")
        # make sure the correct keys are there
        self._patch = {key: value[key] for key in self.patch_keys}

    @property
    def refs(self):
        return self._refs

    @refs.setter
    def refs(self, value):
        if value is None:
            self._refs = None
            return

        if not (isinstance(value, list) and len(value) == self.nrefs):
            raise ValueError(f"refs should be a list of length {self.nrefs}")

        parsed_refs = []
        for ref in value:
            if isinstance(ref, imagehash.ImageHash):
                parsed_refs.append(ref)
            elif isinstance(ref, str):
                parsed_refs.append(imagehash.hex_to_hash(ref))
            else:
                raise ValueError(f"refs should either be str or ImageHash, not {type(ref)}")

        self._refs = parsed_refs

    @property
    def nrefs(self):
        return self._nrefs

    @nrefs.setter
    def nrefs(self, value):
        value = int(value)
        if not (isinstance(value, int) and value > 0):
            self._nrefs = None
            raise ValueError(f"nrefs should be a an int > 0")
        self._nrefs = value

    """
    SERIALISATION
    """

    def to_jcr(self):
        data = {
            "patch": self.patch,
            "refs": [str(ref) for ref in self.refs] if self.refs is not None else None,
            "nrefs": self.nrefs,
        }
        return data

    def load_jcr(self, jcr):
        if "patch" in jcr:
            self.patch = jcr["patch"]
        if "nrefs" in jcr:
            self.nrefs = jcr["nrefs"]
        if "refs" in jcr:
            self.refs = jcr["refs"]

        return self

    def configure(self, data):
        jcr = {
            "patch": data,
        }
        self.load_jcr(jcr)

    def compile(self, data):
        refs = []
        chosen_samples = random.choices(data, k=self.nrefs)
        for sample in chosen_samples:
            ref = self._extract(sample)
            refs.append(ref)
        self.refs = refs

    def extract_feature(self, data):
        phash = self._extract(data)
        dist = min(abs(ref - phash) for ref in self.refs)
        return dist

    def _extract(self, data):
        patch = [self.patch["x0"], self.patch["y0"], self.patch["x1"], self.patch["y1"]]
        crop = data.crop(box=patch)
        phash = imagehash.phash(crop)
        return phash

    def configure_interactive(self, loaded_data, raymon_output, null_stderr=True):
        run_interactive_config(loaded_data, raymon_output, null_stderr=null_stderr)


def run_interactive_config(loaded_images, output_path, null_stderr=True):
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

    print(f"null_strerr: {null_stderr}")
    if null_stderr:
        f = open(os.devnull, "w")
        sys.stderr = f

    app = dash.Dash(
        "Data Schema Config",
        external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
        assets_folder=str((Path(rdv.dash.__file__) / "../assets").resolve()),
    )
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
