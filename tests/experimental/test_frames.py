"""Tests for frames and locations."""

import copy
import math
import pickle
import random

import networkx as nx
import numpy as np
import pytest

from mesa import Agent, Model
from mesa.discrete_space import (
    CellAgent,
    DiscreteSpace,
    HexGrid,
    Network,
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
    VoronoiGrid,
)
from mesa.exceptions import CellFullException, SpaceException
from mesa.experimental.continuous_space import ContinuousSpace, ContinuousSpaceAgent
from mesa.experimental.frames import Frame, Location


class Bird(Agent):
    """An agent located through a Location descriptor."""

    position = Location("physical")


def stacked_model(torus=False, capacity=None):
    """A continuous space of 100 by 100 over a 50 by 50 grid."""
    model = Model(rng=42)
    model.physical = Frame("physical", ndim=2)
    model.air = ContinuousSpace(
        [[0, 100], [0, 100]], torus=torus, random=model.random, frame=model.physical
    )
    model.ground = OrthogonalMooreGrid(
        (50, 50),
        torus=torus,
        capacity=capacity,
        random=model.random,
        frame=model.physical,
        cell_size=2.0,
    )
    return model


# ----------------------------------------------------------------------
# The sketch from discussion #2585
# ----------------------------------------------------------------------
def test_sketch():
    """A write through any member space reaches the others."""
    model = stacked_model()
    air, ground = model.air, model.ground
    bird = Bird(model)

    assert bird.position is None
    air.add(bird, [10.0, 20.0])
    ground.add(bird)
    assert ground.cell_of(bird) is ground[(5, 10)]
    assert bird in ground[(5, 10)].agents

    bird.position = [12.0, 21.0]
    np.testing.assert_array_equal(air.agent_positions, [[12.0, 21.0]])
    assert ground.cell_of(bird) is ground[(6, 10)]
    assert ground[(5, 10)].is_empty

    # a cell move snaps to the cell center, and the continuous space sees it
    ground.move(bird, ground[(0, 0)])
    np.testing.assert_array_equal(bird.position, [1.0, 1.0])
    np.testing.assert_array_equal(air.agent_positions, [[1.0, 1.0]])

    bird.remove()
    assert len(air.agent_positions) == 0
    assert ground[(0, 0)].is_empty
    assert bird._mesa_locations is None


def test_query_without_membership():
    """An agent can look up cells of a space it is not in."""
    model = stacked_model()
    bird = Bird(model)
    model.air.add(bird, [10.0, 20.0])
    cell = model.ground.find_nearest_cell(bird.position)
    assert cell is model.ground[(5, 10)]
    assert cell.is_empty
    assert model.ground.cell_of(bird) is None


# ----------------------------------------------------------------------
# Frames
# ----------------------------------------------------------------------
def test_private_frames():
    """Spaces without a frame get one of their own."""
    rng = random.Random(1)
    grid = OrthogonalMooreGrid((3, 3), random=rng)
    other = OrthogonalMooreGrid((3, 3), random=rng)
    space = ContinuousSpace([[0, 1], [0, 1]], random=rng)
    assert grid.frame is not other.frame
    assert grid.frame.spaces == [grid]
    assert space.frame.spaces == [space]
    assert grid.frame.ndim == 2
    assert grid.frame.name is None


def test_frame_validation():
    """Spaces in a frame must agree on dimensions, torus and torus extent."""
    rng = random.Random(1)
    frame = Frame("physical", ndim=2)
    ContinuousSpace([[0, 10], [0, 10]], torus=True, random=rng, frame=frame)
    assert frame.torus is True

    with pytest.raises(ValueError, match="dimensions"):
        OrthogonalMooreGrid((5, 5, 5), torus=True, random=rng, frame=frame)
    with pytest.raises(ValueError, match="torus"):
        OrthogonalMooreGrid((10, 10), torus=False, random=rng, frame=frame)
    with pytest.raises(ValueError, match="same extent"):
        OrthogonalMooreGrid((5, 5), torus=True, random=rng, frame=frame)

    OrthogonalMooreGrid((5, 5), torus=True, random=rng, frame=frame, cell_size=2.0)
    assert len(frame.spaces) == 2

    # without a torus the extents may differ
    frame = Frame(ndim=2)
    ContinuousSpace([[0, 10], [0, 10]], random=rng, frame=frame)
    OrthogonalMooreGrid((3, 3), random=rng, frame=frame)
    assert frame.bounds is None


def test_grid_mapping():
    """cell_size and origin place a grid in its frame."""
    rng = random.Random(1)
    grid = OrthogonalMooreGrid(
        (4, 3), random=rng, cell_size=(2.0, 5.0), origin=(10, 20)
    )
    np.testing.assert_array_equal(grid[(0, 0)].position, [11.0, 22.5])
    np.testing.assert_array_equal(grid[(3, 2)].position, [17.0, 32.5])
    assert grid.find_nearest_cell([10.0, 20.0]) is grid[(0, 0)]
    assert grid.find_nearest_cell([17.9, 34.9]) is grid[(3, 2)]
    with pytest.raises(ValueError, match="outside grid bounds"):
        grid.find_nearest_cell([9.9, 20.0])
    with pytest.raises(ValueError, match="outside grid bounds"):
        grid.find_nearest_cell([18.0, 20.0])

    with pytest.raises(ValueError, match="positive"):
        OrthogonalMooreGrid((4, 3), random=rng, cell_size=0)
    with pytest.raises(ValueError, match="one value for each"):
        OrthogonalMooreGrid((4, 3), random=rng, cell_size=(1, 2, 3))

    # positions are cached and cannot be changed in place
    assert grid[(0, 0)].position is grid[(0, 0)].position
    with pytest.raises(ValueError):
        grid[(0, 0)].position[0] = 3


@pytest.mark.parametrize(
    "space",
    [
        OrthogonalMooreGrid((4, 5), random=random.Random(1)),
        OrthogonalMooreGrid((4, 5), torus=True, random=random.Random(1)),
        OrthogonalVonNeumannGrid(
            (4, 5, 3), random=random.Random(1), cell_size=0.1, origin=(0.3, -7, 1e6)
        ),
        OrthogonalMooreGrid((7, 7), random=random.Random(1), cell_size=1 / 3),
        HexGrid((4, 4), random=random.Random(1)),
        HexGrid((4, 4), torus=True, random=random.Random(1)),
        VoronoiGrid([(1, 1), (5, 2), (3, 8), (9, 9)], random=random.Random(1)),
    ],
    ids=[
        "moore",
        "moore-torus",
        "von-neumann-3d",
        "moore-thirds",
        "hex",
        "hex-torus",
        "voronoi",
    ],
)
def test_cell_position_round_trip(space):
    """The position of a cell lies in that cell."""
    for cell in space.all_cells:
        assert space.find_nearest_cell(cell.position) is cell


def test_grid_pickle_keeps_mapping():
    """A grid survives pickling with its mapping and one cell class."""
    grid = OrthogonalMooreGrid(
        (4, 4), random=random.Random(1), cell_size=2.0, origin=(1, 1)
    )
    grid.create_property_layer("sugar", 3.0)
    clone = pickle.loads(pickle.dumps(grid))  # noqa: S301
    assert len({type(cell) for cell in clone.all_cells}) == 1
    np.testing.assert_array_equal(clone[(3, 3)].position, [8.0, 8.0])
    assert clone[(3, 3)].sugar == 3.0
    assert clone.find_nearest_cell([8.5, 8.5]) is clone[(3, 3)]
    assert clone.frame.spaces == [clone]


def test_deepcopy_stacked_model():
    """A copied model has its own frame, and its spaces still agree."""
    model = stacked_model()
    bird = Bird(model)
    model.air.add(bird, [1.0, 1.0])
    model.ground.add(bird)

    clone = copy.deepcopy(model)
    bird2 = next(iter(clone.agents))
    bird2.position = [51.0, 99.0]

    np.testing.assert_array_equal(bird.position, [1.0, 1.0])
    assert model.ground.cell_of(bird) is model.ground[(0, 0)]
    np.testing.assert_array_equal(clone.air.agent_positions, [[51.0, 99.0]])
    assert clone.ground.cell_of(bird2) is clone.ground[(25, 49)]
    assert clone.physical is not model.physical


# ----------------------------------------------------------------------
# Locations
# ----------------------------------------------------------------------
def test_location_descriptor():
    """Location reads, writes and clears through the frame."""
    model = stacked_model()
    bird = Bird(model)

    assert isinstance(Bird.position, Location)
    assert Bird.position.frame_name == "physical"
    assert Location(model.physical).frame_name == "physical"
    with pytest.raises(ValueError, match="named frame"):
        Location(Frame())

    with pytest.raises(ValueError, match="not in a space"):
        bird.position = [1.0, 1.0]
    bird.position = None  # nothing to clear

    model.ground.add(bird, model.ground[(2, 3)])
    np.testing.assert_array_equal(bird.position, [5.0, 7.0])
    np.testing.assert_array_equal(model.physical.location_of(bird), [5.0, 7.0])

    # a point write is kept as written, also without a continuous space
    bird.position = [5.5, 7.9]
    np.testing.assert_array_equal(bird.position, [5.5, 7.9])
    assert model.ground.cell_of(bird) is model.ground[(2, 3)]

    with pytest.raises(ValueError):
        bird.position[0] = 1.0
    with pytest.raises(ValueError, match="2 coordinates"):
        bird.position = [1.0, 2.0, 3.0]

    bird.position = None
    assert bird.position is None
    assert model.ground[(2, 3)].is_empty


def test_same_frame_name_twice():
    """An agent cannot be in two different frames with the same name."""
    model = Model(rng=1)
    grid = OrthogonalMooreGrid((3, 3), random=model.random, frame=Frame("physical"))
    other = OrthogonalMooreGrid((3, 3), random=model.random, frame=Frame("physical"))
    bird = Bird(model)
    grid.add(bird, grid[(0, 0)])
    with pytest.raises(ValueError, match="another frame named"):
        other.add(bird, other[(0, 0)])


def test_two_frames():
    """An agent has an independent location in each frame."""

    class Citizen(Agent):
        position = Location("physical")
        view = Location("opinion")

    model = Model(rng=1)
    physical, opinion = Frame("physical"), Frame("opinion")
    districts = OrthogonalMooreGrid((4, 4), random=model.random, frame=physical)
    stance = ContinuousSpace([[-1, 1], [-1, 1]], random=model.random, frame=opinion)
    blocs = VoronoiGrid([(-0.5, 0.0), (0.5, 0.0)], random=model.random, frame=opinion)
    home = ContinuousSpace([[0, 4], [0, 4]], random=model.random, frame=physical)

    citizen = Citizen(model)
    districts.add(citizen, districts[(1, 2)])
    home.add(citizen)
    stance.add(citizen, [-0.3, 0.2])
    blocs.add(citizen)

    assert blocs.cell_of(citizen) is blocs[0]
    citizen.view = [0.4, -0.9]
    assert blocs.cell_of(citizen) is blocs[1]
    np.testing.assert_array_equal(citizen.position, [1.5, 2.5])
    np.testing.assert_array_equal(home.agent_positions, [[1.5, 2.5]])
    np.testing.assert_array_equal(stance.agent_positions, [[0.4, -0.9]])

    # distance queries work for agents that are not ContinuousSpaceAgents
    other = Citizen(model)
    stance.add(other, [0.4, 0.1])
    distances, _ = stance.calculate_distances([0.4, -0.9], agents=[other, citizen])
    np.testing.assert_allclose(distances, [1.0, 0.0])
    citizen.remove()
    distances, _ = stance.calculate_distances([0.4, -0.9], agents=[other])
    np.testing.assert_allclose(distances, [1.0])
    assert len(home.agent_positions) == 0


# ----------------------------------------------------------------------
# Atomic writes
# ----------------------------------------------------------------------
def test_write_into_full_cell_fails_atomically():
    """A write that one space rejects changes none of them."""
    model = stacked_model(capacity=1)
    air, ground = model.air, model.ground
    blocker, bird = Bird(model), Bird(model)
    air.add(blocker, [10.0, 10.0])
    ground.add(blocker)
    air.add(bird, [50.0, 50.0])
    ground.add(bird)

    with pytest.raises(CellFullException):
        bird.position = [11.0, 11.0]
    np.testing.assert_array_equal(bird.position, [50.0, 50.0])
    assert ground.cell_of(bird) is ground[(25, 25)]
    assert ground[(5, 5)].agents == [blocker]

    with pytest.raises(CellFullException):
        ground.move(bird, ground[(5, 5)])
    np.testing.assert_array_equal(bird.position, [50.0, 50.0])

    with pytest.raises(ValueError, match="outside"):
        bird.position = [100.5, 50.0]
    np.testing.assert_array_equal(bird.position, [50.0, 50.0])
    assert ground.cell_of(bird) is ground[(25, 25)]

    # joining a space at a full cell fails and leaves the agent out of it
    newcomer = Bird(model)
    air.add(newcomer, [10.5, 10.5])
    with pytest.raises(CellFullException):
        ground.add(newcomer)
    assert ground.cell_of(newcomer) is None
    np.testing.assert_array_equal(newcomer.position, [10.5, 10.5])


def test_rollback_across_two_grids():
    """A cell entered in one grid is left again if another grid is full."""
    model = Model(rng=1)
    frame = Frame("physical")
    fine = OrthogonalMooreGrid((4, 4), random=model.random, frame=frame)
    coarse = OrthogonalMooreGrid(
        (2, 2), capacity=1, random=model.random, frame=frame, cell_size=2.0
    )
    a, b = Bird(model), Bird(model)
    for agent, cell in ((a, fine[(0, 0)]), (b, fine[(3, 3)])):
        fine.add(agent, cell)
        coarse.add(agent)

    with pytest.raises(CellFullException):
        fine.move(b, fine[(1, 1)])  # fine has room, coarse cell (0, 0) is full
    assert fine[(1, 1)].is_empty
    assert fine[(1, 1)].empty
    assert fine.cell_of(b) is fine[(3, 3)]
    assert coarse.cell_of(b) is coarse[(1, 1)]

    # a move within the same coarse cell does not count against its capacity
    fine.move(a, fine[(1, 1)])
    assert coarse.cell_of(a) is coarse[(0, 0)]
    assert coarse[(0, 0)].agents == [a]


def test_torus_wrap():
    """A point outside a torus wraps the same way in every space."""
    model = stacked_model(torus=True)
    bird = Bird(model)
    model.air.add(bird, [99.0, 1.0])
    model.ground.add(bird)
    bird.position = bird.position + np.array([2.5, -3.0])
    np.testing.assert_allclose(bird.position, [1.5, 98.0])
    assert model.ground.cell_of(bird) is model.ground[(0, 49)]


def test_network_rejects_point_writes():
    """A network takes node moves, not points."""
    model = Model(rng=1)
    frame = Frame("physical")
    graph = nx.path_graph(3)
    layout = {0: (0.5, 0.5), 1: (1.5, 0.5), 2: (2.5, 0.5)}
    roads = Network(graph, random=model.random, layout=layout, frame=frame)
    grid = OrthogonalMooreGrid((3, 1), random=model.random, frame=frame)

    bird = Bird(model)
    roads.add(bird, roads[0])
    grid.add(bird)
    assert grid.cell_of(bird) is grid[(0, 0)]

    roads.move(bird, roads[2])
    assert grid.cell_of(bird) is grid[(2, 0)]

    with pytest.raises(SpaceException, match="by a point"):
        bird.position = [1.5, 0.5]
    with pytest.raises(SpaceException, match="by a point"):
        grid.move(bird, grid[(1, 0)])
    assert roads.cell_of(bird) is roads[2]
    assert grid.cell_of(bird) is grid[(2, 0)]

    other = Bird(model)
    grid.add(other, grid[(1, 0)])
    with pytest.raises(SpaceException, match="by a point"):
        roads.add(other)


# ----------------------------------------------------------------------
# Existing agent classes in shared frames
# ----------------------------------------------------------------------
def test_cell_agent_single_space_has_no_record():
    """A cell agent in one space stays on the single-space path."""
    model = Model(rng=1)
    grid = OrthogonalMooreGrid((3, 3), random=model.random)
    agent = CellAgent(model)
    grid.add(agent, grid[(1, 1)])
    assert agent.cell is grid[(1, 1)]
    assert agent._mesa_locations is None
    assert grid.cell_of(agent) is grid[(1, 1)]
    np.testing.assert_array_equal(grid.frame.location_of(agent), [1.5, 1.5])

    grid.move(agent, grid[(2, 2)])
    assert agent.cell is grid[(2, 2)]
    grid.remove(agent)
    assert agent.cell is None
    assert grid.frame.location_of(agent) is None
    with pytest.raises(ValueError, match="not in this"):
        grid.remove(agent)
    with pytest.raises(ValueError, match="add it first"):
        grid.move(agent, grid[(0, 0)])


def test_cell_agent_in_shared_frame():
    """agent.cell keeps working when the agent joins a second space."""
    model = stacked_model()
    air, ground = model.air, model.ground
    agent = CellAgent(model)
    agent.cell = ground[(1, 1)]
    air.add(agent)
    np.testing.assert_array_equal(air.agent_positions, [[3.0, 3.0]])

    agent.cell = ground[(4, 0)]
    np.testing.assert_array_equal(air.agent_positions, [[9.0, 1.0]])

    model.physical.move(agent, [20.5, 30.5])
    assert agent.cell is ground[(10, 15)]
    assert ground[(4, 0)].is_empty

    agent.cell = None
    assert ground.cell_of(agent) is None
    np.testing.assert_array_equal(air.agent_positions, [[20.5, 30.5]])
    agent.cell = ground[(0, 0)]
    np.testing.assert_array_equal(air.agent_positions, [[1.0, 1.0]])

    agent.remove()
    assert len(air.agent_positions) == 0
    assert ground[(0, 0)].is_empty
    assert agent.cell is None


def test_continuous_agent_in_shared_frame():
    """agent.position keeps working when the agent joins a grid."""
    model = stacked_model(capacity=1)
    air, ground = model.air, model.ground
    boid = ContinuousSpaceAgent(air, model)
    boid.position = [3.0, 3.0]
    other = ContinuousSpaceAgent(air, model)
    other.position = [9.0, 9.0]
    ground.add(boid)
    ground.add(other)

    boid.position = boid.position + np.array([4.0, 0.5])
    assert ground.cell_of(boid) is ground[(3, 1)]
    with pytest.raises(CellFullException):
        boid.position = [9.5, 9.5]
    np.testing.assert_array_equal(boid.position, [7.0, 3.5])

    ground.move(boid, ground[(10, 10)])
    np.testing.assert_array_equal(boid.position, [21.0, 21.0])

    with pytest.raises(ValueError, match="cannot leave"):
        air.remove(boid)
    with pytest.raises(ValueError, match="not added to this space"):
        air.remove(Bird(model))

    # removing an agent moves the last row into its place
    boid.remove()
    assert ground[(10, 10)].is_empty
    np.testing.assert_array_equal(other.position, [9.0, 9.0])
    other.position = [1.0, 1.0]
    assert ground.cell_of(other) is ground[(0, 0)]


def test_continuous_position_is_read_only():
    """In-place changes cannot bypass validation and other spaces."""
    model = Model(rng=1)
    space = ContinuousSpace([[0, 10], [0, 10]], random=model.random)
    agent = ContinuousSpaceAgent(space, model)
    agent.position = [1.0, 1.0]
    with pytest.raises(ValueError, match="read-only"):
        agent.position += 1.0
    with pytest.raises(ValueError, match="read-only"):
        agent.position[0] = 5.0
    np.testing.assert_array_equal(agent.position, [1.0, 1.0])
    agent.position = agent.position + 1.0
    np.testing.assert_array_equal(space.agent_positions, [[2.0, 2.0]])

    # the views survive growing and pickling the array
    for _ in range(200):
        ContinuousSpaceAgent(space, model).position = [3.0, 3.0]
    agent.position = [4.0, 4.0]
    np.testing.assert_array_equal(space.agent_positions[0], [4.0, 4.0])
    clone = copy.deepcopy(model)
    agent2 = next(iter(clone.agents))
    agent2.position = [5.0, 5.0]
    np.testing.assert_array_equal(agent2.space.agent_positions[0], [5.0, 5.0])
    np.testing.assert_array_equal(agent2.space._agent_positions[0], [5.0, 5.0])


def test_membership_errors():
    """Joining twice or joining without a location fails clearly."""
    model = stacked_model()
    air, ground = model.air, model.ground
    bird = Bird(model)
    with pytest.raises(ValueError, match="pass a cell"):
        ground.add(bird)
    with pytest.raises(ValueError, match="pass a position"):
        air.add(bird)
    with pytest.raises(ValueError, match="not in a space"):
        model.physical.move(bird, [1.0, 1.0])
    assert bird._mesa_locations is None

    air.add(bird, [1.0, 1.0])
    ground.add(bird)
    with pytest.raises(ValueError, match="already in this"):
        ground.add(bird)
    with pytest.raises(ValueError, match="already in a continuous space"):
        air.add(bird)
    # agent.cell stays tied to one space once the agent is in several
    other = OrthogonalMooreGrid((2, 2), random=model.random)
    cell_agent = CellAgent(model)
    cell_agent.cell = ground[(0, 0)]
    air.add(cell_agent)
    with pytest.raises(ValueError, match="use space\\.move"):
        cell_agent.cell = other[(0, 0)]
    assert cell_agent.cell is ground[(0, 0)]
    assert other[(0, 0)].is_empty

    air.remove(bird)
    np.testing.assert_array_equal(bird.position, [1.0, 1.0])
    assert len(air.agent_positions) == 1  # the cell agent
    ground.remove(bird)
    assert bird.position is None
    assert bird._mesa_locations is None


# ----------------------------------------------------------------------
# The core invariant
# ----------------------------------------------------------------------
def snapshot(model):
    """Everything a failed write must leave untouched."""
    state = {}
    for frame in model.frames:
        for i, space in enumerate(frame.spaces):
            if isinstance(space, DiscreteSpace):
                state[frame.name, i] = {
                    cell.coordinate: [a.unique_id for a in cell._agents]
                    for cell in space.all_cells
                }
            else:
                state[frame.name, i] = (
                    space.agent_positions.copy(),
                    [a.unique_id for a in space.active_agents],
                )
        for agent in model.agents:
            location = frame.location_of(agent)
            state[frame.name, agent.unique_id] = (
                None if location is None else location.copy()
            )
    return state


def assert_same(before, after):
    """Compare two snapshots."""
    assert before.keys() == after.keys()
    for key, value in before.items():
        other = after[key]
        if isinstance(value, tuple):
            np.testing.assert_array_equal(value[0], other[0])
            assert value[1] == other[1]
        elif isinstance(value, np.ndarray):
            np.testing.assert_array_equal(value, other)
        else:
            assert value == other


def assert_consistent(model):
    """Every member space agrees with the location of every agent."""
    for frame in model.frames:
        for agent in model.agents:
            location = frame.location_of(agent)
            in_any = False
            for space in frame.spaces:
                if isinstance(space, DiscreteSpace):
                    holding = [c for c in space.all_cells if agent in c._agents]
                    cell = space.cell_of(agent)
                    if cell is None:
                        assert holding == []
                        continue
                    in_any = True
                    assert holding == [cell]
                    assert cell._agents.count(agent) == 1
                    assert space.find_nearest_cell(location) is cell
                else:
                    rows = [a for a in space.active_agents if a is agent]
                    if not rows:
                        continue
                    in_any = True
                    assert len(rows) == 1
                    index = space._indices([agent])[0]
                    assert space.active_agents[index] is agent
                    np.testing.assert_array_equal(
                        space.agent_positions[index], location
                    )
                    assert space.in_bounds(location)
            assert (location is not None) == in_any
            # the bookkeeping holds no half-finished memberships
            for record in (agent._mesa_locations or {}).values():
                assert None not in record.cells.values()
                assert not record.is_empty
            if isinstance(agent, CellAgent) and agent.cell is not None:
                # agent.cell mirrors the agent's cell in exactly one space
                homes = [
                    s
                    for s in frame.spaces
                    if isinstance(s, DiscreteSpace) and s._owns(agent.cell)
                ]
                assert len(homes) == 1
                assert homes[0].cell_of(agent) is agent.cell

        for space in frame.spaces:
            if isinstance(space, DiscreteSpace):
                for cell in space.all_cells:
                    assert cell.capacity is None or len(cell._agents) <= cell.capacity
                    assert cell.empty == cell.is_empty
            else:
                assert len(space.agent_positions) == len(space.active_agents)


def build(config, seed):
    """Create a model with one frame holding several spaces."""
    model = Model(rng=seed)
    rng = model.random
    frame = Frame("physical", ndim=2)
    model.frames = [frame]
    if config == "torus":
        ContinuousSpace([[0, 12], [0, 12]], torus=True, random=rng, frame=frame)
        OrthogonalMooreGrid(
            (6, 6), torus=True, capacity=2, random=rng, frame=frame, cell_size=2.0
        )
        OrthogonalVonNeumannGrid(
            (4, 3), torus=True, random=rng, frame=frame, cell_size=(3.0, 4.0)
        )
        model.extent = (-15.0, 30.0)
    elif config == "bounded":
        ContinuousSpace([[0, 10], [0, 10]], random=rng, frame=frame)
        OrthogonalMooreGrid((5, 5), capacity=1, random=rng, frame=frame, cell_size=2.0)
        VoronoiGrid(
            [(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(6)],
            capacity=3,
            random=rng,
            frame=frame,
        )
        # covers only the middle of the frame, so some writes fall outside it
        OrthogonalMooreGrid(
            (4, 4), random=rng, frame=frame, cell_size=1.5, origin=(2.0, 2.0)
        )
        model.extent = (-1.0, 11.0)
    elif config == "discrete":
        OrthogonalMooreGrid((5, 5), capacity=2, random=rng, frame=frame, cell_size=0.4)
        VoronoiGrid(
            [(rng.uniform(0, 2), rng.uniform(0, 2)) for _ in range(5)],
            capacity=4,
            random=rng,
            frame=frame,
        )
        model.extent = (-0.2, 2.2)
    elif config == "hex":
        width = 6 * math.sqrt(3)
        ContinuousSpace([[0, width], [0, 9]], torus=True, random=rng, frame=frame)
        HexGrid((6, 6), torus=True, capacity=2, random=rng, frame=frame)
        model.extent = (-10.0, 20.0)
    model.frame = frame
    return model


def random_point(model):
    """A point that is sometimes outside the spaces."""
    low, high = model.extent
    return [model.random.uniform(low, high), model.random.uniform(low, high)]


def spawn(model):
    """Create an agent of a random kind, in a random subset of the spaces."""
    rng = model.random
    continuous = [s for s in model.frame.spaces if not isinstance(s, DiscreteSpace)]
    kind = rng.choice(["bird", "cell", "continuous" if continuous else "bird"])
    if kind == "continuous":
        agent = ContinuousSpaceAgent(continuous[0], model)
        agent.position = continuous[0].torus_correct(random_point(model))
    elif kind == "cell":
        agent = CellAgent(model)
    else:
        agent = Bird(model)
    return agent


def random_operation(model):
    """Apply one random operation, which may be rejected with an exception."""
    rng = model.random
    frame = model.frame
    discrete = [s for s in frame.spaces if isinstance(s, DiscreteSpace)]
    agents = list(model.agents)

    roll = rng.random()
    if roll < 0.08 or len(agents) < 3:
        spawn(model)
        return
    agent = rng.choice(agents)
    if roll < 0.12:
        agent.remove()
    elif roll < 0.40:  # point write
        point = random_point(model)
        if rng.random() < 0.6 and isinstance(agent, Bird | ContinuousSpaceAgent):
            agent.position = point
        else:
            frame.move(agent, point)
    elif roll < 0.48 and isinstance(agent, ContinuousSpaceAgent):  # relative move
        agent.position = agent.position + np.array(
            [rng.uniform(-3, 3), rng.uniform(-3, 3)]
        )
    elif roll < 0.70:  # cell move
        space = rng.choice(discrete)
        cell = rng.choice(list(space.all_cells))
        if isinstance(agent, CellAgent) and rng.random() < 0.5:
            agent.cell = cell
        else:
            space.move(agent, cell)
    elif roll < 0.85:  # join
        space = rng.choice(frame.spaces)
        if space in discrete:
            cell = rng.choice(list(space.all_cells)) if rng.random() < 0.5 else None
            space.add(agent, cell)
        else:
            space.add(agent, random_point(model) if rng.random() < 0.5 else None)
    else:  # leave
        space = rng.choice(frame.spaces)
        if isinstance(agent, CellAgent) and rng.random() < 0.3:
            agent.cell = None
        else:
            space.remove(agent)


@pytest.mark.parametrize("config", ["torus", "bounded", "discrete", "hex"])
@pytest.mark.parametrize("seed", range(12))
def test_invariant_random_operations(config, seed):
    """After any sequence of operations, all spaces agree with every location.

    Operations that are rejected (full cells, points outside a space, joining
    twice, moving in a space the agent is not in) must change nothing.
    """
    model = build(config, seed)
    accepted = rejected = 0
    for _ in range(250):
        before = snapshot(model)
        n_agents = len(model.agents)
        try:
            random_operation(model)
        except (CellFullException, ValueError):
            rejected += 1
            assert len(model.agents) == n_agents
            assert_same(before, snapshot(model))
        else:
            accepted += 1
        assert_consistent(model)

    # the sequence must exercise both outcomes to mean anything
    assert accepted > 50
    assert rejected > 20
