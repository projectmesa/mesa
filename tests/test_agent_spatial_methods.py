import pytest

from mesa.agent import Agent
from mesa.model import Model
from mesa.space import ContinuousSpace, MultiGrid


@pytest.fixture
def agent_in_space():
    model = Model()
    model.space = ContinuousSpace(10, 10, torus=True)
    agent = Agent(1, model)
    agent.pos = (2, 1)
    agent.heading = 0
    return agent


def test_move_forward(agent_in_space):
    agent_in_space.heading = 90
    agent_in_space.move_forward(1)
    assert agent_in_space.pos[0] == pytest.approx(2)
    assert agent_in_space.pos[1] == pytest.approx(0)


def test_turn_right(agent_in_space):
    agent_in_space.heading = 0
    agent_in_space.turn_right(60)
    assert agent_in_space.heading == 300
    agent_in_space.move_forward(1)
    assert agent_in_space.pos[0] == pytest.approx(2.5)
    assert agent_in_space.pos[1] == pytest.approx(1.8660254)


def test_move_forward_toroid(agent_in_space):
    "Verify that toroidal wrapping applies to move_forward"

    agent_in_space.move_forward(10.0)
    assert agent_in_space.pos[0] == pytest.approx(2)
    assert agent_in_space.pos[1] == pytest.approx(1)


def test_move_forward_raises_if_no_space():
    """move_forward only applies for models with ContinuousSpace"""

    model = Model()
    model.grid = MultiGrid(10, 10, torus=True)
    agent = Agent(1, model)
    agent.pos = (2, 1)
    with pytest.raises(Exception):
        agent.move_forward(10.0)


def test_towards(agent_in_space):
    agent2 = Agent(2, agent_in_space.model)
    agent2.pos = (5, 1)
    assert agent_in_space.towards(agent2) == pytest.approx(0)
    agent2.pos = (2, 4)
    assert agent_in_space.towards(agent2) == pytest.approx(270)
    agent2.pos = (5, 4)
    assert agent_in_space.towards(agent2) == pytest.approx(-45)


def test_facexy(agent_in_space):
    agent_in_space.facexy(2, 5)
    assert agent_in_space.heading == pytest.approx(270)


def test_face(agent_in_space):
    agent2 = Agent(2, agent_in_space.model)
    agent2.pos = (5, 1)
    agent_in_space.face(agent2)
    assert agent_in_space.heading == pytest.approx(0)
