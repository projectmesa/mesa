import unittest
from mesa.SelectionModel import *
from mesa.ReproductionModel import *
from mesa.EvoAgent import *
import random

class TestSelectionModel(unittest.TestCase):
    """
    Test suite for class SelectionModel
    """
    # def __init__(self, *args, **kwargs):
    #     super(TestSelectionModel, self).__init__(*args, **kwargs)

    def test_init(self):
        r=ReproductionModel()
        for t in [SelectionModel,RouletteSelection,ProbabilisticSelection]:
            s=t(r)
            self.assertFalse(s.deaths) # empty
            self.assertFalse(s.offsprings) # empty
            self.assertFalse(s.pregnancies) # empty
            s.deaths=[1]
            s.offsprings=[1]
            s.pregnancies=[1]
            s.nextGeneration([])
            self.assertFalse(s.deaths) # empty
            self.assertFalse(s.offsprings) # empty
            self.assertFalse(s.pregnancies) # empty

    def test_reproduction(self):
        a=EvoAgent(1,None)
        r=ReproductionModel()   # clones the agent
        for t in [SelectionModel,RouletteSelection,ProbabilisticSelection]:
            s=t(r)
            s.agentReproduces(a)
            self.assertTrue((s.pregnancies[0].dna==a.dna).all())
            self.assertTrue((s.offsprings[0].dna==a.dna).all())

    def test_death(self):
        a=EvoAgent(1,None)
        r=ReproductionModel()   # clones the agent
        for t in [SelectionModel,RouletteSelection,ProbabilisticSelection]:
            s=t(r)
            s.agentDies(a)
            self.assertTrue((s.deaths[0].dna==a.dna).all())

    def test_probabilistic_selection(self):
        # individual parameters override the globals
        a=EvoAgent(1,None,repr_p=0.0,die_p=0.0)
        r=ReproductionModel()   # clones the agent
        s=ProbabilisticSelection(r,die_p=1.0,repr_p=1.0)
        for t in range(50):
            s.nextGeneration([a])
            self.assertFalse(s.deaths) # empty
            self.assertFalse(s.offsprings) # empty
            self.assertFalse(s.pregnancies) # empty
        # global parameters
        a=EvoAgent(1,None,repr_p=False,die_p=False)
        r=ReproductionModel()   # clones the agent
        s=ProbabilisticSelection(r,die_p=1.0,repr_p=1.0)
        s.nextGeneration([a])
        self.assertTrue((s.deaths[0].dna==a.dna).all())
        self.assertTrue((s.offsprings[0].dna==a.dna).all())
        self.assertTrue((s.pregnancies[0].dna==a.dna).all())
        # global parameters
        a=EvoAgent(1,None,repr_p=0.0,die_p=0.0)
        a1=EvoAgent(2,None,repr_p=False,die_p=False)
        r=ReproductionModel()   # clones the agent
        s=ProbabilisticSelection(r,die_p=1.0,repr_p=1.0)
        s.nextGeneration([a,a1])
        self.assertEqual(len(s.deaths),1)
        self.assertTrue((s.deaths[0].dna==a1.dna).all())
        self.assertEqual(len(s.offsprings),1)
        self.assertTrue((s.offsprings[0].dna==a1.dna).all())
        self.assertEqual(len(s.pregnancies),1)
        self.assertTrue((s.pregnancies[0].dna==a1.dna).all())
