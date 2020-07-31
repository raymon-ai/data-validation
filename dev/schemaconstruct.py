#%%
%load_ext autoreload
%autoreload 2
from pydoc import locate
from rdv.schema import Schema
from rdv.component import NumericComponent, Stats
from rdv.extractors.vision.similarity import FixedSubpatchSimilarity



# ser_class = locate('rdv.similarity.Serializable')
extractor = FixedSubpatchSimilarity("First Try")
sim_component = NumericComponent(extractor=extractor)
components = [
    sim_component,
]
schema = Schema(components=components)
schema.save('./schema.json')


# %%
schema = Schema()
schema.load('./schema.json')
schema

# %%
extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=[1, 2])
stats = Stats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, bins=[10, 10])
component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
schema = Schema(name="Testing", version='1.0.0', components=[component, component])
schema.save('./schema.json')


# %%
