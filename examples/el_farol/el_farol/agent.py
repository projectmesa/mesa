from mesa import Agent

class BarCostumer(Agent):

     def __init__(self, unique_id, model):
        super().__init__(unique_id, model,n_strategies)
        self.strategies = np.zeros(n_strategies)
        self.best_strategy = None
        self.attend = None
        self.prediction = None

    #need to add step method here, to activate make_decision
    def step(self):
        pass
    
    def update_strategies(self):
        pass
    
    def random_strategy(self):
        pass
    
    def predict_attendance(self):
        pass
    
    def random_move(self):
        pass