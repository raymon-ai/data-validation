import abc
import json
from pydoc import locate

from rdv import Serializable, CCAble, ClassNotFoundError

class Schema(Serializable, CCAble):
    _config_attrs = ['name', 'version']
    _compile_attrs = []
    _ccable_deps = ['components']
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self, name='default', version='0.0.0', components=[]):
        self.name = str(name)
        self.version = str(version)
        self.components = components

    def to_jcr(self):
        jcr = {
            'name': self.name,
            'version': self.version,
            'components': []
        }
        components = []
        for comp in self.components:
            components.append({'component_class': self.class2str(comp),
                        'component': comp.to_jcr()})
        jcr['components'] = components
        return jcr

    def load_jcr(self, jcr):
        self.name = jcr['name']
        self.version = jcr['version']
        components = []
        for comp_dict in jcr['components']:
            classpath = comp_dict['component_class']
            comp_jcr = comp_dict['component']
            compclass = locate(classpath)
            if compclass is None:
                raise ClassNotFoundError("Could not locate classpath")
            component = compclass().load_jcr(comp_jcr)
            components.append(component)

        self.components = components
        return self

    def save(self, fpath):
        with open(fpath, 'w') as f:
            json.dump(self.to_jcr(), f, indent=4)

    def load(self, fpath):
        with open(fpath, 'r') as f:
            jcr = json.load(f)
        self.load_jcr(jcr)

    def get_unconfigured(self):
        unconfigureds = []
        for component in self.components:
            if not component.is_configured():
                unconfigureds.append(component)

        return unconfigureds

    def configure(self):
        unconfigs = self.get_unconfigured()
        print(f"{len(unconfigs)} Components need to be configured")
