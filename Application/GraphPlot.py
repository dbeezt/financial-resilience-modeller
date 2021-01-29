import os
import bokeh.io
import bokeh.models
import bokeh.plotting
import platform
import chromedriver_autoinstaller
import geckodriver_autoinstaller

class GraphPlot:
    def __init__(self, title, graph, coords, export_path):
        self.title = title
        self.width, self.height = 800, 532
        self.graph = graph
        self.coords = coords
        self.export_path = export_path
        self.plot = self.create_plot()
        chromedriver_autoinstaller.install(cwd=True)
        geckodriver_autoinstaller.install(cwd=True)

    def create_plot(self, interactive=False):
        base_plot = bokeh.models.Plot(
            plot_width=self.width,
            plot_height=self.height,
            x_range=bokeh.models.Range1d(-1.125, 1.125),
            y_range=bokeh.models.Range1d(-1.05, 1.05),
            min_border=0,
            outline_line_width=0.0,
            sizing_mode="fixed",
        )
        base_plot.title.text = self.title
        base_plot.title.align = "center"

        if interactive:
            # sizing mode dynamic goes here
            node_hover_tool = bokeh.models.HoverTool(
                tooltips=[
                    ("Index", "@index"),
                    ("Time Exposed", "@time_exposed"),
                    ("Financial Impact", "@financial_impact"),
                ],
                show_arrow=False,
                point_policy="follow_mouse",
            )
            base_plot.add_tools(
                node_hover_tool, bokeh.models.PanTool(), bokeh.models.WheelZoomTool(), bokeh.models.SaveTool(), bokeh.models.ResetTool()
            )
            base_plot.toolbar.active_scroll = base_plot.select_one(bokeh.models.WheelZoomTool)
        else:
            base_plot.toolbar_location = None

        return base_plot

    def create_graph_renderer(self, interactive=False):
        # maybe replace this first coords with nx.spring_layout?
        graph_renderer = bokeh.plotting.from_networkx(
            self.graph.graph, self.coords, scale=1, center=(0, 0), pos=self.coords
        )
        graph_renderer.node_renderer.glyph = bokeh.models.Circle(
            size="node_size", fill_color="node_colour", fill_alpha="financial_impact"
        )
        graph_renderer.edge_renderer.glyph = bokeh.models.MultiLine(
            line_color="edge_colour", line_alpha=0.66, line_width=0.75
        )

        if interactive:
            # Style static, hoverable and selectable Nodes
            hover_colour = "orange"
            graph_renderer.node_renderer.selection_glyph = bokeh.models.Circle(
                size="node_size",
                fill_color=hover_colour,
                fill_alpha="financial_impact",
            )
            graph_renderer.node_renderer.hover_glyph = bokeh.models.Circle(
                size="node_size",
                fill_color=hover_colour,
                fill_alpha="financial_impact",
            )
            graph_renderer.node_renderer.glyph.properties_with_values()

            # Style static, hoverable and selectable Edges
            graph_renderer.edge_renderer.selection_glyph = bokeh.models.MultiLine(
                line_color=hover_colour, line_width=3
            )
            graph_renderer.edge_renderer.hover_glyph = bokeh.models.MultiLine(
                line_color=hover_colour, line_width=3
            )

            graph_renderer.selection_policy = bokeh.models.NodesAndLinkedEdges()
            graph_renderer.inspection_policy = bokeh.models.NodesAndLinkedEdges()

        return graph_renderer

    def export_plot(self, graph_renderer):
        self.plot.renderers.append(graph_renderer)
        dirs, _ = os.path.split(self.export_path)
        os.makedirs(dirs, exist_ok=True)
        bokeh.io.export_png(self.plot, filename=self.export_path)


    def render_and_export_graph(self):
        self.graph.update_visual_attributes()
        graph_renderer = self.create_graph_renderer()
        self.export_plot(graph_renderer=graph_renderer)
