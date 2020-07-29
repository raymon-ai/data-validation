components = [
    NumericalComponent(extractor=MyComponent(name="yourname", description="")),
    CategoricalComponent(extractor=MyComponent2()),
]

schema = MySchema(components=components)
schema.save(fpath)

# Now load it with the wizard
