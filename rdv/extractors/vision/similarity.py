import base64
import json
import random
from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
import imagehash
import numpy as np
import plotly.graph_objects as go
import rdv.dash
from dash.dependencies import Input, Output
from rdv.dash.helpers import get_dash
from rdv.extractors import FeatureExtractor
from rdv.globals import Configurable


class FixedSubpatchSimilarity(FeatureExtractor, Configurable):

    _attrs = ["patch", "refs"]
    _patch_keys = ["x0", "y0", "x1", "y1"]

    def __init__(self, patch, refs=None, nrefs=10, idfr=None):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self._nrefs = None
        self._patch = None
        self._refs = None
        self._idfr = None

        self.patch = patch
        self.nrefs = nrefs
        self.refs = refs
        self.idfr = idfr

    """
    PROPERTIES
    """

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, value):

        if isinstance(value, dict):
            self._patch = {key: value[key] for key in self._patch_keys}
        elif isinstance(value, list) and len(value) == 4:
            self._patch = {key: value[i] for i, key in enumerate(self._patch_keys)}
        else:
            raise ValueError(f"patch must be a dict or list, not {type(value)}")
        # make sure the correct keys are there
        print(f"Patch set to: {self._patch} for {self}")

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

    @property
    def idfr(self):
        return self._idfr

    @idfr.setter
    def idfr(self, value):
        self._idfr = str(value)

    """Feature extractor"""

    def extract_feature(self, data):
        phash = self._extract(data)
        dist = min(abs(ref - phash) for ref in self.refs)
        return dist

    def _extract(self, data):
        patch = [self.patch["x0"], self.patch["y0"], self.patch["x1"], self.patch["y1"]]
        crop = data.crop(box=patch)
        phash = imagehash.phash(crop)
        return phash

    """Serializable interface """

    def to_jcr(self):
        data = {
            "patch": self.patch,
            "refs": [str(ref) for ref in self.refs] if self.refs is not None else None,
            "nrefs": self.nrefs,
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        patch, refs, nfres, idfr = None, None, None, None
        if "patch" in jcr:
            patch = jcr["patch"]
        if "nrefs" in jcr:
            nrefs = jcr["nrefs"]
        if "refs" in jcr:
            refs = jcr["refs"]
        if "idfr" in jcr:
            refs = jcr["idfr"]

        return cls(patch=patch, refs=refs, nrefs=nrefs, idfr=idfr)

    """Buildable interface"""

    def build(self, data):
        refs = []
        chosen_samples = random.choices(data, k=self.nrefs)
        for sample in chosen_samples:
            ref = self._extract(sample)
            refs.append(ref)
        self.refs = refs

    def is_built(self):
        return self.refs is not None and len(self.refs) == self.nrefs

    def __str__(self):
        return f"{self.class2str()} ({self.idfr})"

    """Configurable interface"""

    def set_config(self, data):
        self.patch = data

    def is_configured(self):
        return isinstance(self.patch, dict) and all(key in self.patch for key in self._patch_keys)

    @classmethod
    def configure_interactive(cls, loaded_data, mode="inline"):
        def render_controls():
            return html.Div(
                [
                    html.H3("Controls", className="Subhead"),
                    html.Form(
                        html.Div(
                            className="form",
                            children=[
                                html.Div(
                                    id="page-controls",
                                    children=[],
                                ),
                                html.Div(
                                    className="form-group-header",
                                    children=html.Label("Patch Location:", className="m-2"),
                                ),
                                html.Div(
                                    className="form-group-body",
                                    children=html.Pre(
                                        id="patch-config",
                                        className="m-2 similarity-code-view",
                                    ),
                                ),
                                html.Div(
                                    className="form-group-body",
                                    children=html.Div(
                                        id="extractor-constructor",
                                        className="m-2 codelike-content",
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
                className="col-4 float-left",
                id="left-column-div",
            )

        def render_img_view():
            return html.Div(
                [
                    html.H3("View", className="Subhead"),
                    dcc.Graph(
                        id="graph-image",
                    ),
                    html.Div(id="hidden-dummy"),
                ],
                className="col-8 float-left",
            )

        def render_figure(active_img_idx, patch, editable=True):
            active_img = loaded_data[active_img_idx].copy()
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

        applauncher, kwargs = get_dash(mode=mode)
        app = applauncher(  # dash.Dash(
            "Data Schema Config",
            assets_folder=str((Path(rdv.dash.__file__) / "../assets").resolve()),
        )
        app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.Div(
                    [
                        html.H1(f"Configuring extractor {cls.__name__}", className="pagehead mb-5"),
                        html.Div(
                            [
                                render_controls(),
                                render_img_view(),
                            ],
                            className="clearfix",
                        ),
                    ],
                    className="gutter-md-spacious",
                ),
            ],
            id="page-body",
            className="schema-container",
        )
        app.title = f"Configuring component {cls.__name__}"

        @app.callback(
            [
                Output(component_id="patch-config", component_property="children"),
                Output(component_id="extractor-constructor", component_property="children"),
            ],
            [Input(component_id="graph-image", component_property="relayoutData")],
        )
        def update_patch_data(shape_data):
            keys = ["x0", "y0", "x1", "y1"]

            if shape_data is None or not "shapes[0].x0" in shape_data:
                # raise PreventUpdate()
                data = {"x0": 0, "y0": 0, "x1": 64, "y1": 64}
            else:
                data = {key: int(shape_data[f"shapes[0].{key}"]) for key in keys}

            return f"{json.dumps(data, indent=4)}", f"{cls.__name__}(patch={[data[k] for k in keys]})"

        def parse_imgidx(pathname):
            if pathname == "/":
                img_idx = 0
            else:
                img_idx = int(pathname.split("/")[-1])
            return img_idx

        @app.callback(
            Output("graph-image", "figure"),
            [Input("url", "pathname"), Input("url", "search")],
            # [State("patch-config", "children")],
        )
        def render_img(pathname, search):

            if len(search) == 0:
                patch = {"x0": 0, "y0": 0, "x1": 64, "y1": 64}
            else:
                patchenc = search.split("patch=")[1]
                patch = json.loads(base64.b64decode(patchenc.encode("ascii")).decode("ascii"))

            img_idx = parse_imgidx(pathname)
            return render_figure(active_img_idx=img_idx, patch=patch)

        @app.callback(
            Output("page-controls", "children"),
            [Input("url", "pathname"), Input("patch-config", "children")],
        )
        def update_controls(pathname, patch):
            img_idx = parse_imgidx(pathname)
            if patch is None:
                patch = json.dumps(None)
            patchenc = base64.b64encode(patch.encode("ascii")).decode("ascii")

            return [
                html.Button(dcc.Link("Prev", href=f"/{img_idx-1}?patch={patchenc}"), className="btn btn-sm m-2"),
                f"Image: {img_idx} / {len(loaded_data)}",
                html.Button(dcc.Link("Next", href=f"/{img_idx+1}?patch={patchenc}"), className="btn btn-sm m-2"),
            ]

        app.run_server(debug=True, **kwargs)
