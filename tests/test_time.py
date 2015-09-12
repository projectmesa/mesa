'''
Test the advanced schedulers.
'''

import unittest
from mesa import Model, Agent
from mesa.time import StagedActivation


class MockStagedAgent(Agent):
    '''
    Minimalistic agent for testing purposes.
    '''

    def __init__(self, name):
        self.unique_id = name

    def stage_one(self, model):
        model.log.append(self.unique_id + "_1")

    def stage_two(self, model):
        model.log.append(self.unique_id + "_2")


class MockModel(Model):

    def __init__(self, shuffle):
        self.log = []
        model_stages = ["stage_one", "stage_two"]
        self.schedule = StagedActivation(self, model_stages, shuffle=shuffle)

        # Make agents
        for name in ["A", "B"]:
            agent = MockStagedAgent(name)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()


class TestStagedActivation(unittest.TestCase):
    '''
    Test the staged activation.
    '''

    expected_output = ["A_1", "B_1", "A_2", "B_2"]

    def test_no_shuffle(self):
        '''
        Testing staged activation without shuffling.
        '''
        model = MockModel(False)
        model.step()
        assert model.log == self.expected_output

    def test_shuffle(self):
        '''
        Test staged activation with shuffling
        '''
        model = MockModel(True)
        model.step()
        for output in self.expected_output[:2]:
            assert output in model.log[:2]
        for output in self.expected_output[2:]:
            assert output in model.log[2:]


