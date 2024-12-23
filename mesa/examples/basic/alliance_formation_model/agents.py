import mesa


def calculate_shapley_value(self, other_agent):
    """
    Calculate the Shapley value of the two agents
    """
    other_agent.hierarchy = other_agent.hierarchy
    self.hierarchy = self.hierarchy
    new_position = 1 - abs(self.position - other_agent.position)
    potential_utility = (self.power + other_agent.power) * 1.1 * new_position
    value_me = 0.5 * self.power + 0.5 * (potential_utility - other_agent.power)
    value_other = 0.5 * other_agent.power + 0.5 * (potential_utility - self.power)

    # Determine ig there is value in the alliance
    if value_me > self.power and value_other > other_agent.power:
        if other_agent.hierarchy > self.hierarchy:
            hierarchy = other_agent.hierarchy
        elif other_agent.hierarchy == self.hierarchy:
            hierarchy = self.hierarchy + 1
        else:
            hierarchy = self.hierarchy

        return (potential_utility, new_position, hierarchy)
    else:
        return None


class AllianceAgent(mesa.Agent):
    """
    Agent has three attributes power (float), position (float) and hierarchy (int)

    """

    def __init__(self, model, power, position, hierarchy=0):
        super().__init__(model)
        self.power = power
        self.position = position
        self.hierarchy = hierarchy

    def form_alliance(self):
        # Randomly select another agent of the same type
        other_agents = [
            agent for agent in self.model.agents_by_type[type(self)] if agent != self
        ]

        # Determine if there is a beneficial alliance
        if other_agents:
            other_agent = self.random.choice(other_agents)
            shapley_value = calculate_shapley_value(self, other_agent)
            if shapley_value:
                class_name = f"MetaAgentHierarchy{shapley_value[2]}"
                meta = self.create_metaagent(
                    class_name,
                    {other_agent, self},
                    hierarchy=shapley_value[2],
                    power=shapley_value[0],
                    position=shapley_value[1],
                )

                # Update the network if a new meta agent instance created
                if meta:
                    self.model.network.add_node(
                        meta.unique_id, size=(meta.hierarchy + 1) * 200
                    )
                    self.model.new_agents = True
                else:
                    self.model.new_agents = False
