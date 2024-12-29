import networkx as nx
import numpy as np
from mesa.examples.basic.alliance_formation_model.agents import AllianceAgent

import mesa


class AllianceModel(mesa.Model):
    def __init__(self, n=50, mean=0.5, std_dev=0.1, seed=42):
        super().__init__(seed=seed)
        self.population = n
        self.network = nx.Graph()  # Initialize the network
        self.datacollector = mesa.DataCollector(model_reporters={"Network": "network"})

        # Create Agents
        power = self.rng.normal(mean, std_dev, n)
        power = np.clip(power, 0, 1)
        position = self.rng.normal(mean, std_dev, n)
        position = np.clip(position, 0, 1)
        AllianceAgent.create_agents(self, n, power, position)
        agent_ids = [
            (agent.unique_id, {"size": 300, "hierarchy": 0}) for agent in self.agents
        ]
        self.network.add_nodes_from(agent_ids)

    def add_link(self, meta_agent, agents):
        for agent in agents:
            self.network.add_edge(meta_agent.unique_id, agent.unique_id)

    def step(self):
        for agent_class in list(
            self.agent_types
        ):  # Convert to list to avoid modification during iteration
            self.agents_by_type[agent_class].shuffle_do("form_alliance")

            # Update graph
            if agent_class is not AllianceAgent:
                for meta_agent in self.agents_by_type[agent_class]:
                    self.add_link(meta_agent, meta_agent.agents)
