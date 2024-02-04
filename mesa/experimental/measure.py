from collections import defaultdict


class Group:
    def __init__(self, model, fn):
        self.model = model
        self.fn = fn

    @property
    def value(self):
        return self.fn(self.model)


class Measure:
    def __init__(self, group, measurer):
        self.group = group
        self.measurer = measurer

    def _measure_group(self, group, measurer):
        # get an attribute
        if isinstance(measurer, str):
            return getattr(group, measurer)
        # apply
        return measurer(group)

    @property
    def value(self):
        group_object = self.group
        if isinstance(self.group, Group):
            group_object = self.group.value
        return self._measure_group(group_object, self.measurer)


class DataCollector:
    """
    Example: a model consisting of a hybrid of Boltzmann wealth model and
    Epstein civil violence.

    class EpsteinBoltzmannModel:
        def __init__(self):
            # Groups
            self.quiescents = Group(
                lambda model: model.agents.select(
                    agent_type=Citizen, filter_func=lambda a: a.condition == "Quiescent"
                )
            )
            self.citizens = Group(lambda model: model.get_agents_of_type(Citizen))

            # Measurements
            self.num_quiescents = Measure(self.quiescents, len)
            self.gini = Measure(
                self.agents, lambda agents: calculate_gini(agents.get("wealth"))
            )
            self.gini_quiescents = Measure(
                self.quiescents, lambda agents: calculate_gini(agents.get("wealth"))
            )
            self.condition = Measure(self.citizens, "condition")
            self.wealth = Measure(self.agents, "wealth")


    def run():
        model = EpsteinBoltzmannModel()
        datacollector = DataCollector(
            model, ["num_quiescents", "gini_quiescents", "wealth"]
        )

        for _ in range(10):
            model.step()
            datacollector.collect()
    """

    def __init__(self, model, attributes):
        self.model = model
        self.attributes = attributes
        self.data_collection = defaultdict(lambda: defaultdict(list))

    def collect(self):
        for name in self.attributes:
            attribute = getattr(self.model, name)
            group = "model"
            if isinstance(attribute, Measure):
                group = attribute.group
                attribute = attribute.value
            self.data_collection[group][name].append(attribute)
