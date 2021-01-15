# %%
# %load_ext autoreload
# %autoreload 2
import pandas as pd
import numpy as np

from pathlib import Path
from pydoc import locate
from rdv.schema import Schema
from rdv.feature import IntFeature, FloatFeature, CategoricFeature, construct_features
from rdv.extractors.structured import ElementExtractor

pd.set_option("display.max_rows", 500)


schema_path = "/Users/kv/Raymon/Code/rdv/examples/houses-cheap-compiled.json"
schema = Schema().load(schema_path)

# %%
for component in schema.components:
    print(component.name)

component = schema.components[1]
# %%
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def get_stat_table(component):
    if isinstance(component, FloatFeature):
        fields = ["min", "max", "mean", "std", "pinv"]
        values = [round(component.stats.to_jcr()[field], 5) for field in fields]
        data = [fields, values]
        table = go.Table(header=dict(values=["Stat", "Value"], align="left"), cells=dict(values=data, align="left"))
        return table
    elif isinstance(component, CategoricFeature):
        fields = ["domain", "pinv"]
        values = [", ".join(component.stats.domain), component.stats.pinv]
        data = [fields, values]

        table = go.Table(header=dict(values=["Stat", "Value"], align="left"), cells=dict(values=data, align="left"))
        return table
    else:
        print(f"Instance of unknown type {type(component)} passed to get_stat_table")


def get_dist_plot(component, name, decimals=2):
    if isinstance(component, FloatFeature):
        stats = component.stats
        edges = np.linspace(start=stats.min, stop=stats.max, num=stats.nbins)

        bin_centers = np.round(np.mean(np.vstack([edges[:-1], edges[1:]]), axis=0), decimals=decimals)
        width = bin_centers[1] - bin_centers[0]

        x = bin_centers
        y = component.stats.hist
        bar = go.Bar(x=x, y=y, name=name, width=width, opacity=0.5)
        return bar

    elif isinstance(component, CategoricFeature):
        x = list(component.stats.domain_counts.keys())
        y = list(component.stats.domain_counts.values())
        bar = go.Bar(x=x, y=y, name=name)
        return bar
    else:
        print(f"Instance of unknown type {type(component)} passed to get_dist_plot")


# fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'table'}, {'type': 'bar'}]])
# fig.add_trace(
#     get_stat_table(component),
#     row=1, col=1
# )
# fig.add_trace(
#     get_dist_plot(component),
#     row=1, col=2
# )

# %%
def show_schema(schema):
    components = schema.components
    nrows = len(components)
    fig = make_subplots(rows=nrows, cols=2, specs=[[{"type": "table"}, {"type": "bar"}]] * nrows)

    for row, component in enumerate(components):
        print(f"Feature: {component.name}, {type(component)}")
        fig.add_trace(get_stat_table(component), row=row + 1, col=1)
        fig.add_trace(get_dist_plot(component), row=row + 1, col=2)
    fig.update_layout(height=200 * nrows, width=800, title_text=f"Schema {schema.name}")
    fig.show()


# show_schema(schema)
# %%

import ipywidgets as ipw
from ipywidgets.embed import embed_minimal_html
import dominate
from dominate.tags import div, h1
from dominate.util import raw


def show_schema_figs(schema):

    components = schema.components
    nrows = len(components)
    figs = [ipw.HTML(f"<h1> Schema {schema.name}</h1>")]

    for row, component in enumerate(components):
        fig = go.FigureWidget(
            make_subplots(rows=1, cols=2, specs=[[{"type": "table"}, {"type": "bar"}]], column_widths=[0.5, 0.5])
        )
        print(f"Feature: {component.name}, {type(component)}")
        fig.add_trace(get_stat_table(component), row=1, col=1)
        fig.add_trace(get_dist_plot(component, name=schema.name), row=1, col=2)
        fig.update_layout(
            height=500,
            width=800,
            title_text=f"Feature {component.name}",
            legend=dict(
                yanchor="top",
                y=0.99,
            ),
        )
        figs.append(fig)

        # fhtml = fig.to_html(full_html=False, include_plotlyjs='cdn')

    vbox = ipw.VBox(figs)
    return vbox


# show_schema_figs(schema)

# %%
def components_equal(csa, csb):
    for ca, cb in zip(csa, csb):
        if ca.name != cb.name:
            return False
        # TODO: check same domain, min, max etc?
    return True


def compare_schema(schema_a, schema_b):
    # Check schema components
    components_a = sorted(schema_a.components, key=lambda x: x.name)
    components_b = sorted(schema_b.components, key=lambda x: x.name)
    if not components_equal(components_a, components_b):
        raise Exception("Cannot compare schemas with unidentical components")

    components = schema.components
    nrows = len(components)
    figs = [ipw.HTML(f"<h1> Schema {schema_b.name} (left) vs {schema_b.name} (right)</h1>")]

    for row, (comp_a, comp_b) in enumerate(zip(components_a, components_b)):
        fig = go.FigureWidget(
            make_subplots(
                rows=1,
                cols=3,
                specs=[[{"type": "table"}, {"type": "bar"}, {"type": "table"}]],
                column_widths=[0.3, 0.4, 0.3],
            )
        )
        fig.add_trace(get_stat_table(comp_a), row=1, col=1)
        fig.add_trace(get_dist_plot(comp_a, name=schema_a.name), row=1, col=2)
        fig.add_trace(get_dist_plot(comp_b, name=schema_b.name), row=1, col=2)
        fig.add_trace(get_stat_table(comp_b), row=1, col=3)
        fig.update_layout(height=500, width=1400, title_text=f"Feature {comp_a.name}")
        figs.append(fig)

        # fhtml = fig.to_html(full_html=False, include_plotlyjs='cdn')

    vbox = ipw.VBox(figs)
    return vbox


def create_schema(fpath, name):
    all_data = pd.read_csv(fpath).drop(["Id", "SalePrice"], axis="columns")
    components = construct_features(all_data.dtypes)
    schema = Schema(features=components, name=name)
    schema.compile(data=all_data)
    return schema


schema_cheap = create_schema("/Users/kv/Raymon/Code/rdv/examples/subset-cheap.csv", name="training")
schema_exp = create_schema("/Users/kv/Raymon/Code/rdv/examples/subset-exp.csv", name="prod")

vis = compare_schema(schema_a=schema_cheap, schema_b=schema_exp)
embed_minimal_html("export.html", views=[vis], title="Schema comparison export")
#%%
