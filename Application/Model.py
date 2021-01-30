import collections
import functools
import glob
import math
import operator
import os
import PIL
import random
import time
import networkx as nx
from Agents import AgentPopulation
from Graph import Graph
from GraphPlot import GraphPlot
from DataPlot import DataPlot


class Model:
    def __init__(self, output_dir: str, options, log = '', mode: str = "automatic"):
        # reason for not putting datetime here would be to facilitate manual mode
        # this is generated each time the ne model class is inst'd
        # containts dir name, date, time
        self.output_dir = output_dir
        self.log = log
        # this records the time for cycle starts (i think)
        self.latest_run_time = time.strftime("%H:%M:%S")
        self.create_datetime_output_dir()
        self.save_model_settings_to_txt(options)
        self.enforce_input_value_data_types(options)
    
    def print_to_log(self, message):
        if self.log:
            self.log.insert('end', f"{message}\n")

    def create_datetime_output_dir(self):
        os.makedirs(self.output_dir , exist_ok=True)
   
    def save_model_settings_to_txt(self, options):
        option_list_names = ['Compound Settings', 'Pandemic Settings', 'Financial Settings']
        compound_setting_names = ['Total Agents', 'No. Cycles', 'Graph Type', 'Random Seed']
        pandemic_setting_names = ['Geographic Cohesion', 'No. Iterations', 'Ease of Transmission', 'Time to Recover']
        financial_setting_names = ['Financial Cohesion', 'No. Iterations', 'Lockdown Severity', 'Loan Threshold']
        all_setting_names = [compound_setting_names, pandemic_setting_names, financial_setting_names]
        with open(f"{self.output_dir}/model_variables.txt", 'w') as txt_file:
            txt_file.write("COMPOUND PANDEMIC/FINANCIAL MODEL\n")
            txt_file.write("---------------------------------\n")
            for option_list in range(0, len(option_list_names)):
                txt_file.write(f"\n{option_list_names[option_list]}\n")
                txt_file.write("-----------------\n\n")
                for option in range(0, len(options[option_list])):
                    txt_file.write(f"{all_setting_names[option_list][option]}: {options[option_list][option]}\n")

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
        txt_export_path = self.output_dir
        graphml_export_path = f"{self.output_dir}/graphs"
        plot_export_path = f"{self.output_dir}/plots"
        stats_export_path = f"{self.output_dir}/stats"
        condition_count_per_iteration = []
        financial_impact_count_per_iteration = []
        
        # if we persist the attribute values of node sizes, it means
        # either financial uses node (degree) sizes of pandemic of vice versa
        # would we rather see node size represented by geographic or financial significance?
        # infected_agents = math.floor(self.total_agents/50)
        infected_agents = 1
        agents = AgentPopulation(self.total_agents, infected_agents).agents
        pandemic = Graph(agents, self.pandemic_cohesion, self.graph_type, self.seed)
        condition_count_per_iteration.append(
            self.sum_agent_attributes(pandemic.graph.nodes.data("condition"))
        )
        financial = Graph(
            agents, self.financial_cohesion, self.graph_type, self.seed + 1
        )
        financial.persist_attributes_between_graphs(pandemic.graph)
        financial_impact_count_per_iteration.append(
            self.sum_agent_attributes(financial.graph.nodes.data("financial_impact"))
        )
        self.print_to_log(f"    State: {self.sum_agent_attributes(pandemic.graph.nodes.data('condition'))}")
        self.print_to_log(f"    Impact: {self.sum_agent_attributes(pandemic.graph.nodes.data('financial_status'))}")

        node_positions = nx.spring_layout(pandemic.graph, k=0.5, seed=self.seed)
        GraphPlot(
            title="PANDEMIC MODEL: Cycle 0.0",
            graph=pandemic,
            coords=node_positions,
            export_path=self.concat_plot_write_path(plot_export_path, "network", "pandemic", 0, 0),
        ).render_and_export_graph()
        GraphPlot(
            title="FINANCIAL MODEL: Cycle 0.0",
            graph=financial, 
            coords=node_positions,
            export_path=self.concat_plot_write_path(plot_export_path, "network", "financial", 0, 0),
        ).render_and_export_graph()
        pandemic.compose_and_write_csv_of_graph_data(
            alt_graph=financial.graph, output_path=self.concat_csv_write_path(stats_export_path, 0, 0)
        )

        for cycle in range(0, self.model_cycles):
            # Used for generating iterative seed when performing random interaction checks
            self.cycle = cycle
            # formata these L's in prin to logs
            self.print_to_log(f"    Cycle #{cycle + 1}")
            print(f"Cycle #{cycle + 1}")
            self.latest_run_time = time.strftime("%H:%M:%S")          
            for iteration in range(0, self.pandemic_iterations):
                print(f"  Pandemic Iteration #{cycle + 1}.{iteration + 1}")
                pandemic.persist_attributes_between_graphs(financial.graph)
                pandemic.graph = self.run_pandemic_model(
                    pandemic.graph,
                    self.pandemic_transmission_rate,
                    self.pandemic_time_to_recover,
                )

                GraphPlot(
                    title=f"PANDEMIC MODEL: Cycle {cycle + 1}.{iteration + 1}",
                    graph=pandemic,
                    coords=node_positions,
                    export_path=self.concat_plot_write_path(
                        plot_export_path, "network", "pandemic", cycle + 1, iteration + 1
                    ),
                ).render_and_export_graph()
                self.write_graph_to_graphml(
                    pandemic.graph, graphml_export_path, "pandemic", cycle + 1, iteration + 1
                )
            condition_count_per_iteration.append(
                self.sum_agent_attributes(pandemic.graph.nodes.data("condition"))
            )
            self.print_to_log(f"    State: {self.sum_agent_attributes(pandemic.graph.nodes.data('condition'))}")
            for iteration in range(0, self.financial_iterations):
                self.current_iteration = iteration + 1
                print(f"  Financial Iteration #{cycle + 1}.{iteration + 1}")
                financial.persist_attributes_between_graphs(pandemic.graph)
                financial.graph = self.run_financial_model(
                    financial.graph,
                    self.financial_lockdown_severity,
                    self.financial_loan_threshold,
                )
                GraphPlot(
                    title=f"FINANCIAL MODEL: Cycle {cycle + 1}.{iteration + 1}",
                    graph=financial,
                    coords=node_positions,
                    export_path=self.concat_plot_write_path(
                        plot_export_path, "network", "financial", cycle + 1, iteration + 1
                    ),
                ).render_and_export_graph()
                self.write_graph_to_graphml(
                    financial.graph, graphml_export_path, "financial", cycle + 1, iteration + 1
                )
                financial_impact_count_per_iteration.append(
                    self.sum_agent_attributes(
                        financial.graph.nodes.data("financial_impact")
                    )
                )
            self.print_to_log(f"    Impact: {self.sum_agent_attributes(pandemic.graph.nodes.data('financial_status'))}")
            pandemic.compose_and_write_csv_of_graph_data(
                alt_graph=financial.graph,
                output_path=self.concat_csv_write_path(stats_export_path, cycle + 1, iteration + 1),
            )
            # f"{graphml_dir_path}/{self.latest_run_time}-{cycle}.{iteration}.graphml"

        self.latest_pandemic_gif = self.compose_gif_from_pngs(
            f"{plot_export_path}/network/pandemic"
        )
        self.latest_financial_gif = self.compose_gif_from_pngs(
            f"{plot_export_path}/network/financial"
        )

        # data_plot = DataPlot(
        #     path_to_data=f"{stats_export_path}/graph/node_attributes",
        #     export_path=f"{plot_export_path}/data",
        # ).create_plot()

    def concat_csv_write_path(self, stats_dir, cycle, iteration):
        return f"{stats_dir}/graph/node_attributes/{self.latest_run_time}-{cycle}.{iteration}.csv"

    def concat_plot_write_path(self, plot_dir, plot, model, cycle, iteration):
        return f"{plot_dir}/{plot}/{model}/{self.latest_run_time}-{cycle}.{iteration}.png"

    def write_graph_to_graphml(self, graph, graphml_dir, model, cycle, iteration):
        graphml_dir_path = f"{graphml_dir}/{model}"
        os.makedirs(graphml_dir_path, exist_ok=True)
        graphml_file_path = (
            f"{graphml_dir_path}/{self.latest_run_time}-{cycle}.{iteration}.graphml"
        )
        nx.write_graphml(G=graph, path=graphml_file_path)


    def compose_gif_from_pngs(self, path_to_images: str):
        def compose_image_grid_from_frames(images):
            columns = 3
            rows = (math.ceil(len(images)/columns))
            width, height = images[0].size
            grid = PIL.Image.new('RGB', size = ((columns * width), (rows * height)), color='#FFFFFF')
            grid_width, grid_height = grid.size

            for x, image in enumerate(images):
                box = (((x % columns) * width), ((x // columns) * height))
                grid.paste(image, box = box)
            return grid
        
        frames_in = f"{path_to_images}/*.png"
        gif_out = f"{path_to_images}/model.gif"

        frame_zero, *frames = [PIL.Image.open(file) for file in sorted(glob.glob(frames_in))]
        frame_zero.save(
            fp=gif_out,
            format="GIF",
            append_images=frames,
            save_all=True,
            duration=600,
            loop=0,
        )

        grid_out = f"{path_to_images}/grid.png"
        grid = compose_image_grid_from_frames(images = [frame_zero, *frames])
        grid.save(
            fp=grid_out,
            format='PNG'
        )

        return gif_out


    def sum_agent_attributes(self, attribute):
        counter = collections.Counter([y for (x, y) in attribute])
        return (sorted(counter.items(), key=operator.itemgetter(0)))


    def run_pandemic_model(self, graph, transmission_rate, time_to_recover):
        def update_edge_fill_colour(condition: str):
            return {
                "susceptible": "#00FF00",
                "infectious": "#FF0000",
                "removed": "#CCCCCC",
            }.get(condition, "#CCCCCC")

        time_before_becoming_contagious = math.ceil(time_to_recover / 5)
        # print(time_before_becoming_contagious)
        agent_population: int = len(graph.nodes)
        graph.add_nodes_from(graph.nodes, able_to_recover=True)
        for agent in range(0, agent_population):
            for edge in graph.edges(agent):
                (source_node, target_node) = edge
                if graph.nodes[source_node]["time_exposed"] > time_to_recover:
                    graph.edges[edge]["edge_colour"] = update_edge_fill_colour(
                        "default"
                    )
                    graph.nodes[source_node]["condition"] = "removed"
                    graph.nodes[source_node]["able_to_recover"] = False
                    # should add blank return here?
                if graph.nodes[source_node]["condition"] == "infectious":
                    # print(graph.nodes[source_node]["time_exposed"])
                    # print(graph.nodes[agent]["able_to_recover"])
                    # var. show to time before becoming infectious to others
                    if (
                        graph.nodes[source_node]["time_exposed"]
                        > time_before_becoming_contagious
                    ):
                        # print(f"{graph.nodes[source_node]['location']}:{graph.nodes[source_node]['condition']}")
                        if graph.nodes[target_node]["condition"] == "susceptible":
                            # print(f"{graph.nodes[target_node]['location']}:{graph.nodes[target_node]['condition']}")
                            # Initialise random generator for repeatable results
                            # This seed is annoying
                            random.seed(self.cycle + target_node)
                            chance_of_transmission = round(random.random(), 2)
                            # print(f"    Infection will occur if the transmission rate is over {chance_of_transmission}")
                            # could put nice inline if here TRUE if >= 0.00
                            # chance_of_transmission = pandemic_transmission_rate - chance_of_transmission
                            # print(f"{graph.nodes[target_node]['location']}'s chance to be infected is {chance_of_transmission}")
                            # print(chance_of_transmission)
                            if transmission_rate - chance_of_transmission >= 0.00:
                                graph.edges[edge][
                                    "edge_colour"
                                ] = update_edge_fill_colour("infectious")
                                # print(f"{graph.nodes[source_node]['location']} infected {graph.nodes[target_node]['location']}")
                                graph.nodes[target_node]["condition"] = "infectious"
                                graph.nodes[target_node]["able_to_recover"] = False
                    # print(f"{graph.nodes[source_node]['location']} is able to recover: {graph.nodes[source_node]['able_to_recover']}")
                    # print(graph.nodes[agent]["able_to_recover"])
                    if graph.nodes[agent]["able_to_recover"]:
                        # print(f"{graph.nodes[source_node]['location']} recovered, now at {graph.nodes[source_node]['time_exposed']}")
                        time_exposed = graph.nodes[agent]["time_exposed"]
                        graph.nodes[agent]["time_exposed"] = time_exposed + 1
                        graph.nodes[agent]["able_to_recover"] = False

        return graph

    def run_financial_model(self, graph, lockdown_severity, loan_threshold):
        agent_population = len(graph.nodes)
        for agent in range(0, agent_population):
            if graph.nodes[agent]["financial_impact"] != "bust":
                if (
                    graph.nodes[agent]["condition"] == "infectious"
                    and graph.nodes[agent]["time_exposed"] > 1
                ):
                    # print("bank", agent, graph.nodes[agent]["financial_impact"])
                    # asset value should be float to 2 points
                    # multiply this by number of degrees?
                    reduced_asset_value = (
                        graph.nodes[agent]["initial_asset_value"] * lockdown_severity
                    )
                    current_asset_value = graph.nodes[agent]["current_asset_value"]
                    graph.nodes[agent]["current_asset_value"] = (
                        current_asset_value - reduced_asset_value
                    )
                    # print(
                    # f"Node{agent}'s wealth reduced by {reduced_asset_value}, from {current_asset_value} to {graph.nodes[agent]['current_asset_value']}"
                    # )
                for edge in graph.edges(agent):
                    (source_node, target_node) = edge
                    if (
                        graph.nodes[source_node]["financial_impact"] != "bust"
                        and graph.nodes[target_node]["financial_impact"] != "bust"
                    ):
                        neighbour_current_asset_value = graph.nodes[target_node][
                            "current_asset_value"
                        ]
                        neighbour_loan_threshold = (
                            graph.nodes[target_node]["initial_asset_value"]
                            / loan_threshold
                        )
                        if (
                            neighbour_current_asset_value >= neighbour_loan_threshold
                            and graph.nodes[target_node]["financial_impact"]
                            != "critical"
                        ):
                            if graph.nodes[source_node]["current_asset_value"] < 0:
                                source_node_bail_out_amount = graph.nodes[source_node][
                                    "current_asset_value"
                                ]
                                if (
                                    source_node_bail_out_amount
                                    <= neighbour_loan_threshold
                                ):
                                    graph.nodes[source_node][
                                        "current_asset_value"
                                    ] += source_node_bail_out_amount
                        graph.nodes[source_node]["financial_impact"] = (
                            graph.nodes[source_node]["current_asset_value"]
                            / graph.nodes[source_node]["initial_asset_value"]
                        )

                        if graph.nodes[source_node]["financial_impact"] == "bust":
                            print(f"Node {source_node} is bust")
                            # graph.nodes[source_node][
                            #     "financial_impact"
                            # ] = self.update_financial_status(financial_damage)
                        # aka go bust

                        # need to add edge colouration for this model

        return graph
