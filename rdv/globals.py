from abc import ABC, abstractmethod


class ClassNotFoundError(Exception):
    pass


class Serializable(ABC):

    def class2str(self, obj=None):
        if obj is None:
            return None
        module = str(obj.__class__.__module__)
        classname = str(obj.__class__.__name__)
        return f"{module}.{classname}"

    @abstractmethod
    def to_jcr(self):
        # Return a json-compatible representation
        raise NotImplementedError()

    @abstractmethod
    def load_jcr(self, jcr):
        # Load a json-compatible representation
        raise NotImplementedError()


class CCAble(ABC):

    # Base class for Configurable and Compilable classes.

    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    @abstractmethod
    def configure(self, data):
        raise NotImplementedError

    @abstractmethod
    def compile(self, data):
        raise NotImplementedError

    def check_has_attrs(self, attributes):
        for attr in attributes:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                return False
        return True

    def check_dep(self, dep, func):
        # check whether dep is CCAble and call the desired check on it. (is_configured / is_compiled)
        if not (isinstance(dep, CCAble) and getattr(dep, func)()):
            return False
        return True

    def check_deps(self, func):
        for attr in self._ccable_deps:
            dep_value = getattr(self, attr)
            # The dependent attribute can be a list (in case of checking a schema's components)
            if isinstance(dep_value, list):
                for dep in dep_value:
                    ok = self.check_dep(dep, func=func)
                    if not ok:
                        return False
            else:  # The dependency is an object
                ok = self.check_dep(dep_value, func=func)
                if not ok:
                    return False
        return True

    def is_configured(self):
        has_attrs = self.check_has_attrs(self._config_attrs + self._ccable_deps)
        if not has_attrs:
            return False
        # Dependencies need to be configured and compiled
        return self.check_deps(func='is_configured') and self.check_deps(func='is_compiled')  
    
    def is_compiled(self):
        has_attrs = self.check_has_attrs(self._compile_attrs + self._ccable_deps)
        if not has_attrs:
            return False
        return self.check_deps(func='is_compiled')

    def __eq__(self, other):
        for attr in self._attrs:
            if isinstance(getattr(self, attr), list):
                selflist = getattr(self, attr)
                otherlist = getattr(other, attr)
                for self_el, other_el in zip(selflist, otherlist):
                    if not self_el == other_el:
                        return False

            else:
                if not getattr(self, attr) == getattr(other, attr):
                    return False
        return True


class FeatureExtractor(Serializable, CCAble, ABC):

    @abstractmethod
    def extract_feature(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        raise NotImplementedError


class NoneExtractor(FeatureExtractor):

    def to_jcr(self):
        data = {
        }
        return data

    def load_jcr(self, jcr):
        return self

    def extract(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        return 0

    def configure(self, data):
        pass

    def compile(self, data):
        pass
    
    def extract_feature(self, data):
        pass
