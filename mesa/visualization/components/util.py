from collections.abc import Callable

from mesa.experimental.cell_space import DiscreteSpace
from mesa.space import ContinuousSpace, NetworkGrid, _Grid, _HexGrid

__all__ = [
    "get_agent_continuous",
    "get_agents_olstyle_grid",
    "get_agents_newstyle_grid",
]

OldStyleSpace = _Grid | ContinuousSpace | _HexGrid | NetworkGrid
Space = OldStyleSpace | DiscreteSpace


def get_agents_olstyle_space(space: OldStyleSpace):
    for entry in space:
        if entry:
            yield entry


def get_agents_newstyle_space(space: DiscreteSpace):
    yield from space.all_cells.agents


def _get_oldstyle_agent_data(agents, agent_portrayal):
    """Helper function to get agent data for visualization."""
    x, y, s, c, m = [], [], [], [], []
    for agent in agents:
        data = agent_portrayal(agent)
        x.append(pos[0] + 0.5)  # Center the agent in the cell
        y.append(pos[1] + 0.5)  # Center the agent in the cell
        default_size = (180 / max(space.width, space.height)) ** 2
        s.append(data.get("size", default_size))
        c.append(data.get("color", "tab:blue"))
        m.append(data.get("shape", "o"))
    return {"x": x, "y": y, "s": s, "c": c, "m": m}


# fixme:
#  how we get the data depends on the space and I don't like it.
#  can't we separate more cleanly the data and any post
#  space specific refinements?
#  or gather data depending on the space?
# fixme:
#  what routes do we have?
#  network (2 options)
#  continuous (1 option)
#  orthogonal grids (7 options?)
#  voronoi (1 option)


def get_agent_data(space: Space, agent_portrayal: Callable):
    # fixme should we cover networks here at all?

    match space:
        case _Grid():  # matches also hexgrids
            agents = get_agents_olstyle_space(space)
        case ContinuousSpace():
            agents = get_agents_olstyle_space(space)
        case NetworkGrid():
            agents = get_agents_olstyle_space(space)
        case DiscreteSpace():
            agents = get_agents_newstyle_space(space)
        case _:
            raise NotImplementedError(f"Unknown space of type {type(space)}")

    x, y, s, c, m = [], [], [], [], []
    for agent in agents:
        data = agent_portrayal(agent)

        if isinstance(space, DiscreteSpace):
            x_i, y_i = agent.cell.coordinate
        else:
            x_i, y_i = agent.pos

        x.append(x_i)
        y.append(y_i)
        s.append(
            data.get("size", None)
        )  # we use None here as a flag to fall back on default
        c.append(data.get("color", "tab:blue"))
        m.append(data.get("shape", "o"))


if __name__ == "__main__":
    from mesa import Agent, Model
    from mesa.experimental.cell_space import CellAgent, OrthogonalMooreGrid
    from mesa.space import SingleGrid

    model = Model()
    space = SingleGrid(10, 10, True)
    for _ in range(10):
        agent = Agent(model)
        pos = model.random.choice(list(space.empties))
        space.place_agent(agent, pos)

    agents = list(get_agents_olstyle_space(space))
    assert len(agents) == 10

    model = Model()
    space = OrthogonalMooreGrid((10, 10), capacity=1, torus=True, random=model.random)
    for _ in range(10):
        agent = CellAgent(model)
        cell = space.select_random_empty_cell()
        agent.cell = cell

    agents = list(get_agents_newstyle_space(space))
    assert len(agents) == 10

    model = Model()
    space = ContinuousSpace(10, 10, True)
    for _ in range(10):
        agent = Agent(model)
        pos = (
            agent.random.random() * space.width,
            agent.random.random() * space.height,
        )
        space.place_agent(agent, pos)

    agents = list(get_agents_olstyle_space(space))
    assert len(agents) == 10
