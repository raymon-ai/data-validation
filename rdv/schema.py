import json
from pydoc import locate
from pathlib import Path
import time
import webbrowser
from multiprocessing import Process
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import rdv
from rdv.globals import Buildable, SchemaStateException, Serializable
from rdv.feature import Feature
from rdv.dash.helpers import windowcloselistener, dash_app
from rdv.tags import SCHEMA_FEATURE


class Schema(Serializable, Buildable):
    _attrs = ["name", "version", "features"]

    def __init__(self, name="default", version="0.0.0", features=[]):

        self._name = None
        self._version = None
        self._features = {}

        self.name = str(name)
        self.version = str(version)
        self.features = features

    """Serializable interface"""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Schema name should be a string")
        self._name = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Schema version should be a string")
        self._version = value

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        if isinstance(value, list) and all(isinstance(feat, Feature) for feat in value):
            # Convert to dict
            self._features = {c.name: c for c in value}

        elif isinstance(value, dict) and all(isinstance(feat, Feature) for feat in value.values()):
            self._features = value
        else:
            raise ValueError(f"features must be a list[Feature] or dict[str, Feature]")

    @property
    def group_idfr(self):
        return f"{self.name}@{self.version}"

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
            "features": [],
        }
        features = []
        for feat in self.features.values():
            features.append({"feature_class": feat.class2str(), "feature": feat.to_jcr()})
        jcr["features"] = features
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        name = jcr["name"]
        version = jcr["version"]
        features = []
        for comp_dict in jcr["features"]:
            classpath = comp_dict["feature_class"]
            comp_jcr = comp_dict["feature"]
            compclass = locate(classpath)
            if compclass is None:
                NameError("Could not locate classpath")
            feature = compclass.from_jcr(comp_jcr)
            features.append(feature)

        return cls(name=name, version=version, features=features)

    def save(self, fpath):
        with open(fpath, "w") as f:
            json.dump(self.to_jcr(), f, indent=4)

    @classmethod
    def load(cls, fpath):
        with open(fpath, "r") as f:
            jcr = json.load(f)
        return cls.from_jcr(jcr)

    """Buildable Interface"""

    def build(self, data):
        # check wheter there are no extractors that require config
        require_config = self.get_unconfigured()
        if len(require_config) > 0:
            raise SchemaStateException(f"Some schema feature extractors require configuration.")
        # Build the schema
        for feat in self.features.values():
            # Compile stats
            feat.build(data)

    def is_built(self):
        return all(feat.is_built() for feat in self.features.values())

    """Configurable extractors support"""

    def get_unconfigured(self):
        unconfigureds = []
        for feature in self.features.values():
            if feature.requires_config():
                unconfigureds.append(feature)
        return unconfigureds

    def configure(self, data):
        require_config = self.get_unconfigured()
        for feat in require_config:
            print(f"Starting configuration wizard for {feat.name} extractor...")
            feat.extractor.configure(data)
            print(f"Done.")
        print(f"Configuration complete.")

    """Other Methods"""

    def set_schema_group(self, tags):
        for feature_tag in tags:
            feature_tag.group = self.group_idfr

    def check(self, data, convert_json=True):
        tags = []
        if self.is_built():
            for feature in self.features.values():
                feature_tags = feature.check(data)
                self.set_schema_group(feature_tags)
                tags.extend(feature_tags)
        else:
            raise SchemaStateException(f"Cannot check data on an unbuilt schema. Check whether all features are built.")
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def drop_feature(self, name):
        self.features = [c for c in self.features.values() if c.name != name]

    def tags2featvalue(self, tags):
        tags_dict = {}
        for tag in tags:
            if tag["type"] == SCHEMA_FEATURE:
                tags_dict[tag["name"]] = tag["value"]
        return tags_dict

    @dash_app
    def view(self, poi=None):
        if poi is not None:
            poi_dict = self.tags2featvalue(self.check(poi))
        else:
            poi_dict = {}

        def get_feature_page(feature_name):
            return html.Div(
                id="feature-page-div",
                children=[
                    dcc.Graph(id="feature-graph", figure=self.features[feature_name].plot()),
                    dcc.Link("Back", href=f"/"),
                ],
                className="my-3",
            )

        def feature2row(feat):
            return html.Tr(
                [
                    html.Td(dcc.Link(feat.name, href=f"/{feat.name}")),
                    html.Td(feat.__class__.__name__, className="codelike-content"),
                    html.Td(
                        dcc.Graph(
                            id=f"{feat.name}-prev",
                            figure=feat.plot(size=(400, 150), poi=poi_dict.get(feat.name, None), hist=False),
                            config={"displayModeBar": False},
                        )
                    ),
                ]
            )

        def get_feature_table():
            return html.Table(
                children=[
                    html.Thead(
                        className="schema-tablehead",
                        children=[
                            html.Tr(
                                [
                                    html.Td("Feature", className="schema-name-column"),
                                    html.Td("Type", className="schema-type-column"),
                                    html.Td("Indicator", className="schema-preview-column"),
                                ]
                            )
                        ],
                    ),
                    html.Tbody(children=[feature2row(feat) for feat in self.features.values()]),
                ]
            )

        app = dash.Dash(
            __name__,
            assets_folder=str((Path(rdv.dash.__file__) / "../assets").resolve()),
        )
        app.title = f"Schema viewer"
        app.layout = html.Div(
            className="schema-container",
            children=[
                dcc.Location(id="url", refresh=False),
                windowcloselistener(app),
                html.Div(
                    className="my-5",
                    children=[
                        html.H1(app.title, className="my-3"),
                        html.H3(
                            [
                                "Schema:",
                                html.Span(self.name, className="codelike-flex"),
                                ", Version:",
                                html.Span(self.version, className="codelike-flex"),
                            ],
                            className="my-3",
                        ),
                        html.Div(id="page-content"),
                    ],
                ),
            ],
        )

        @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
        def display_page(pathname):
            if pathname == "/":
                return get_feature_table()
            else:
                return get_feature_page(pathname.split("/")[1])

        app.run_server()

    @dash_app
    def compare(self, other, pthresh=0.05):
        def drift_cell(feat_name):
            self_feat = self.features[feat_name]
            other_feat = other.features[feat_name]
            _, pvalue, drift = self_feat.stats.test_drift(other_feat.stats, pthresh=pthresh)
            if drift:
                return html.Span(className="Label mr-1 Label--red", children=f"{pvalue:.2E}")
            else:
                return html.Span(className="Label mr-1 Label--green", children=f"{pvalue:.2E}")

        def get_feature_page(feature_name):
            return html.Div(
                id="feature-page-div",
                children=[
                    dcc.Graph(
                        id="feature-graph",
                        figure=other.features[feature_name].compare(
                            size=(400, 150), other=other.features[feature_name]
                        ),
                    ),
                    dcc.Link("Back", href=f"/"),
                ],
                className="my-3",
            )

        def feature2row(feat):
            return html.Tr(
                [
                    html.Td(dcc.Link(feat.name, href=f"/{feat.name}")),
                    html.Td(feat.__class__.__name__, className="codelike-content"),
                    html.Td(drift_cell(feat.name), className="codelike-content"),
                    html.Td(
                        dcc.Graph(
                            id=f"{feat.name}-prev",
                            figure=feat.compare(size=(400, 150), other=other.features[feat.name]),
                            config={"displayModeBar": False},
                        )
                    ),
                ]
            )

        def get_feature_table():
            return html.Table(
                children=[
                    html.Thead(
                        className="schema-tablehead",
                        children=[
                            html.Tr(
                                [
                                    html.Td("Feature", className="schema-name-column"),
                                    html.Td("Type", className="schema-type-column"),
                                    html.Td("H0 pvalue", className="schema-h0-column"),
                                    html.Td("Indicator", className="schema-preview-column"),
                                ]
                            )
                        ],
                    ),
                    html.Tbody(children=[feature2row(feat) for feat in self.features.values()]),
                ]
            )

        app = dash.Dash(
            __name__,
            assets_folder=str((Path(rdv.dash.__file__) / "../assets").resolve()),
        )
        app.title = f"Schema compare"
        app.layout = html.Div(
            className="schema-container",
            children=[
                dcc.Location(id="url", refresh=False),
                windowcloselistener(app),
                html.Div(
                    className="my-5",
                    children=[
                        html.H1(app.title, className="my-3"),
                        html.H3(
                            [
                                "Schema",
                                html.Span(self.name, className="codelike-flex"),
                                ", Version:",
                                html.Span(self.version, className="codelike-flex"),
                                html.Span("(self)", className="codelike-flex"),
                                " vs Schema",
                                html.Span(other.name, className="codelike-flex"),
                                ", Version:",
                                html.Span(other.version, className="codelike-flex"),
                                html.Span("(other)", className="codelike-flex"),
                            ],
                            className="my-3",
                        ),
                        html.Div(id="page-content"),
                    ],
                ),
            ],
        )

        @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
        def display_page(pathname):
            if pathname == "/":
                return get_feature_table()
            else:
                return get_feature_page(pathname.split("/")[1])

        app.run_server()
