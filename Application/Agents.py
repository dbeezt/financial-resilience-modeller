from pandas import DataFrame


class AgentPopulation:
    def __init__(self, num_of_agents: int):
        self.data = self.setup_agent_population(num_of_agents)

    def setup_agent_population(self, num_of_agents):
        agents = DataFrame(
            index=range(0, num_of_agents),
            columns=[
                "location",
                "condition",
                "time_exposed",
                "financial_impact",
                "initial_asset_value",
                "current_asset_value",
            ],
        )
        locations = []
        for index in range(0, len(agents)):
            locations.append(f"Bank{index}")

        agents["location"] = locations
        agents["condition"] = "susceptible"
        agents["time_exposed"] = 0
        agents["financial_impact"] = "none"
        agents["initial_asset_value"] = 100000000.00
        agents["current_asset_value"] = agents["initial_asset_value"]

        agent_zero_index = agents.sample(n=1, random_state=1)
        agent_zero_index = agents.index.get_loc(agent_zero_index.iloc[0].name)
        agents.at[agent_zero_index, "condition"] = "infectious"
        agents.at[agent_zero_index, "time_exposed"] = 1

        return agents
