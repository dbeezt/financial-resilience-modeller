import pandas

class AgentPopulation:
    """
    A class to represent a collective population of agents.

    Attributes
    ----------
    agents : DataFrame
        population of agents where each row represents an agent,
        and each column represents an attribute of said agent
        for later conversion to a dict_of_dicts for
        ingestion into model graphs

    Methods
    -------
    setup_agent_population(num_of_agents):
        Creates a DataFrame with columns representing agent attributes,
        and subsequently populates them with default values.

    introduce_infected_agents(infected_agents):
        Integrates a specified number of infectious agents
        into an existing agent population.
    """

    def __init__(self, num_of_agents: int, infected_agents: int):
        """
        Constructs essential attributes for the AgentPopulation object.

        Args:
            num_of_agents (int):
                number of agents to generate (i.e. size of population)
            infected_agents (int):
                number of agents that begin the simulation as 'infectious'
        """
        self.agents = self.setup_agent_population(num_of_agents)
        self.introduce_infected_agents(infected_agents)

    def setup_agent_population(self, num_of_agents: int):
        """
        Creates a DataFrame with columns representing agent attributes,
        and subsequently populates them with default values.

        Args:
            num_of_agents (int):
                number of agents to generate (i.e. size of population)

        Returns:
            agents (DataFrame):
                DataFrame of agents with default-configured attributes
        """
        agents = pandas.DataFrame(
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
        """
        Integrates a specified number of infectious agents
        into an existing agent population.

        Args:
            infected_agents (int):
                number of agents to make infectious
        """
        infected_agent_indices = self.agents.sample(n=infected_agents, random_state=1)
        for agent in range(0, len(infected_agent_indices)):
            infected_agent_index = self.agents.index.get_loc(
                infected_agent_indices.iloc[agent].name
            )
            self.agents.at[infected_agent_index, "condition"] = "infectious"
            self.agents.at[infected_agent_index, "time_exposed"] = 1
