

class Component:
    def __init__(self, config=None):
        self.requires_interaction = False  # Fixed per class
        pass
    
    def process(self, data):
        return {
            'feature_1': 1,
            'feature_2' 2
        }
        
    def configure(self):
        raise NotImplementedError()

    def interact(self, st):
        # Will only be called if self.requires_interaction
        # Put streamlit components for every config param

        raise NotImplementedError()

    
    def tojcr(self):
        # Must return a JSON-compatible representation of this component's state
        raise NotImplementedError()

    
class Schema:
    
    def __init__(self, components):
        pass
    
    def 
