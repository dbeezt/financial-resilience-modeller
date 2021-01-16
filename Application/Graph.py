import networkx as nx
from bokeh.io import output_file, show, export_png
from bokeh.models import (
    Circle,
    HoverTool,
    PanTool,
    WheelZoomTool,
    SaveTool,
    ResetTool,
    TapTool,
    LabelSet,
    MultiLine,
    Plot,
    Range1d,
    NodesAndLinkedEdges,
    EdgesAndLinkedNodes,
    ColumnDataSource,
)
from bokeh.plotting import from_networkx
from pandas import DataFrame

# could have main graph class, then subclass for graph type
class Graph:
    def __init__(self, agents, cohesion, graph_type, seed):
        self.graph = self.generate_graph(agents, cohesion, graph_type, seed)

    def generate_graph(self, agents, cohesion, graph_type, seed):
        num_of_nodes = len(agents.index)
        dataframe_as_dict_of_dicts = agents.set_index(agents.index).to_dict("index)")
        # place switch for graph_type here
        graph = nx.erdos_renyi_graph(n=num_of_nodes, p=cohesion, seed=seed)
        nx.set_node_attributes(graph, dataframe_as_dict_of_dicts)

        def add_extra_attributes(graph):
            # Attribute that allows us to restrict incrementation of recovery to once per iteration per agent
            able_to_recover = dict.fromkeys(graph.nodes, False)
            nx.set_node_attributes(
                graph, name="able_to_recover", values=able_to_recover
            )
            # Attribute representing degree (number of edges)
            degrees = dict(nx.degree(graph))
            nx.set_node_attributes(graph, name="degree", values=degrees)
            # Attribute representing scaled-up version of degree for enhanced awareness of nodes' visual indicators
            node_sizes = dict(
                [(node, (degree + 5)) for node, degree in nx.degree(graph)]
            )
            nx.set_node_attributes(graph, name="node_size", values=node_sizes)
            # Attribute representing colour of the node, indicated in time via their condition (health)
            node_colours = dict.fromkeys(graph.nodes, "")
            nx.set_node_attributes(graph, name="node_colour", values=node_colours)
            # Attribute representing the alpha of the node's colour, indicated in time via their condition (financial)
            node_alphas = dict.fromkeys(graph.nodes, 1.0)
            nx.set_node_attributes(
                graph, name="financial_indicator", values=node_alphas
            )
            node_hatch_patterns = dict.fromkeys(graph.nodes, "blank")
            nx.set_node_attributes(
                graph, name="hatch_pattern", values=node_hatch_patterns
            )

        add_extra_attributes(graph)

        return graph

    def update_visual_attributes(self):
        def update_node_fill_colour(condition: str):
            return {
                "susceptible": "#00FF00",
                "infectious": "#FF0000",
                "removed": "#808080",
            }.get(condition, "#000000")

        def update_node_fill_alpha(effect: float):
            if effect == 1.0:
                return 1.0
            elif effect < 1.0 and effect >= 0.8:
                return 0.9
            elif effect < 0.8 and effect >= 0.6:
                return 0.8
            elif effect < 0.6 and effect >= 0.4:
                return 0.7
            elif effect < 0.4 and effect >= 0.2:
                return 0.6
            elif effect < 0.2 and effect >= 0.0:
                return 0.5
            else:
                return 0.25

        def update_node_hatch_pattern(status: str):
            return {
                "none": "blank",
                "minor": "blank",
                "intermediate": "blank",
                "major": "blank",
                "critical": "blank",
                "bust": "diagonal_cross",
            }.get(status, "blank")

        for node in self.graph.nodes:
            self.graph.nodes[node]["node_colour"] = update_node_fill_colour(
                self.graph.nodes[node]["condition"]
            )
            financial_impact = (
                self.graph.nodes[node]["current_asset_value"]
                / self.graph.nodes[node]["initial_asset_value"]
            )
            self.graph.nodes[node]["financial_indicator"] = update_node_fill_alpha(
                financial_impact
            )
            self.graph.nodes[node]["hatch_pattern"] = update_node_hatch_pattern(
                self.graph.nodes[node]["financial_impact"]
            )
