import random

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx

from mesa.space import NetworkGrid


def number_of_nodes_infected(model):
    agents = model.grid.get_all_cell_contents()
    return sum([1 for a in agents if a.infected is True])


class VirusModel(Model):
    """A virus model with some number of agents"""

    def __init__(self, num_nodes=150, avg_node_degree=3, initial_outbreak_size=10, spread_probability=0.3):

        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        self.spread_probability = spread_probability
        self.running = True

        self.datacollector = DataCollector(
            model_reporters={"Nodes_Infected": number_of_nodes_infected},
            agent_reporters={"Infected": lambda _: _.infected}
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(i, self, self.spread_probability, infected=False)
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.infected = True

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class VirusAgent(Agent):
    def __init__(self, unique_id, model, spread_probability, infected=False):
        super().__init__(unique_id, model)
        self.spread_probability = spread_probability
        self.infected = infected

    def infect(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbors = self.model.grid.get_cell_list_contents(neighbors_nodes)
        if len(neighbors) > 0:
            for a in neighbors:
                if random.random() < self.spread_probability:
                    a.infected = True

    def step(self):
        if self.infected:
            self.infect()
