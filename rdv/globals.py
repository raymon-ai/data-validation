import json

import tempfile
import time
import webbrowser
from multiprocessing import Process

from abc import ABC, abstractmethod
from rdv.dash.helpers import dash_input


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
    @abstractmethod
    def configure_interactive(self, loaded_data):
        raise NotImplementedError

    @abstractmethod
    def set_config(self, data):
        raise NotImplementedError

    @abstractmethod
    def is_configured(self):
        raise NotImplementedError

    @dash_input
    def _configure(self, loaded_data):
        config = self.configure_interactive(loaded_data=loaded_data)
        return config

    def configure(self, data):
        config = self._configure(data)
        print(f"Config received: {config}")
        if len(config) > 0:
            self.set_config(config)
        return config

        # _, output_fpath = tempfile.mkstemp()
        # print(f"Saving to: {output_fpath}")
        # # Crease new process
        # p = Process(
        #     target=self.configure_interactive,
        #     args=(data, output_fpath),
        # )
        # p.start()
        # time.sleep(0.5)
        # webbrowser.open_new("http://127.0.0.1:8050/")
        # p.join()
        # # Load saved config and save to extractor
        # with open(output_fpath, "r") as f:
        #     loaded = json.load(f)
        #
