import json
from pydoc import locate

from rdv.globals import Buildable, ClassNotFoundError, SchemaStateException, Serializable
from rdv.component import Component


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
