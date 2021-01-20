from os import makedirs, path
from bokeh.models import (
    Plot,
    Range1d,
    HoverTool,
    PanTool,
    WheelZoomTool,
    SaveTool,
    ResetTool,
    WheelZoomTool,
    Circle,
    MultiLine,
    NodesAndLinkedEdges,
)
from bokeh.io import export_png
from bokeh.plotting import from_networkx


class GraphPlot:
    def __init__(self, title, graph, coords, export_path):
        self.title = title
        self.width, self.height = 800, 500
        self.graph = graph
        self.coords = coords
        self.export_path = export_path

    def create_plot(self, interactive=False):
        base_plot = Plot(
            plot_width=self.width,
            plot_height=self.height,
            x_range=Range1d(-1.125, 1.125),
            y_range=Range1d(-1.05, 1.05),
            min_border=0,
            outline_line_width=0.0,
            sizing_mode="fixed",
        )
        base_plot.title.text = self.title
        base_plot.title.align = "center"

        if interactive:
            # sizing mode dynamic goes here
            node_hover_tool = HoverTool(
                tooltips=[
                    ("Index", "@index"),
                    ("Time Exposed", "@time_exposed"),
                    ("Financial Impact", "@financial_impact"),
                ],
                show_arrow=False,
                point_policy="follow_mouse",
            )
            base_plot.add_tools(
                node_hover_tool, PanTool(), WheelZoomTool(), SaveTool(), ResetTool()
            )
            base_plot.toolbar.active_scroll = plot.select_one(WheelZoomTool)
        else:
            base_plot.toolbar_location = None

        return base_plot

    def create_graph_renderer(self, interactive=False):
        # maybe replace this first coords with nx.spring_layout?
        graph_renderer = from_networkx(
            self.graph.graph, self.coords, scale=1, center=(0, 0), pos=self.coords
        )
        graph_renderer.node_renderer.glyph = Circle(
            size="node_size", fill_color="node_colour", fill_alpha="financial_impact"
        )
        graph_renderer.edge_renderer.glyph = MultiLine(
            line_color="edge_colour", line_alpha=0.66, line_width=0.75
        )

        if interactive:
            # Style static, hoverable and selectable Nodes
            hover_colour = "orange"
            graph_renderer.node_renderer.selection_glyph = Circle(
                size="node_size",
                fill_color=hover_colour,
                fill_alpha="financial_impact",
            )
            graph_renderer.node_renderer.hover_glyph = Circle(
                size="node_size",
                fill_color=hover_colour,
                fill_alpha="financial_impact",
            )
            graph_renderer.node_renderer.glyph.properties_with_values()

            # Style static, hoverable and selectable Edges
            graph_renderer.edge_renderer.selection_glyph = MultiLine(
                line_color=hover_colour, line_width=3
            )
            graph_renderer.edge_renderer.hover_glyph = MultiLine(
                line_color=hover_colour, line_width=3
            )

            graph_renderer.selection_policy = NodesAndLinkedEdges()
            graph_renderer.inspection_policy = NodesAndLinkedEdges()

        return graph_renderer

    def export_plot(self, graph_renderer):
        self.plot.renderers.append(graph_renderer)
        dirs, file = path.split(self.export_path)
        makedirs(dirs, exist_ok=True)
        export_png(self.plot, filename=self.export_path)

    def render_and_export_graph(self):
        self.plot = self.create_plot()
        self.graph.update_visual_attributes()
        graph_renderer = self.create_graph_renderer()
        self.export_plot(graph_renderer=graph_renderer)
