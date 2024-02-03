from collections import defaultdict

import pandas as pd


class DataCollector:
    """
    Example: a model consisting of a hybrid of Boltzmann wealth model and
    Epstein civil violence.
    ```
    groups = {
        "quiescents": lambda model: model.agents.select(
            agent_type=Citizen, filter_func=lambda a: a.condition == "Quiescent"
        ),
        "citizens": lambda model: model.get_agents_of_type(Citizen),
        # These are available by default. Your custom specification of these
        # will be ignored.
        "agents": lambda model: model.agents
        "model": lambda model: model
    }

    collectors = {
        ("n_quiescent", "quiescents"): len,
        ("gini", "model"): lambda model: calculate_gini(model.agents.get("wealth")),
        # A better way to do the former:
        ("gini", "agents"): lambda agents: calculate_gini(agents.get("wealth")),
        ("gini_quiescent", "quiescents"): lambda agents: calculate_gini(
            agents.get("wealth")
        ),
        ("condition", "citizens"): "condition",
        # "agents" is a string, because model.agents may refer to a different
        # object, over time, when accessed from scratch each time.
        ("wealth", "agents"): "wealth",
    }

    # Then finally
    model.datacollector = DataCollector(model, groups=groups, collectors=collectors).collect()
    ```
    """

    def __init__(self, model, groups=None, collectors=None) -> "DataCollector":
        self.model = model
        self.groups = groups
        self.collectors = collectors
        self.data_collection = defaultdict(list)
        return self

    def collect(self) -> "DataCollector":
        group_data = defaultdict(dict)
        for (name, group), collector in self.collectors.items():
            group_object = group
            if group == "agents":
                group_object = self.model.agents
            elif group == "model":
                group_object = self.model
            elif callable(group):
                group_object = group(self.model)
            elif isinstance(group, str):
                group_object = self.groups[group]

            group_data[group][name] = self._collect_group(group_object, collector)

        for group, data in group_data.items():
            self.data_collection[group].append(data)
        return self

    def _collect_group(self, group, collector):
        def _get_or_apply(obj, value):
            # get
            if isinstance(value, str):
                return getattr(obj, value)
            # apply
            return value(obj)

        if group is self.model:
            return {
                name: _get_or_apply(group, value) for name, value in collector.items()
            }
        return {
            name: [_get_or_apply(e, value) for e in group]
            for name, value in collector.items()
        }

    def to_df(self, group=None):
        if group is None:
            return {
                group: pd.DataFrame(data_list)
                for group, data_list in self.data_collection.items()
            }
        return pd.DataFrame(self.data_collection[group])
