from mesa import Agent
import numpy as np
class BarCustomer(Agent):
    def __init__(self, unique_id, model,num_strategies,memory_size,crowdthreshold):
        super().__init__(unique_id, model)
        self.strategies = np.zeros(num_strategies)
        self.best_strategy = None
        self.attend = False
        self.prediction = None
        self.memory = np.zeros(memory_size)
        self.crowdthreshold = crowdthreshold

    #need to add step method here, to activate make_decision
    def step(self):
        self.prediction = 
        self.update_strategies()
    
    def update_strategies(self):
        pass
    
    def random_strategy(self):

        return np.random.choice(self.strategies)
    
    def predict_attendance(self):
        pass
    
    def random_move(self):
        pass