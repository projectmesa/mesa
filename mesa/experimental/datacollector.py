from collections import defaultdict

import pandas as pd


class DataCollector:
    def __init__(self, model, group_reporters, groups=None):
        self.model = model
        self.group_reporters = group_reporters
        self.groups = groups
        self.data = defaultdict(lambda: defaultdict(list))

    def get_group(self, group_name):
        if group_name == "model":
            return self.model
        elif group_name == "agents":
            return self.model.agents
        else:
            try:
                return getattr(self.model, group_name)
            except AttributeError as e:
                raise Exception(f"Unknown group: {group_name}") from e

    def report(self, reporter, group):
        if group is self.model:
            return reporter(group)
        if isinstance(reporter, str):
            if hasattr(group, "get"):
                return group.get(reporter)
            else:
                raise Exception()
        return reporter(group)

    def collect(self):
        for group_name, reporters in self.group_reporters.items():
            group = self.get_group(group_name)
            for name, reporter in reporters.items():
                value = self.report(reporter, group)
                self.data[group_name][name].append(value)

    def to_df(self, group_name):
        return pd.DataFrame(self.data[group_name])
