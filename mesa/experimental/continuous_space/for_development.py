"""to be removed once further into the development."""

if __name__ == "__main__":
    from mesa import Agent, Model
    from mesa.experimental.continuous_space import ContinuousSpace as NewStyleSpace
    from mesa.experimental.continuous_space import ContinuousSpaceAgent
    from mesa.space import ContinuousSpace as OldStyleSpace

    n = 400

    model = Model(rng=42)
    space = OldStyleSpace(100, 100, torus=True)

    positions = model.rng.random((n, 2)) * n
    for pos in positions:
        agent = Agent(model)
        space.place_agent(agent, pos)

    for _ in range(100):
        space.get_neighbors([50, 50], radius=5, include_center=False)

    model = Model(rng=42)
    space = NewStyleSpace(
        [[0, 100], [0, 100]], torus=True, random=model.random, n_agents=n
    )

    positions = model.rng.random((n, 2)) * n
    for pos in positions:
        agent = ContinuousSpaceAgent(space, model)
        agent.position = pos

    for _ in range(100):
        space.get_agents_in_radius([50, 50], radius=5)
