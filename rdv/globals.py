import json

import tempfile
import time
import webbrowser
from multiprocessing import Process

from abc import ABC, abstractmethod


class SchemaStateException(Exception):
    pass


class DataException(Exception):
    pass


class Serializable(ABC):
    def class2str(self):
        module = str(self.__class__.__module__)
        classname = str(self.__class__.__name__)
        return f"{module}.{classname}"

    @abstractmethod
    def to_jcr(self):
        # Return a json-compatible representation
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_jcr(cls, jcr):
        # Load a json-compatible representation
        raise NotImplementedError()


class Buildable(ABC):
    @abstractmethod
    def build(self, data):
        raise NotImplementedError

    @abstractmethod
    def is_built(self):
        raise NotImplementedError


class Configurable(ABC):
    @classmethod
    @abstractmethod
    def configure_interactive(self, loaded_data, mode="inline"):
        raise NotImplementedError
