import mesa
import numpy as np
import perfplot
import itertools


# Mesa implementation
def mesa_original_implementation(n_agents: int) -> None:
    model = MoneyModel(n_agents)
    model.run_model(100)


class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)

        # Create the agent's variable and set the initial values.
        self.wealth = 1

    def step(self):
        # Verify agent has some wealth
        if self.wealth > 0:
            other_agent = self.random.choice(list(itertools.chain.from_iterable(self.model.agents_by_type.values())))
            if other_agent is not None:
                other_agent.wealth += 1
                self.wealth -= 1


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N):
        super().__init__()
        self.num_agents = N
        # Create scheduler and assign it to the model
        self.schedule = mesa.time.RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.add(a)

    def step(self):
        """Advance the model by one step."""

        # The model's step will go here for now this will call the step method of each agent and print the agent's unique_id
        self.schedule.step()

    def run_model(self, n_steps) -> None:
        for _ in range(n_steps):
            self.step()



def mesa_test_implementation(n_agents: int) -> None:
    model = MoneyTestModel(n_agents)
    model.run_model(100)


class MoneyTestAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)

        # Create the agent's variable and set the initial values.
        self.wealth = 1

    def step(self):
        # Verify agent has some wealth
        if self.wealth > 0:
            other_agent = self.random.choice(self.model.my_agents)
            if other_agent is not None:
                other_agent.wealth += 1
                self.wealth -= 1


class MoneyTestModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N):
        super().__init__()
        self.num_agents = N
        # Create scheduler and assign it to the model
        self.schedule = mesa.time.RandomActivation(self)
        self.my_agents = []

        # Create agents
        for i in range(self.num_agents):
            a = MoneyTestAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.add(a)
            self.my_agents.append(a)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()

    def run_model(self, n_steps) -> None:
        for _ in range(n_steps):
            self.step()


# Mesa Frames implementation
def mesa_list_implementation(n_agents: int) -> None:
    model = MoneyListModel(n_agents)
    model.run_model(100)

class MoneyListModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N):
        super().__init__()
        self.num_agents = N
        # Create scheduler and assign it to the model
        self.schedule = []

        # Create agents
        for i in range(self.num_agents):
            a = MoneyListAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.append(a)

    def step(self):
        """Advance the model by one step."""
        self.random.shuffle(self.schedule)
        for agent in self.schedule:
            agent.step()

    def run_model(self, n_steps) -> None:
        for _ in range(n_steps):
            self.step()

class MoneyListAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)

        # Create the agent's variable and set the initial values.
        self.wealth = 1

    def step(self):
        # Verify agent has some wealth
        if self.wealth > 0:
            other_agent = self.random.choice(self.model.schedule)
            if other_agent is not None:
                other_agent.wealth += 1
                self.wealth -= 1

def main():
    out = perfplot.bench(
        setup=lambda n: n,
        kernels=[mesa_original_implementation, mesa_test_implementation, mesa_list_implementation],
        labels=["itertools", "test", "list"],
        n_range=[k for k in range(10, 1000, 500)],
        xlabel="Number of agents",
        equality_check=None,
        title="100 steps of the Boltzmann Wealth model",
    )
    out.show()
    out.save("readme_plot4.png")


if __name__ == "__main__":
    main()