import pytest
import json
from rdv.schema import Schema
from rdv.feature import FloatFeature
from rdv.stats import NumericStats, CategoricStats
from rdv.extractors.vision.similarity import FixedSubpatchSimilarity


def test_schema_jcr():
    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101))
    component = FloatFeature(name="testcomponent", extractor=extractor, stats=stats)
    component2 = FloatFeature(name="testcomponent2", extractor=extractor, stats=stats)

    schema = Schema(name="Testing", version="1.0.0", features=[component, component2])
    schema_jcr = schema.to_jcr()
    assert len(schema_jcr["features"]) == 2
    jsonstr = json.dumps(schema_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    schema_restored = Schema.from_jcr(schema_jcr)

    assert schema.name == schema_restored.name
    assert schema.version == schema_restored.version
    assert all([c1 == c2 for (c1, c2) in zip(schema.features.keys(), schema_restored.features.keys())])
