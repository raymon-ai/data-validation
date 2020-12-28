
# Raymon Data Validation Library
![Build](https://github.com/raymon-ai/data-validation/workflows/build/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<a href="https://github.com/raymon-ai/data-validation/blob/master/LICENSE.md"><img alt="License" src="https://img.shields.io/github/license/raymon-ai/data-validation"></a>
<a href="#"><img alt="PyPI" src="https://img.shields.io/pypi/v/rdv"></a>

## What?

## Why?

## How?
4 concepts are central to how the rdv package works: schema's, components, extractors and stats. They are related as follows.

An **extractor** is simply an object with a function that extracts a metric from a piece of data. For structured data, the most straightforward extractor is one that simply extracts one element from a vector, for example the "number of bathrooms" feature from a feature vector in the case of house price prediction. However, extractors can transform their input data in any way you want and their input data is not limited to structured data. For example, an extractor could extract the total duration of missing data from sensor data, or it could extract the sharpness from an image, the norm of a subvector of an input vector. Moreover, it could operate not only on model input data, but also on model internals,  model outputs, or data not directly linked to a model. Examples for these could be an extractor that extracts the Intersection over Union of different detected objects in an image, object detection 'flicker' over successive frames, a metric for model uncertainty based and the model's internals, etc... Extractors are simply used to extract some kind of metric from your data that can then be tracked to assess your system's health. 

A data **schema** is basically a bunch of extractors, coupled to **statistics** of their output values. This coupling between an extractor and its output stats is done using a schema **component**. Currently there are 2 types of components: Numerical and Categorical components, which type a component should be depends on the output type of the extractor it encapsulates. When building a schema, extractors will transform 

Depending on the output type of an extractor (numeric or categorical)

## Who?
For who vs by who?

## Where
