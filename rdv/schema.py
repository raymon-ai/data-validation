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
from rdv.component import Component
from rdv.dash.helpers import windowcloselistener, dash_app


class Schema(Serializable, Buildable):
    _attrs = ["name", "version", "components"]

    def __init__(self, name="default", version="0.0.0", components=[]):

        self._name = None
        self._version = None
        self._components = {}

        self.name = str(name)
        self.version = str(version)
        self.components = components

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
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        if isinstance(value, list) and all(isinstance(comp, Component) for comp in value):
            # Convert to dict
            self._components = {c.name: c for c in value}

        elif isinstance(value, dict) and all(isinstance(comp, Component) for comp in value.values()):
            self._components = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
            "components": [],
        }
        components = []
        for comp in self.components.values():
            components.append({"component_class": comp.class2str(), "component": comp.to_jcr()})
        jcr["components"] = components
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        name = jcr["name"]
        version = jcr["version"]
        components = []
        for comp_dict in jcr["components"]:
            classpath = comp_dict["component_class"]
            comp_jcr = comp_dict["component"]
            compclass = locate(classpath)
            if compclass is None:
                NameError("Could not locate classpath")
            component = compclass.from_jcr(comp_jcr)
            components.append(component)

        return cls(name=name, version=version, components=components)

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
            raise SchemaStateException(f"Some schema component extractors require configuration.")
        # Build the schema
        for comp in self.components.values():
            # Compile stats
            comp.build(data)

    def is_built(self):
        return all(comp.is_built() for comp in self.components.values())

    """Configurable extractors support"""

    def get_unconfigured(self):
        unconfigureds = []
        for component in self.components.values():
            if component.requires_config():
                unconfigureds.append(component)
        return unconfigureds

    def configure(self, data):
        require_config = self.get_unconfigured()
        for comp in require_config:
            print(f"Starting configuration wizard for {comp.name} extractor...")
            comp.extractor.configure(data)
            print(f"Done.")
        print(f"Configuration complete.")

    """Other Methods"""

    def check(self, data, convert_json=True):
        tags = []
        if self.is_built():
            for component in self.components.values():
                tag = component.check(data)
                tags.extend(tag)
        else:
            raise SchemaStateException(
                f"Cannot check data on an unbuilt schema. Check whether all components are built."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def drop_component(self, name):
        self.components = [c for c in self.components.values() if c.name != name]

    @dash_app
    def view(self, poi=None):
        def get_component_page(component_name):
            return html.Div(
                id="component-page-div",
                children=[
                    dcc.Graph(id="component-graph", figure=self.components[component_name].plot()),
                    dcc.Link("Back", href=f"/"),
                ],
                className="my-3",
            )

        def component2row(comp):
            return html.Tr(
                [
                    html.Td(dcc.Link(comp.name, href=f"/{comp.name}")),
                    html.Td(comp.__class__.__name__, className="codelike-content"),
                    html.Td(
                        dcc.Graph(
                            id=f"{comp.name}-prev",
                            figure=comp.plot(size=(400, 150), hist=False),
                            config={"displayModeBar": False},
                        )
                    ),
                ]
            )

        def get_component_table():
            return html.Table(
                children=[
                    html.Thead(
                        className="schema-tablehead",
                        children=[
                            html.Tr(
                                [
                                    html.Td("Component", className="schema-name-column"),
                                    html.Td("Type", className="schema-type-column"),
                                    html.Td("Indicator", className="schema-preview-column"),
                                ]
                            )
                        ],
                    ),
                    html.Tbody(children=[component2row(comp) for comp in self.components.values()]),
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
                return get_component_table()
            else:
                return get_component_page(pathname.split("/")[1])

        app.run_server()
