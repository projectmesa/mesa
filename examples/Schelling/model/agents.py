from mesa import Agent


class SchellingAgent(Agent):
    '''
    Schelling segregation agent
    '''
    def __init__(self, pos, agent_type):
        '''
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        self.unique_id = pos
        self.pos = pos
        self.type = agent_type

    def step(self, model):
        similar = 0
        for neighbor in model.grid.neighbor_iter(self.pos):
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < model.homophily:
            model.grid.move_to_empty(self)
        else:
            model.happy += 1
