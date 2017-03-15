import numpy as np
import copy

class ReproductionModel:
    """
    ReproductionModel deals with the reproduction.
    Base class for reproduction models, it clones the agent.
    """
    def __init__(self):
        pass

    def reproduce(self,agent,**kwargs):
        """
        Args:
        agent: the agent that reproduces

        Kwargs:
        Any argument required by the specific implementation of the reproduction model
        """
        return copy.deepcopy(agent)
        pass

class AsexualReproduction(ReproductionModel):
    """
    Subclass AsexualReproduction create an offspring that is derived from the agent, with a mutated dna.
    """
    def __init__(self):
        super().__init__()

    def reproduce(self,agent,**kwargs):
        """
        Agents can reproduce if their energy is False, or if their energy after reproduction is greater than 0
        Args:
        agent: the agent that reproduces

        Returns: the offspring if reproduction is successful, None otherwise
        """
        offspring=agent.duplicate()
        offspring.mutate()
        # split energy
        if agent.energy is not False:
            e=int(agent.energy/2)
            if agent.energy-e >0 and e>0:
                agent.energy-=e
                offspring.energy=e
                print(str(agent.unique_id)+" reproduces with new energy "+str(agent.energy)+" and offspring energy "+str(offspring.energy))
            else:
                offspring=None
        return offspring

class SexualReproduction(ReproductionModel):
    """
    Reproduces sexually by performing crossover and mutation with a suitable partner in the population.

    Attributes:
    mixing_ratio: the fraction of offspring's genes to take from the agent's dna. Defaults to 0.5, both parents contribute with the same number of genes.
    """
    def __init__(self,mixing_ratio=0.5):
        super().__init__()
        self.mixing_ratio=mixing_ratio

    def reproduce(self,agent,population=[],**kwargs):
        """
        Agents can reproduce if their energy is False, or if the energy after reproduction of both parents and of the offspring is greater than 0
        the partner is randomly choosen by all other agents in the population of the same type as agent, with enough energy for reproduction

        Args:
        agent: the agent that reproduces
        population: a list of possible partners

        Returns: the offspring, if a partner is found, None otherwise
        """
        offspring=agent.duplicate()
        partners=copy.copy(population)
        np.random.shuffle(partners)
        partners=[i for i in partners if i!=agent and (
            (agent.energy is False and i.energy is False) or # if energy is false ignore it
            int(agent.energy/3)+int(i.energy/3)>0 # check that the energy of the offspring is greater than 0
        ) and isinstance(i,type(agent))]            # of the same type
        if partners:
            partner=partners[0] # randomly chosen by shuffle
            assert(agent.unique_id!=partner.unique_id)
            # crossover
            g1=agent.dna
            g2=partner.dna
            assert(len(g1)==len(g2))
            rng=np.arange(len(g1))
            np.random.shuffle(rng)
            mask=rng[:int(len(g1)*self.mixing_ratio)] # choose randomly what genes to cross over
            g1=[i if c in mask else j for i,j,c in zip(g1,g2,np.arange(len(g1)))]
            # mutate
            offspring.dna=g1
            offspring.mutate()
            # split energy
            if agent.energy is not False:
                e=int(agent.energy/3)
                e2=int(partner.energy/3)
                if agent.energy-e>0 and partner.energy-e2>0 and e+e2>0:
                    agent.energy-=e
                    partner.energy-=e2
                    offspring.energy=e+e2
                    print(str(agent.unique_id)+" and "+str(partner.unique_id)+" are parents of "+str(offspring.unique_id))
                else:
                    offspring=None
            return offspring
        else:
            return None
