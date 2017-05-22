import unittest
from mesa.EvoAgent import *
import random

class TestEvoAgent(unittest.TestCase):
    """
    Test suite for class EvoAgent
    """

    def __init__(self, *args, **kwargs):
        super(TestEvoAgent, self).__init__(*args, **kwargs)
        uid=random.randint(1,10)
        e=random.randint(1,10)
        l=random.randint(1,10)
        r=random.randint(1,10)
        d=random.randint(1,10)
        m=random.randint(1,10)
        self.a=EvoAgent(uid,None,energy=e,genome_len=l,repr_p=r,die_p=d,mutation_rate=m)

    def test_age_increase(self):
        self.assertEqual(self.a.age,0)
        self.a.step()
        self.assertEqual(self.a.age,1)

    def test_duplicate(self):
        cp=self.a.duplicate()
        self.assertEqual(type(cp),type(self.a))
        self.assertTrue((cp.dna==self.a.dna).all())
        self.assertEqual(cp.unique_id,self.a.unique_id)
        self.assertEqual(cp.energy,self.a.energy)
        self.assertEqual(cp.age,self.a.age)
        self.assertEqual(cp.repr_p,self.a.repr_p)
        self.assertEqual(cp.die_p,self.a.die_p)
        self.assertEqual(cp.mutation_rate,self.a.mutation_rate)

    def test_mutate(self):
        cp=self.a.duplicate()
        cp.mutate()
        self.assertFalse((cp.dna==self.a.dna).all())

    def test_duplicate_energy_mod(self):
        """
        Make sure that the objects are two different instances, so by modifiying one object the other is not affected
        """
        cp=self.a.duplicate()
        cp.energy=self.a.energy+1
        self.assertEqual(cp.energy,self.a.energy+1)
