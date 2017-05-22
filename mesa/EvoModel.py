from mesa.model import *

class EvoModel(Model):
    """
    Model for evolutionary simulations.
    EvoModel extends Model to deal with death and reproduction in the population. It also supports mixed populations with agents of different types.
    EvoModel requires a subclass of SelectionModel.

    Attributes:
    schedule: the initial size of the population
    last_id: used to assign incremental ids to newly generated agents
    sel_f: a selection model
    """
    def __init__(self,agent_dict,selection_model,scheduler):
        """
        Args:
        agent_dict: list of triples containing the agent class, the number of agents of that class and a dictionary with additional parameters
        selection_model: an instance of SelectionModel of any derivate
        scheduler: an class derivated from BaseScheduler
        """
        super().__init__()
        self.schedule = scheduler(self)
        self.last_id=0
        # Create agents
        for t,n,p in agent_dict:
            for i in range(n):
                a = t(self.last_id, self,**p)
                self.last_id+=1
                print("adding agent of type "+str(t)+" to schedule")
                self.schedule.add(a)
        self.sel_f=selection_model

    def step(self):
        """
        Advance the model by one step.
        """
        # Update the population
        self.__update_population()
        self.schedule.step()    # call the step method of all agents

    def update_population(self):
        self.sel_f.nextGeneration(self.schedule.agents)
        for i in self.sel_f.deaths:
            print("Removing agent "+str(i.unique_id))
            self.schedule.remove(i)
        # Add offsprings from last turn
        for i in self.sel_f.offsprings:
            i.unique_id=self.last_id
            print("adding agent "+str(i.unique_id))
            self.schedule.add(i)
            self.last_id+=1

    def is_dead(self,agent=False):
        """
        Returns: True if the agent is dead
        """
        return agent is False or agent in self.sel_f.deaths

    def is_parent(self,agent=False):
        """
        Returns: True if the agent reproduced
        """
        if agent is False:
            return False
        else:
            return agent in self.sel_f.pregnancies
