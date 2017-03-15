import numpy as np
import random

from mesa.EvoAgent import *

class SelectionModel:
    """
    SelectionModel determines the modalities of death and reproduction.
    Base class for the selection model, which does nothing.
    SelectionModel requires a subclass of ReproductioModel

    Arguments:
    deaths: a list of agents that died in this turn
    offsprings: a list of agents spawned in this turn
    pregnancies: a list of agents that reproduced in this turn
    repr_f: the reproduction model
    """
    def __init__(self,reproduction_model):
        self.deaths=[]
        self.offsprings=[]
        self.pregnancies=[]
        self.repr_f=reproduction_model

    def nextGeneration(self,population):
        """
        Process the population, kill agents and produce new agents.

        Returns: the subset of the population composed of EvoAgents
        """
        self.deaths=[]
        self.offsprings=[]
        self.pregnancies=[]
        return [p for p in population if isinstance(p,EvoAgent)] # select only evolutionary agents

    def agentReproduces(self,agent,**kwargs):
        """
        Creates a new agent and adds it to the offsprings.

        Args:
        agent: the agent that reproduces

        Kwargs:
        Any argument required by the reproduction model
        """
        offspring=self.repr_f.reproduce(agent,**kwargs)
        if offspring is not None:
            self.pregnancies.append(agent)
            self.offsprings.append(offspring)

    def agentDies(self,agent):
        """
        Adds an agent to the deads.
        """
        self.deaths.append(agent)

class RouletteSelection(SelectionModel):
    """
    Subclass RouletteSelection implements the roulette-wheel selection with stochastic acceptance:
    a fraction of the population is considered for death and reproduction, each agent obtains a weight based on its characteristics (age/energy)
    and a model parameter (max_age/max_energy) and it dies/reproduces with a probability proportional to the weight.

    Arguments:
    f2k: fraction of the population (randomly chosen agents) to consider for death, the remaining population is not tested.
    f2m: fraction of the population (randomly chosen agents) to consider for reproduction, the remaining population is not tested.
    max_energy: the max energy to consider in the computation of the weights when testing for reproduction
    max_age: the max age to consider in the computation of the weights when testing for death
    """
    def __init__(self,model,fraction_to_kill=1.0,fraction_to_mate=1.0,max_energy=20,max_age=20):
        super().__init__(model)
        self.f2k=fraction_to_kill
        self.max_energy=max_energy
        self.max_age=max_age
        self.f2m=fraction_to_mate

    def nextGeneration(self,population=[],**kwargs):
        """
        Args:
        population: a list containing all agents in the schedule

        Kwargs:
        Any argument required by the reproduction model
        """
        pop=super().nextGeneration(population)
        for i in pop:
            if i.energy is False:
                print("Warning: Forcing agent "+str(i.unique_id)+" to have an integer energy, setting it to 0")
                i.energy=0
        nkills=int(self.f2k*len(pop))
        pop=[]                  # agents that are alive
        for i in pop:
            if i.is_dead(): # remove agents with no energy left
                self.agentDies(i,**kwargs)
            else:
                pop.append(i)
        np.random.shuffle(pop)
        pop=pop[:nkills] # test only nkills agents
        if(len(pop)>0):
            for i in pop:
                w=float(i.age/self.max_age)
                if random.random() < w:
                    self.agentDies(i,**kwargs)
        # reproduction
        pop=[i for i in pop if i not in self.deaths]
        ncouples=int(self.f2m*len(pop))
        pop=pop[:ncouples] # only ncouples agents can procreate
        if(len(pop)>0):
            for i in pop:
                w=float(i.energy/self.max_energy)
                if random.random()<w:
                    self.agentReproduces(i,population=pop,**kwargs)

class ProbabilisticSelection(SelectionModel):
    """
    Subclass ProbabilisticSelection agents die with a given probability and reproduce with another, determined by model parameters.
    If the agent specifies individual probabilities, they are used instead of the global probabilities.
    Arguments:
    die_p: the global probabiliy for which agents die, it is overridden by individual arguments of agents
    repr_p: the global probabiliy for which agents reproduce, it is overridden by individual arguments of agents
    """
    def __init__(self,model,die_p=0.5,repr_p=1.0):
        super().__init__(model)
        self.die_p=die_p
        self.repr_p=repr_p

    def nextGeneration(self,population=[],**kwargs):
        """
        Args:
        population: a list containing all agents in the schedule

        Kwargs:
        Any argument required by the reproduction model
        """
        pop=super().nextGeneration(population)
        for i in pop:
            if (i.energy is not False and i.energy<0) or i.is_dead() or self.__is_dead(i):
                self.agentDies(i,**kwargs)
        for i in pop:
            if (i.energy is False or i.energy>1) and not i.is_dead() and self.__is_parent(i):
                self.agentReproduces(i,**kwargs)

    def __is_dead(self,agent=False):
        """
        Test if the agent is dead.
        Use the individual probability of the agent, if present, otherwise the probability of the model
        """
        p=False
        if agent is not False:
            if agent.die_p is not False:
                p=agent.die_p
            elif self.die_p is not False:
                p=self.die_p
            else:
                print("Warning: no death probability defined")
                return False
        elif self.die_p is not False:
            p=self.die_p
        else:
            print("Warning: no death probability defined")
            return False
        return random.random() < p

    def __is_parent(self,agent=False):
        """
        Test if the agent reproduces.
        Use the individual probability of the agent, if present, otherwise the probability of the model
        """
        p=False
        if agent is not False:
            if agent.repr_p is not False:
                p=agent.repr_p
            elif self.repr_p is not False:
                p=self.repr_p
            else:
                print("Warning: no death probability defined")
                return False
        elif self.repr_p is not False:
            p=self.repr_p
        else:
            print("Warning: no death probability defined")
            return False
        return random.random() < p
