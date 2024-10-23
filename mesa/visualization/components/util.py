from mesa.space import _Grid, ContinuousSpace
from mesa.experimental.cell_space import DiscreteSpace


def get_agents_olstyle_grid(space: _Grid):
    for entry in space:
        if entry:
            yield entry


def get_agents_newstyle_grid(space: DiscreteSpace):
    for agent in space.all_cells.agents:
        yield agent

def get_agent_continuous(space: ContinuousSpace):
    pass
