import random

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class {{cookiecutter.agent}}(Agent):
    """
    An agent with an id
    """

    def __init__(self, unique_id):
        """
        Customize the agent
        """
        self.name = unique_id


    def step(self, model):
        """
        Modify this method to change what an individual agent will do during each step.
        Can include logic based on neighbors states.
        """
        pass


class {{cookiecutter.model}}(Model):
    """
    An agent-based model with a random activation schedule.
    See mesa.time for alternative builtin schedulers.
    """

    def __init__(self, num_agents, width, height):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width=width, height=height, torus=True)

        for i in range(self.num_agents):
            agent = {{cookiecutter.agent}}(i)
            self.schedule.add(agent)

            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # example data collector
        self.datacollector = DataCollector(
            model_reporters={"AgentCounter": lambda m: m.num_agents},
            agent_reporters={"AgentID": lambda a: a.unique_id})


    def step(self):
        """
        A model step. You probably want to consider manipulating some agents here.
        """
        self.datacollector.collect(self)
        self.schedule.step()
