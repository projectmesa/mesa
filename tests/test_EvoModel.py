import unittest
from mesa.EvoModel import *
from mesa.EvoAgent import *
from mesa.SelectionModel import *
from mesa.ReproductionModel import *
from mesa.time import BaseScheduler
import random

class TestEvoModel(unittest.TestCase):
    """
    Test suite for class EvoModel
    """
    # def __init__(self, *args, **kwargs):
    #     super(TestEvoModel, self).__init__(*args, **kwargs)

    def test_init_agents(self):
        r=ReproductionModel();s=SelectionModel(r)
        l1="1";l2="2"
        class TestAgent1(EvoAgent):
            def __init__(self, unique_id,model):
                super().__init__(unique_id,model,energy=False)
                self.label=l1

        class TestAgent2(EvoAgent):
            def __init__(self, unique_id,model):
                super().__init__(unique_id,model,energy=False)
                self.label=l2

        n1=random.randint(1,10);n2=random.randint(1,10)
        agents=[(TestAgent1,n1,{}),(TestAgent2,n2,{})]
        m=EvoModel(agents,s,BaseScheduler)
        l1_count=0;l2_count=0
        for i in m.schedule.agents:
            if i.label==l1:
                l1_count+=1
            elif i.label==l2:
                l2_count+=1
            else:
                raise(TypeError,"Wrong label")
        self.assertEqual(l1_count,n1)
        self.assertEqual(l2_count,n2)
