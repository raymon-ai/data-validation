import json
from pydoc import locate


from rdv.globals import (
    CCAble,
    ClassNotFoundError,
    Serializable,
    DataException,
    SchemaCompilationException,
)


class Schema(Serializable, CCAble):
    _config_attrs = ["name", "version"]
    _compile_attrs = []
    _ccable_deps = ["components"]
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, name="default", version="0.0.0", components=[]):
        self.name = str(name)
        self.version = str(version)
        self.components = components

    """Serializable interface"""

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
            "components": [],
        }
        components = []
        for comp in self.components:
            components.append(
                {"component_class": self.class2str(comp), "component": comp.to_jcr()}
            )
        jcr["components"] = components
        return jcr

    def load_jcr(self, jcr):
        self.name = jcr["name"]
        self.version = jcr["version"]
        components = []
        for comp_dict in jcr["components"]:
            classpath = comp_dict["component_class"]
            comp_jcr = comp_dict["component"]
            compclass = locate(classpath)
            if compclass is None:
                raise ClassNotFoundError("Could not locate classpath")
            component = compclass().load_jcr(comp_jcr)
            components.append(component)

        self.components = components
        return self

    """CCAble Interface"""

    def configure(self, data):
        """This will configure the components extractors and stats, and will compile the extracotrs using the loaded data.
        Steps:
        1. Find components with unconfigured extractors
        2. Select component to configure
            1. Config extractor
            2. Compile extractor & propose stats config
            3. Inspect stat config

        Args:
            loaded_data ([type]): [description]
        """
        # Find unconfigured components

        # Configure extractor, process loaded data (compile extractor), configure stats
        unconfigs = self.get_unconfigured()
        for comp in unconfigs:
            # Configure component
            comp.configure(data)

    def compile(self, data):
        """Compile the schema."""
        for comp in self.components:
            # Compile stats
            comp.compile(data)

    """Other Methods"""

    def check(self, data, convert_json=True):
        tags = []
        if self.is_compiled():
            for component in self.components:
                tag = component.check(data)
                tags.extend(tag)
        else:
            raise SchemaCompilationException(
                f"Cannot check data on an uncompiled schema. Check whether all components are compiled."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def save(self, fpath):
        with open(fpath, "w") as f:
            json.dump(self.to_jcr(), f, indent=4)

    def load(self, fpath):
        with open(fpath, "r") as f:
            jcr = json.load(f)
        return self.load_jcr(jcr)

    def get_unconfigured(self):
        unconfigureds = []
        for component in self.components:
            if not component.is_configured():
                unconfigureds.append(component)

        return unconfigureds

    def drop_component(self, name):
        self.components = [c for c in self.components if c.name != name]

    @classmethod
    def from_json(cls, json):
        schema = cls()
        schema.load_jcr(json)
        return schema
