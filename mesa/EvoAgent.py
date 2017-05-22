from mesa.agent import *
import copy
import numpy as np

class EvoAgent(Agent):
    """
    An agent suited for playing in an evolutionary environment.
    EvoAgent extends Agent to deal with energy, age, death, reproduction and genome

    Attributes:
    dna: contains the genetic code of the individual, an array of float numbers whose length is determined on creation by the parameter 'genome_len'
    energy: the energy of the agent
    age: the age, it is automatically incremented at every step
    repr_p: the individual probability of reproduction, relevant when using a probabilistic selection model. The individual probability overrides the global probability.
    die_p: the individual probability of death, relevant when using a probabilistic selection model. The individual probability overrides the global probability.
    mutation_rate: how much the dna can mutate during reproduction
    """
    def __init__(self, unique_id,model,energy=False,genome_len=10,repr_p=False,die_p=False,mutation_rate=1.0):
        """
        Args:
        unique_id: the unique identifier of this agent
        energy: the starting energy. If False, the energy is ignored. Defaults to False.
        genome_len: the size of the dna
        repr_p: the individual probability of reproduction
        die_p: the individual probability of death
        """
        super().__init__(unique_id,model)
        self.dna = np.random.random(genome_len)
        self.energy=energy
        self.age=0
        self.repr_p=repr_p
        self.die_p=die_p
        self.mutation_rate=mutation_rate
        self.deceased=False

    def step(self):
        """
        Performs one step of simulation

        Side effect: age is increased by 1
        """
        self.age+=1

    def duplicate(self):
        """
        Creates a clone of this agent, used during reproduction.
        Any method overloading this should call super and copy any additional parameters introduced in the subclass

        Returns: An agent of the same class with identical attributes
        """
        dup=type(self)(self.unique_id,self.model)
        dup.energy=self.energy
        dup.repr_p=self.repr_p
        dup.die_p=self.die_p
        dup.dna=copy.deepcopy(self.dna)
        dup.mutation_rate=copy.deepcopy(self.mutation_rate)
        return dup

    def mutate(self):
        """
        Mutates the dna
        """
        g=np.asarray(self.dna)
        mutations=np.random.normal(0,self.mutation_rate,len(g))
        self.dna=g+mutations

    def consume_energy(self,diff=1):
        if self.energy is not False:
            self.energy-=diff
            if self.energy<=0:
                self.deceased=True
        else:
            print("Warning, trying to decrement energy with value False")

    def gain_energy(self,diff=1):
        if self.energy is not False:
            self.energy+=diff
        else:
            print("Warning, trying to decrement energy with value False")

    def kill(self):
        self.deceased=True

    def is_dead(self):
        return self.deceased
