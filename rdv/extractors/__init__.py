import abc

from rdv import Serializable, CCAble

class FeatureExtractor(Serializable, CCAble):

    @abc.abstractmethod
    def extract(self, data):
        """Extracts a feature from the data.

        Args:
            data (Object): [description]
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def configure(self, config):
        for attr in self._config_attrs:
            setattr(self, attr, config['attr'])
        return self

    def configure_interact(self, st, output):
        pass


class NoneExtractor(FeatureExtractor):

    def to_jcr(self):
        data = {
        }
        return data

    def load_jcr(self, jcr):
        self.name = jcr['name']
        return self
