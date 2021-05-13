from mesa import Agent
import pyibl
import random


class BarCustomer(Agent):
    def __init__(self, unique_id, model, memory_size, crowd_threshold, strategies):
        super().__init__(unique_id, model)
        self.strategies = strategies
        self.best_strategy = self.strategies[0]
        self.attend = False
        self.memory_size = memory_size
        self.crowd_threshold = crowd_threshold
        self.utility = 0
        self.update_strategies()

    def step(self):
        prediction = self.predict_attendance(self.best_strategy, self.model.history[-self.memory_size:])
        if prediction <= self.crowd_threshold:
            self.attend = True
            self.model.attendance += 1
        else:
            self.attend = False

    def update_strategies(self):
        best_score = float('inf')
        for strategy in self.strategies:
            score, week = 0, 0
            for _ in range(self.memory_size):
                prediction = self.predict_attendance(strategy, self.model.history[week: week + self.memory_size])
                score = score + abs(self.model.history[week + self.memory_size] - prediction)
                week += 1
            if score <= best_score:
                best_score = score
                self.best_strategy = strategy
        if (self.model.history[-1] > self.crowd_threshold and self.attend) or (self.model.history[-1] < self.crowd_threshold and self.attend is False):
            self.utility -= 1
        else:
            self.utility += 1

    def predict_attendance(self, strategy, subhistory):
        return strategy[0] * 100 + sum(strategy[1:] * subhistory)


class BarCustomerIBLT(Agent):
    def __init__(self, unique_id, model, decay, crowd_threshold):
        super().__init__(unique_id, model)
        self.agent = pyibl.Agent("BarCustomer", ["Attendence"], decay=decay, noise=random.uniform(0.1, 1.5))
        self.agent.default_utility = 10
        self.attend = False
        self.utility = 0
        self.decay = decay
        self.crowd_threshold = crowd_threshold
        self.step()
        self.update_strategies()

    def step(self):
        choice = self.agent.choose('Attend', 'Not Attend')
        if choice == 'Attend':
            self.attend = True
            self.model.attendance += 1
        else:
            self.attend = False

    def update_strategies(self):
        """
        Update blending value for IBL agent. the if statement is the same as the if statement in BarCustomer agent
        """
        if (self.model.history[-1] > self.crowd_threshold and self.attend) or (self.model.history[-1] < self.crowd_threshold and self.attend is False):
            self.agent.respond(-1)
            self.utility -= 1
        else:
            self.agent.respond(1)
            self.utility += 1
