# RDV Schemas

In RDV, a data schema is used to capture data characteristics at train time. These characteristics can then be used in production settings to validate incoming data samples and to monitor and compare aggragate data distributions. 

## Features, Extractors and Stats
In RDV, every schema contains out of one or more features, represented by `rdv.feature.Feature` objects. RDV tracks the distribution statistics for each of those features and uses those to validate incoming data after deployment. Features are calculated by `rdv.extractors.FeatureExtractor` objects, which take a piece of data as input and return a feature as output.

### Feature Extractors
The most straighforward feature extractor is one that takes a vector of structured data, and extracts one specific element like the "number of bathrooms" feature in the case of house price prediction. However, feature extractors can be much more complex and are not limited to structured data, in fact any operation on any type of data that returns a number (`IntFeature` or `FloatFeature`) or a string (`CatFeature`) can be a feature extractor. A feature can be an outlier score of a vector or image, it can be the sharpness of an image, it can be the amount of missing data in a time series, it can be a metric for model output quality, etc... Feature extractors are implemented in `rdv.extractors.*` modules. If there is no suitable feature extractor for your needs, you can [easliy plug in your own]()!

### Bulding a schema
When building a schema given a set of data, the data is processed by the feature extractors resulting in a set of feature values for every feature extractor. These values will then be analysed and statistics will be stored in the `Feature.stats` object. The relavent statistics depend on the type of the feature. For numeric features (int or float), a `NumericStats` object tracks the `min`, `max`, `mean`, `std` and `percentiles` of the observed values. For categorical values (strings), a `CategoricStats` object will track their domain and value frequencies. 

## Summary
In summary, a `Schema` consists of possibly many `Feature`s, that can be of type `int` (`IntFeature`), `float` (`FloatFeature`) or `str` (`CatFeature`). Features are the output of `FeatureExtractors`, which are any function that ingest data and return a value (numeric or categoric). The schema stores distribution statistics for each of those features in their `stats` property and uses these stats to validate incoming data and compare schemas with each other.
