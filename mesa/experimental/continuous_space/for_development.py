# to be removed once further into the development
from random import Random

import numpy as np
from continuous_space import ContinuousSpace
from continuous_space_agents import ContinuousSpaceAgent

from mesa import Model

if __name__ == "__main__":
    dimensions = [[0, 1], [0, 1]]

    model = Model(seed=42)
    space = ContinuousSpace(dimensions, random=Random(42), torus=True)

    for _ in range(2):
        agent = ContinuousSpaceAgent(
            space,
            model,
        )
        agent.position = [agent.random.random(), agent.random.random()]

    distances = space.calculate_distances(np.asarray([0.5, 0.5]))

    print("blaat")
