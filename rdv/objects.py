import abc

class Serializable:
    
    @abc.abstractmethod
    def to_jdr(self):
        # Return a json-dumpable representation
        raise NotImplementedError()
    
    @abc.abstractmethod
    def load_jdr(self, jcr):
        # Load a json-dumpable representation
        raise NotImplementedError()


class FeatureExtractor:
    
    compiled_attributes = []

    def __init__(self, attr1=None, attr2=None):
        self.configured_required = []
        self.compiler_required = []
        pass
    
    def check_attrs(self, attributes):
        for attr in attributes:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                return False
        return True
    
    def is_configured(self):
        configured_required = []

        return self.check_attrs(self.configured_attributes)
    
    def is_compiled(self):
        return self.check_attrs(self.compiled_attributes)
    
    def configure_interact(self, st, output):
        pass
        

        
class SchemaComponent:
    
    configured_attributes = []
    compiled_attributes = []
    
    def __init__(self, extractor):
        self.extractor = extractor
        self.compiled = False
        
    def warmup(self, sample):
        ## Store whatever you need to state. e.g. record the min and max value so far
        pass

    
    def configure(self, st):
        # Let the user inspect the results of warmup stage
        pass
    
    def compiler_add(self, data):
        # Add data to compilation
        pass
        
    def compile(self):
        pass
    
    def verify_compilation(self):
        # Let the user inspect and edit the schema. Ask for input if required
        pass
    
    def extract(self, data):
        # 
    
    def check_sample(self, sample):
        # Compare extracted feature to min, max or other hard boundary
        pass
    
    def compare(self, schema):
        # Compare with another schema
        pass

