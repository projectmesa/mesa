from collections import defaultdict

import pandas as pd


class DataCollector:
    """
    Example: a model consisting of a hybrid of Boltzmann wealth model and
    Epstein civil violence.
    ```
    def get_citizen():
        return model.get_agents_of_type(Citizen)

    collectors = {
        model: {
            "n_quiescent": lambda model: len(
                model.agents.select(
                    agent_type=Citizen,
                    filter_func=lambda a: a.condition == "Quiescent"
                )
            ),
            "gini": lambda model: calculate_gini(model.agents.get("wealth"))
        },
        get_citizen: {"condition": condition},
        # This is a string, because model.agents may refer to a different
        # object, over time.
        "agents": {"wealth": "wealth"}
    }
    # Then finally
    model.datacollector = DataCollector(model, collectors=collectors).collect()
    ```
    """

    def __init__(self, model, collectors=None) -> "DataCollector":
        self.model = model
        self.collectors = collectors
        self.data_collection = defaultdict(list)
        return self

    def collect(self) -> "DataCollector":
        for group, group_collector in self.collectors.items():
            group_object = group
            if group == "agents":
                group_object = self.model.agents
            elif callable(group):
                group_object = group()
            data = {
                name: self._collect_group(group_object, collector)
                for name, collector in group_collector.items()
            }
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
