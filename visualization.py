import random
import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pyvis.network import Network
from config import config
from sklearn import preprocessing

import plotly.io as pio

pio.renderers.default = "browser"


def scaler(x, min, max):
    if isinstance(x, list):
        x = np.array(x)
    x_std = (x - x.min()) / (x.max() - x.min())
    x_scaled = x_std * (max - min) + min
    return x_scaled


edges = pd.read_csv(r"edges.csv")
nodes = pd.read_csv(r"nodes.csv")

G = nx.from_pandas_edgelist(edges.loc[:100], source="source", target="target", edge_attr="weight")
pos = nx.spring_layout(G, k=5, seed=42)
nx.set_node_attributes(G, pos, "pos")
nx.set_node_attributes(
    G=G,
    values=pd.Series(nodes["name"].to_list(), index=nodes["id"]).to_dict(),
    name="name"
)
nx.set_node_attributes(
    G=G,
    values=pd.Series(nodes["h_index"].to_list(), index=nodes["id"]).to_dict(),
    name="h_index"
)
nx.set_node_attributes(
    G=G,
    values=pd.Series(nodes["organization_name"].to_list(), index=nodes["id"]).to_dict(),
    name="organization_name"
)
nx.set_node_attributes(
    G=G,
    values=pd.Series(nodes["publication_num"].to_list(), index=nodes["id"]).to_dict(),
    name="publication_num"
)

edge_x = [[G.nodes[edge[0]]["pos"][0], G.nodes[edge[1]]["pos"][0], None] for edge in G.edges()]
edge_y = [[G.nodes[edge[0]]["pos"][1], G.nodes[edge[1]]["pos"][1], None] for edge in G.edges()]

link_size = edges["weight"].to_numpy()
link_size = scaler(link_size, 0.5, 15)
edge_traces = {}
for i in range(0, len(edge_x)):
    edge_traces["trace_" + str(i)] = go.Scatter(
        x=edge_x[i],
        y=edge_y[i],
        line=dict(width=link_size[i], color="#888"),
        mode="lines"
    )
edge_traces = list(edge_traces.values())

node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]["pos"]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='h-index',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_color = []
node_size = []
node_text = []
for node_values in G.nodes.values():
    node_color.append(node_values['organization_name'])
    node_size.append(node_values['h_index'])
    node_text.append(
        f"<b>Name:</b> {node_values['name']}<br>"
        f"<b>h-index:</b> {node_values['h_index']}<br>"
        f"<b>Organization:</b> {node_values['organization_name']}"

    )
label_encoder = preprocessing.LabelEncoder()
node_color = label_encoder.fit_transform(node_color)

node_trace.marker.size = scaler(node_size, 10, 50)
node_trace.marker.line = dict(color='Black', width=2)
random.seed(40)
unique_colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in
                 range(len(np.unique(node_color)))]
node_color = [unique_colors[i] for i in node_color]
node_trace.marker.color = node_color
node_trace.text = node_text

fig = go.Figure(
    data=edge_traces + [node_trace],
    layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
)

fig.show()
import igviz as ig

ig.plot()
# net = Network(select_menu=True, filter_menu=True)
# net.from_nx(G)
# net.set_options(config)
# net.show("network.html", local=False) # TODO: how to save "html" without opening the browser?
