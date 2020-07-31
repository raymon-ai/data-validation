import pytest
import json
from rdv.schema import Schema
from rdv.component import NumericComponent, Stats
from rdv.extractors.vision.similarity import FixedSubpatchSimilarity

def test_stats_none():
    stats = Stats()
    jcr = stats.to_jcr()
    for attr in Stats._config_attrs + Stats._compile_attrs:
        assert jcr[attr] is None
        

def test_stats_partial_none():
    params = dict(min=0, max=1, nbins=10)
    stats = Stats(**params)
    jcr = stats.to_jcr()
    for attr in Stats._compile_attrs:
        assert jcr[attr] is None
    for attr in Stats._config_attrs:
        assert jcr[attr] == params[attr]


def test_component_jcr():
    comp = NumericComponent()
    comp_jcr = comp.to_jcr()
    jsonstr = json.dumps(comp_jcr)
    comp_restored = NumericComponent()
    comp_restored.load_jcr(comp_jcr)
    for attr in NumericComponent._attrs:
        assert getattr(comp, attr) == getattr(comp_restored, attr) 

def test_schema_jcr():
    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=[1, 2])
    stats = Stats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, bins=[10, 10])
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = Schema(name="Testing", version='1.0.0', components=[component, component])
    schema_jcr = schema.to_jcr()
    assert len(schema_jcr['components']) == 2
    jsonstr = json.dumps(schema_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    schema_restored = Schema()
    schema_restored.load_jcr(schema_jcr)
    assert schema == schema_restored
        
    
def test_stats_ccable():
    stats = Stats()
    assert not stats.is_configured() 
    assert not stats.is_compiled()

    
    stats = Stats(min=0, max=1, nbins=10)
    assert stats.is_configured()
    assert not stats.is_compiled()

    stats = Stats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, bins=[10, 10])
    assert stats.is_configured()
    assert stats.is_compiled()


def test_fsps_extractor_ccable():
    extractor = FixedSubpatchSimilarity()
    assert not extractor.is_configured()
    assert not extractor.is_compiled()

    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64])
    assert extractor.is_configured()
    assert not extractor.is_compiled()

    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=[1, 2])
    assert extractor.is_configured()
    assert extractor.is_compiled()
    

def test_component_ccable():
    component = NumericComponent(name="testcomponent")

    assert not component.is_configured()
    assert not component.is_compiled()
    
    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64])
    stats = Stats(min=0, max=1, nbins=10)
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    assert component.is_configured()
    assert not component.is_compiled()
    
    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=[1, 2])
    stats = Stats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, bins=[10, 10])
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    assert component.is_configured()
    assert component.is_compiled()


def test_schema_ccable():
    component = NumericComponent(name="testcomponent")
    schema = Schema(name="Testing", version='1.0.0',components=[component])
    assert not schema.is_configured()
    assert not schema.is_compiled()

    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64])
    stats = Stats(min=0, max=1, nbins=10)
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = Schema(name="Testing", version='1.0.0', components=[component])

    assert schema.is_configured()
    assert not schema.is_compiled()

    extractor = FixedSubpatchSimilarity(patch=[0, 0, 64, 64], refs=[1, 2])
    stats = Stats(min=0, max=1, nbins=2, mean=0.8, std=0.2, pinv=0.1, bins=[10, 10])
    component = NumericComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = Schema(name="Testing", version='1.0.0', components=[component, component])

    assert schema.is_configured()
    assert schema.is_compiled()
