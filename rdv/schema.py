import json
from pydoc import locate

from rdv.globals import Buildable, ClassNotFoundError, NotSupportedException, SchemaBuildingException, Serializable


class Schema(Serializable, Buildable):
    _attrs = ["name", "version", "components"]

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
            components.append({"component_class": comp.class2str(), "component": comp.to_jcr()})
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

    def save(self, fpath):
        with open(fpath, "w") as f:
            json.dump(self.to_jcr(), f, indent=4)

    def load(self, fpath):
        with open(fpath, "r") as f:
            jcr = json.load(f)
        return self.load_jcr(jcr)

    """Buildable Interface"""

    def build(self, data):
        # check wheter there are no extractors that require config
        require_config = self.get_unconfigured()
        if len(require_config) > 0:
            raise SchemaBuildingException(f"Some schema component extractors require configuration.")
        # Build the schema
        for comp in self.components:
            # Compile stats
            comp.build(data)

    def is_built(self):
        return all(comp.is_built() for comp in self.components)

    """Configurable extractors support"""

    def get_unconfigured(self):
        unconfigureds = []
        for component in self.components:
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
            for component in self.components:
                tag = component.check(data)
                tags.extend(tag)
        else:
            raise NotSupportedException(
                f"Cannot check data on an unbuilt schema. Check whether all components are built."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def drop_component(self, name):
        self.components = [c for c in self.components if c.name != name]

    @classmethod
    def from_json(cls, json):
        schema = cls()
        schema.load_jcr(json)
        return schema
