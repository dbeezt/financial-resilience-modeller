from pandas import DataFrame


class AgentPopulation:
    def __init__(self, num_of_agents: int, infected_agents: int):
        self.agents = self.setup_agent_population(num_of_agents)
        self.introduce_infected_agents(infected_agents)

    def setup_agent_population(self, num_of_agents):
        agents = DataFrame(
            index=range(0, num_of_agents),
            columns=[
                "condition",
                "time_exposed",
                "financial_impact",
                "initial_asset_value",
                "current_asset_value",
            ],
        )
        agents["condition"] = "susceptible"
        agents["time_exposed"] = 0
        agents["financial_impact"] = 1.0
        agents["initial_asset_value"] = 100000000.00
        agents["current_asset_value"] = agents["initial_asset_value"]

        return agents

    def introduce_infected_agents(self, infected_agents):
        infected_agent_indices = self.agents.sample(n=infected_agents, random_state=1)
        for agent in range(0, len(infected_agent_indices)):
            infected_agent_index = self.agents.index.get_loc(
                infected_agent_indices.iloc[agent].name
            )
            self.agents.at[infected_agent_index, "condition"] = "infectious"
            self.agents.at[infected_agent_index, "time_exposed"] = 1
