import unittest
from mesa.ReproductionModel import *
from mesa.EvoAgent import *
import random

class TestReproductionModel(unittest.TestCase):
    """
    Test suite for class ReproductionModel
    """
    # def __init__(self, *args, **kwargs):
    #     super(TestReproductionModel, self).__init__(*args, **kwargs)

    def test_AsexualReproduction(self):
        m=AsexualReproduction()
        n=random.randint(1,10)
        a=EvoAgent(1,None,energy=n*2)
        offspring=m.reproduce(a)
        self.assertFalse((a.dna==offspring.dna).all()) # dna mutated
        # split energy
        self.assertEqual(a.energy,n)
        self.assertEqual(offspring.energy,n)

    def test_SexualReproduction(self):
        m=SexualReproduction()
        n=random.randint(1,10)
        n2=random.randint(1,10)
        a=EvoAgent(1,None,energy=n*3)
        a1=EvoAgent(2,None,energy=n2*3)
        offspring=m.reproduce(a,[a1])                  # only one possible partner
        self.assertFalse((a.dna==offspring.dna).all()) # dna mutated
        # split energy
        self.assertEqual(a.energy,n*2)
        self.assertEqual(a1.energy,n2*2)
        self.assertEqual(offspring.energy,n+n2)

    def test_SexualReproduction_energy_false(self):
        m=SexualReproduction()
        a=EvoAgent(1,None,energy=False)
        a1=EvoAgent(2,None,energy=False)
        offspring=m.reproduce(a,[a1])                  # only one possible partner
        self.assertFalse(offspring.energy)
        a=EvoAgent(2,None,energy=1)  # if one parent's energy is not False, reproduction fails
        offspring=m.reproduce(a,[a1])                  # only one possible partner
        self.assertFalse(offspring)

    def test_SexualReproduction_self_partner(self):
        m=SexualReproduction()
        n=random.randint(1,10)
        a=EvoAgent(1,None,energy=n*3)
        offspring=m.reproduce(a,[a])                   # the partner is the agent itself
        self.assertFalse(offspring)                    # failure

    def test_mixing_ratio(self):
        class TestAgent(EvoAgent):
            def mutate(self):
                pass            # no mutations
        a=TestAgent(1,None,energy=False)
        a1=TestAgent(2,None,energy=False)
        m=SexualReproduction(mixing_ratio=1.0) # keep only the mother's
        offspring=m.reproduce(a,[a1])                  # only one possible partner
        self.assertTrue((a.dna==offspring.dna).all())
        m=SexualReproduction(mixing_ratio=0.0) # keep only the father
        offspring=m.reproduce(a,[a1])                  # only one possible partner
        self.assertTrue((a1.dna==offspring.dna).all())
