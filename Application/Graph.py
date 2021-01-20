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
from math import exp
from os import makedirs, path
from pandas import DataFrame, concat

# could have main graph class, then subclass for graph type
class Graph:
    def __init__(self, agents, cohesion, graph_type, seed):
        self.default_colour = '#CCCCCC'
        self.generate_graph(agents, cohesion, graph_type, seed)

    def generate_graph(self, agents, cohesion, graph_type, seed):
        num_of_nodes = len(agents.index)
        dataframe_as_dict_of_dicts = agents.set_index(agents.index).to_dict("index)")
        # place switch for graph_type here
        self.graph = nx.erdos_renyi_graph(n=num_of_nodes, p=cohesion, seed=seed)
        nx.set_node_attributes(self.graph, dataframe_as_dict_of_dicts)

        def add_extra_node_attributes(self):
            # Attribute that allows us to restrict incrementation of recovery to once per iteration per agent
            able_to_recover = dict.fromkeys(self.graph.nodes, False)
            nx.set_node_attributes(
                self.graph, name="able_to_recover", values=able_to_recover
            )

            # Attribute representing colour of the node, indicated in time via their condition (health)
            node_colours = dict.fromkeys(self.graph.nodes, self.default_colour)
            nx.set_node_attributes(self.graph, name="node_colour", values=node_colours)
            # Attribute representing the alpha of the node's colour, indicated in time via their condition (financial)
            node_alphas = dict.fromkeys(self.graph.nodes, 1.0)
            nx.set_node_attributes(
                self.graph, name="financial_indicator", values=node_alphas
            )
            node_hatch_patterns = dict.fromkeys(self.graph.nodes, "blank")
            nx.set_node_attributes(
                self.graph, name="hatch_pattern", values=node_hatch_patterns
            )
        
        def add_extra_edge_attributes(self):
            edge_colours = dict.fromkeys(self.graph.edges, self.default_colour)
            nx.set_edge_attributes(self.graph, name="edge_colour", values=edge_colours)

        add_extra_node_attributes(self)
        add_extra_edge_attributes(self)
        self.scale_node_size_to_model()

    def scale_node_size_to_model(self):
            # Attribute representing degree (number of edges)
            degrees = dict(nx.degree(self.graph))
            min_degree, max_degree = min(degrees.values()), max(degrees.values())
            nx.set_node_attributes(self.graph, name="degree", values=degrees)
            # Attribute representing scaled-up version of degree for enhanced awareness of nodes' visual indicators
            min_node_size, max_node_size = 3.5, 20.0
            node_degree_scale = (max_node_size - min_node_size) / max_degree
            node_sizes = dict(
                [
                    (node, ((node_degree_scale * degree) + min_node_size))
                    for node, degree in nx.degree(self.graph)
                ]
            )
            nx.set_node_attributes(self.graph, name="node_size", values=node_sizes)


    def persist_attributes_between_graphs(self, from_graph):
        updated_attributes = dict(from_graph.nodes(data=True))
        nx.set_node_attributes(self.graph, updated_attributes)
        self.scale_node_size_to_model()

    def update_visual_attributes(self):
        def update_node_fill_colour(condition: str):
            return {
                "susceptible": "#00FF00",
                "infectious": "#FF0000",
                "removed": "#d3d3d3",
            }.get(condition, self.default_colour)

        def update_node_fill_alpha(impact: float):
            if impact == 1.0:
                return 1.0
            elif impact < 1.0 and impact >= 0.8:
                return 0.9
            elif impact < 0.8 and impact >= 0.6:
                return 0.8
            elif impact < 0.6 and impact >= 0.4:
                return 0.7
            elif impact < 0.4 and impact >= 0.2:
                return 0.6
            elif impact < 0.2 and impact >= 0.0:
                return 0.5
            else:
                return 0.25

        # bokeh hatch patterns for glyphs not implemented as of 2.2.3-dev10
        # def update_node_hatch_pattern(status: str):
        #     return {
        #         "none": "blank",
        #         "minor": "blank",
        #         "intermediate": "blank",
        #         "major": "blank",
        #         "critical": "blank",
        #         "bust": "diagonal_cross",
        #     }.get(status, "blank")

        for node in self.graph.nodes:
            self.graph.nodes[node]["node_colour"] = update_node_fill_colour(
                self.graph.nodes[node]["condition"]
            )
            self.graph.nodes[node]["financial_indicator"] = update_node_fill_alpha(
                self.graph.nodes[node]["financial_impact"]
            )
            # self.graph.nodes[node]["hatch_pattern"] = update_node_hatch_pattern(
            #     self.graph.nodes[node]["financial_impact"]
            # )

            

    def compose_and_write_csv_of_graph_data(self, alt_graph, output_path):
        
        assert len(self.graph.nodes) == len(alt_graph.nodes)

        node_attributes = []
        for node in range(0, len(self.graph.nodes)):
            node_attributes.append([self.graph.nodes[node]['degree'], alt_graph.nodes[node]['degree'], self.graph.nodes[node]['condition'], self.graph.nodes[node]['time_exposed'],
            self.graph.nodes[node]['initial_asset_value'], self.graph.nodes[node]['current_asset_value'], self.graph.nodes[node]['financial_impact']])      
        graph_data = DataFrame(node_attributes, columns=['geographic_degree', 'financial_degree', 'condition', 'time_exposed', 'financial_impact', 'initial_asset_value', 'current_asset_value'])
        output_dirs, output_file = path.split(output_path)
        makedirs(output_dirs, exist_ok=True)
        graph_data.to_csv(output_path)


    # def update_financial_status(self, impact: float):
    #     if impact == 1.0:
    #         return "none"
    #     elif impact < 1.0 and impact >= 0.75:
    #         return "minor"
    #     elif impact < 0.75 and impact >= 0.5:
    #         return "intermediate"
    #     elif impact < 0.5 and impact >= 0.25:
    #         return "major"
    #     elif impact < 0.25 and impact >= 0.0:
    #         return "critical"
    #     else:
    #         return "bust"