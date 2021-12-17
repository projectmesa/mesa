from mesa.space import MultiGrid
from mesa import Model
from mesa.time import RandomActivation
import numpy as np
from .agents import BarCustomer
from .agents import BarCustomerIBLT
from mesa.datacollection import DataCollector


class ElFarolBar(Model):
    def __init__(
        self,
        crowdthreshold=60,
        num_strategies=10,
        memory_size=10,
        width=100,
        height=100,
        N=100,
    ):
        self.running = True
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.history = np.random.randint(0, 100, size=memory_size * 2).tolist()
        self.attendance = self.history[-1]
        strategies = np.random.rand(num_strategies, memory_size + 1, N) * 2 - 1
        for i in range(self.num_agents):
            a = BarCustomer(i, self, memory_size, crowdthreshold, strategies[:, :, i])
            self.schedule.add(a)
        self.datacollector = DataCollector(
            model_reporters={"Customers": "attendance"},
            agent_reporters={"Utility": "utility", "Attendance": "attend"},
        )

    def step(self):
        self.datacollector.collect(self)
        self.attendance = 0
        self.schedule.step()
        self.history.pop(0)
        self.history.append(self.attendance)
        for agent in self.schedule.agent_buffer(shuffled=False):
            agent.update_strategies()


class ElFarolBarIBLT(Model):
    def __init__(
        self,
        crowdthreshold=60,
        decay={1: 1},
        memory_size=10,
        width=100,
        height=100,
        N=100,
    ):
        self.running = True
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.history = np.random.randint(0, 100, size=memory_size * 2).tolist()
        self.attendance = self.history[0]
        i = 0
        for d, portion in decay.items():
            for _ in range(int(self.num_agents * portion)):
                a = BarCustomerIBLT(i, self, d, crowdthreshold)
                self.schedule.add(a)
                i += 1
        self.datacollector = DataCollector(
            model_reporters={"Customers": "attendance"},
            agent_reporters={
                "Utility": "utility",
                "Decay": "decay",
                "Attendance": "attend",
            },
        )

    def step(self):
        self.datacollector.collect(self)
        self.attendance = 0
        self.schedule.step()
        self.history.pop(0)

        self.history.append(self.attendance)
        for agent in self.schedule.agent_buffer(shuffled=False):
            agent.update_strategies()
