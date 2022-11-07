from random import shuffle

# simple schedule mixer
class ScheduleMixerRandom:
    """
    Be careful: ScheduleMixerRandom as written here would not capture changes to
    the agent lists in the sub-schedules. The user would need to be mindful if
    this functionality were to be included.
    """

    def __init__(self, schedules):
        self._agents = {}
        for s in schedules:
            for a in s.agents:
                self._agents[
                    a.unique_id
                ] = a  # each agent must have a unique id across models

    def step(self):
        # do stuff with self._agents
        pass


class MyModel(Model):
    def __init__(self, args):
        super().__init__()
        self.schedule_one = BaseScheduler()
        self.schedule_two = BaseScheduler()

        # each DataCollector instance is associated with a specific schedule (and therefore its agents)
        self.datacollector_one = DataCollector(
            agent_reporters={"value_one": "value_one"}, schedule=self.schedule_one
        )
        self.datacollector_two = DataCollector(
            agent_reporters={"value_two": "value_two"}, schedule=self.schedule_two
        )

        self.schedule_mixer = ScheduleMixerRandom(
            schedules=[self.schedule_one, self.schedule_two]
        )

    def step():
        self.schedule_mixer.step()  # calls step() on each agent in both schedules, mixed together
        self.datacollector_one.collect(
            self
        )  # collects data on the agents in schedule_one
        self.datacollector_two.collect(
            self
        )  # collects data on the agents in schedule_two
