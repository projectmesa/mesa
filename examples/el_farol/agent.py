from mesa import Agent
import pyibl
import random


class BarCustomer(Agent):
    def __init__(self, unique_id, model, memory_size, crowdthreshold, strategies):
        super().__init__(unique_id, model)
        self.strategies = strategies
        self.best_strategy = self.strategies[0]
        self.attend = False
        self.memory_size = memory_size
        self.crowdthreshold = crowdthreshold
        self.utility = 0
        self.update_strategies()

    def step(self):
        prediction = self.predict_attendance(self.best_strategy, self.model.history[-self.memory_size:])
        if prediction <= self.crowdthreshold:
            self.attend = True
            self.model.attendance = self.model.attendance + 1
        else:
            self.attend = False

    def update_strategies(self):
        best_score = float('inf')
        for strategy in self.strategies:
            score, week = 0, 0
            for _ in range(self.memory_size):
                prediction = self.predict_attendance(strategy, self.model.history[week: week + self.memory_size])
                score = score + abs(self.model.history[week + self.memory_size] - prediction)
                week = week + 1
            if score <= best_score:
                best_score = score
                self.best_strategy = strategy
        if (self.model.history[-1] > self.crowdthreshold and self.attend) or (self.model.history[-1] < self.crowdthreshold and self.attend is False):
            self.utility = self.utility - 1
        else:
            self.utility = self.utility + 1

    def predict_attendance(self, strategy, subhistory):
        return strategy[0] * 100 + sum(strategy[1:] * subhistory)


class BarCustomerIBLT(Agent):
    def __init__(self, unique_id, model, decay, crowdthreshold):
        super().__init__(unique_id, model)
        self.agent = pyibl.Agent("BarCustomer", ["Attendence"], decay=decay, noise=random.uniform(0.1, 1.5))
        self.agent.default_utility = 10
        self.attend = False
        self.utility = 0
        self.decay = decay
        self.crowdthreshold = crowdthreshold
        self.step()
        self.update_strategies()

    def step(self):
        choise = self.agent.choose('Attend', 'Not Attend')
        if choise == 'Attend':
            self.attend = True
            self.model.attendance = self.model.attendance + 1
        else:
            self.attend = False

    def update_strategies(self):
        if (self.model.history[-1] > self.crowdthreshold and self.attend) or (self.model.history[-1] < self.crowdthreshold and self.attend is False):
            self.agent.respond(-1)
            self.utility = self.utility - 1
        else:
            self.agent.respond(1)
            self.utility = self.utility + 1
