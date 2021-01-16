from collections import Counter
from PIL import Image
from os import makedirs
from time import strftime
from .Agents import AgentPopulation
from .Graph import Graph
from .Plotter import Plotter
import glob, random
import networkx as nx


class Model:
    def __init__(self, output_dir: str, options, mode: str = "automatic"):
        # reason for not putting datetime here would be to facilitate manual mode
        self.output_dir = output_dir
        self.graphml_export_path = f"{self.output_dir}/graphs"
        self.plot_export_path = f"{self.output_dir}/plots"
        self.stats_export_path = f"{self.output_dir}/stats"
        self.condition_count_per_iteration = []
        self.financial_impact_count_per_iteration = []
        self.enforce_input_value_data_types(options)

    def enforce_input_value_data_types(self, options):
        self.total_agents = int(options[0][0])
        self.model_cycles = int(options[0][1])
        self.graph_type = str(options[0][2])
        self.seed = int(options[0][3])

        self.pandemic_cohesion = float(options[1][0])
        self.pandemic_iterations = int(options[1][1])
        self.pandemic_transmission_rate = float(options[1][2])
        self.pandemic_time_to_recover = int(options[1][3])

        self.financial_cohesion = float(options[2][0])
        self.financial_iterations = int(options[2][1])
        self.financial_lockdown_severity = float(options[2][2])
        self.financial_loan_threshold = float(options[2][3])

    def auto_run(self):
        agents = AgentPopulation(self.total_agents).data
        pandemic = Graph(agents, self.pandemic_cohesion, self.graph_type, self.seed)
        self.condition_count_per_iteration.append(
            self.sum_agent_attributes(pandemic.graph.nodes.data("condition"))
        )
        financial = Graph(
            agents, self.financial_cohesion, self.graph_type, self.seed + 1
        )
        self.financial_impact_count_per_iteration.append(
            self.sum_agent_attributes(financial.graph.nodes.data("financial_impact"))
        )

        node_positions = nx.spring_layout(pandemic.graph, k=0.5, seed=self.seed)
        Plotter(
            title=f"PANDEMIC MODEL: Cycle 0.0",
            graph=pandemic,
            coords=node_positions,
            export_path=f"{self.plot_export_path}/pandemic/{strftime('%H:%M:%S')}-0.0.png",
        ).render_and_export_plot()
        Plotter(
            title=f"FINANCIAL MODEL: Cycle 0.0",
            graph=financial,
            coords=node_positions,
            export_path=f"{self.plot_export_path}/financial/{strftime('%H:%M:%S')}-0.0.png",
        ).render_and_export_plot()

        for cycle in range(0, self.model_cycles):
            print(f"Cycle #{cycle + 1}")
            self.latest_run_time = strftime("%H:%M:%S")
            for iteration in range(0, self.pandemic_iterations):
                print(f"  Pandemic Iteration #{iteration + 1}")
                pandemic.graph = self.run_pandemic_model(
                    pandemic.graph,
                    self.pandemic_transmission_rate,
                    self.pandemic_time_to_recover,
                )
                Plotter(
                    title=f"PANDEMIC MODEL: Cycle {cycle + 1}.{iteration + 1}",
                    graph=pandemic,
                    coords=node_positions,
                    export_path=self.concat_plot_write_path(
                        "pandemic", cycle + 1, iteration + 1
                    ),
                ).render_and_export_plot()
                self.write_graph_to_graphml(
                    pandemic.graph, "pandemic", cycle + 1, iteration + 1
                )
            self.condition_count_per_iteration.append(
                self.sum_agent_attributes(pandemic.graph.nodes.data("condition"))
            )
            for iteration in range(0, self.financial_iterations):
                self.current_iteration = iteration + 1
                print(f"  Financial Iteration #{iteration + 1}")
                financial.graph = self.run_financial_model(
                    financial.graph,
                    self.financial_lockdown_severity,
                    self.financial_loan_threshold,
                )
                Plotter(
                    title=f"FINANCIAL MODEL: Cycle {cycle + 1}.{iteration + 1}",
                    graph=financial,
                    coords=node_positions,
                    export_path=self.concat_plot_write_path(
                        "financial", cycle + 1, iteration + 1
                    ),
                ).render_and_export_plot()
                self.write_graph_to_graphml(
                    financial.graph, "financial", cycle + 1, iteration + 1
                )
                self.financial_impact_count_per_iteration.append(
                    self.sum_agent_attributes(
                        financial.graph.nodes.data("financial_impact")
                    )
                )
            self.latest_pandemic_gif = self.compose_gif_from_pngs(
                f"{self.plot_export_path}/pandemic"
            )
            self.latest_financial_gif = self.compose_gif_from_pngs(
                f"{self.plot_export_path}/financial"
            )

    def concat_plot_write_path(self, model, cycle, iteration):
        return f"{self.plot_export_path}/{model}/{self.latest_run_time}-{cycle}.{iteration}.png"

    def write_graph_to_graphml(self, graph, model, cycle, iteration):
        graphml_dir_path = f"{self.graphml_export_path}/{model}"
        makedirs(graphml_dir_path, exist_ok=True)
        graphml_file_path = (
            f"{graphml_dir_path}/{self.latest_run_time}-{cycle}.{iteration}.graphml"
        )
        nx.write_graphml(G=graph, path=graphml_file_path)

    def compose_gif_from_pngs(self, path_to_images: str):
        files_in = f"{path_to_images}/*.png"
        file_out = f"{path_to_images}.gif"

        img, *imgs = [Image.open(file) for file in sorted(glob.glob(files_in))]
        img.save(
            fp=file_out,
            format="GIF",
            append_images=imgs,
            save_all=True,
            duration=400,
            loop=0,
        )
        return file_out

    def sum_agent_attributes(self, attribute):
        condition_counter = Counter([y for (x, y) in attribute])
        return condition_counter

    def run_pandemic_model(self, graph, transmission_rate, time_to_recover):
        transmission_rate, time_to_recover = transmission_rate, time_to_recover
        time_before_becoming_contagious = int(round(time_to_recover / 5))
        agent_population: int = len(graph.nodes)
        graph.add_nodes_from(graph.nodes, able_to_recover=True)
        for agent in range(0, agent_population):
            for edge in graph.edges(agent):
                (source_node, target_node) = edge
                if graph.nodes[source_node]["time_exposed"] > time_to_recover:
                    graph.nodes[source_node]["condition"] = "removed"
                    graph.nodes[source_node]["able_to_recover"] = False
                if graph.nodes[source_node]["condition"] == "infectious":
                    # var. show to time before becoming infectious to others
                    if (
                        graph.nodes[source_node]["time_exposed"]
                        > time_before_becoming_contagious
                    ):
                        if graph.nodes[target_node]["condition"] == "susceptible":
                            # Initialise random generator for repeatable results
                            random.seed(1)
                            chance_of_transmission = round(random.random(), 2)
                            # could put nice inline if here TRUE if >= 0.00
                            # chance_of_transmission = pandemic_transmission_rate - chance_of_transmission
                            # print(f"{graph.nodes[target_node]['location']}'s chance to be infected is {chance_of_transmission}")
                            if transmission_rate - chance_of_transmission >= 0.00:
                                # print(f"{graph.nodes[source_node]['location']} infected {graph.nodes[target_node]['location']}")
                                graph.nodes[target_node]["condition"] = "infectious"
                                graph.nodes[target_node]["able_to_recover"] = False
                    # print(f"{graph.nodes[source_node]['location']} is able to recover: {graph.nodes[source_node]['able_to_recover']}")
                    if graph.nodes[source_node]["able_to_recover"]:
                        # print(f"{graph.nodes[source_node]['location']} recovered, now at {graph.nodes[source_node]['time_exposed']}")
                        time_exposed = graph.nodes[source_node]["time_exposed"]
                        graph.nodes[source_node]["time_exposed"] = time_exposed + 1
                        graph.nodes[source_node]["able_to_recover"] = False
        return graph

    def run_financial_model(self, graph, lockdown_severity, loan_threshold):
        lockdown_severity, loan_threshold = lockdown_severity, loan_threshold
        agent_population = len(graph.nodes)
        for agent in range(0, agent_population):
            if graph.nodes[agent]["financial_impact"] != "bust":
                if (
                    graph.nodes[agent]["condition"] == "infectious"
                    and graph.nodes[agent]["time_exposed"] > 1
                ):
                    # asset value should be float to 2 points
                    # multiply this by number of degrees?
                    reduced_asset_value = (
                        graph.nodes[agent]["initial_asset_value"] * lockdown_severity
                    )
                    graph.nodes[agent]["current_asset_value"] = (
                        graph.nodes[agent]["current_asset_value"] - reduced_asset_value
                    )
                for edge in graph.edges(agent):
                    (source_node, target_node) = edge
                    neighbour_current_asset_value = graph.nodes[target_node][
                        "current_asset_value"
                    ]
                    neighbour_loan_threshold = (
                        graph.nodes[target_node]["initial_asset_value"] / loan_threshold
                    )
                    if (
                        neighbour_current_asset_value >= neighbour_loan_threshold
                        and graph.nodes[target_node]["financial_impact"] != "critical"
                    ):
                        if graph.nodes[source_node]["current_asset_value"] < 0:
                            source_node_bail_out_amount = graph.nodes[source_node][
                                "current_asset_value"
                            ]
                            if source_node_bail_out_amount <= neighbour_loan_threshold:
                                graph.nodes[source_node][
                                    "current_asset_value"
                                ] += source_node_bail_out_amount
                # aka go bust
                if graph.nodes[source_node]["current_asset_value"] < 0:
                    # do something e.g. revoke loans
                    graph.nodes[source_node]["financial_impact"] = "bust"
                else:
                    # prob dont need the above if, as this should cater to it
                    financial_damage = (
                        graph.nodes[source_node]["current_asset_value"]
                        / graph.nodes[source_node]["initial_asset_value"]
                    )
                    graph.nodes[source_node][
                        "financial_impact"
                    ] = self.update_financial_status(financial_damage)
        return graph

    def update_financial_status(self, impact: float):
        if impact == 1.0:
            return "none"
        elif impact < 1.0 and impact >= 0.75:
            return "minor"
        elif impact < 0.75 and impact >= 0.5:
            return "intermediate"
        elif impact < 0.5 and impact >= 0.25:
            return "major"
        elif impact < 0.25 and impact >= 0.0:
            return "critical"
        else:
            return "bust"