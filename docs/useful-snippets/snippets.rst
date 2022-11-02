Useful Snippets
===============

A collection of useful code snippets. Here you can find code that allows you to get to get started on common tasks in Mesa.

Models with Discrete Time
-------------------------
If you have `Multiple` type agents and one of them has time attribute you can still build a model that is run by discrete time. In this example, each step of the model, and the agents have a time attribute that is equal to the discrete time to run its own step.

.. code:: python

  if self.model.schedule.time in self.discrete_time:
      self.model.space.move_agent(self, new_pos)


Using ```numpy.random```
-------------

Sometimes you need to use ``numpy``'s ``random`` library, for example to get a Poisson distribution.

.. code:: python

  class MyModel(Model):
      def __init__(self, ...):
          super().__init__()
          self.random = np.random.default_rng(seed)

And just use `numpy`'s random as usual, e.g. ``self.random.poisson()``.

Using multi-process ```batch_run``` on Windows
-------------

You will have an issue with `batch_run` and `number_processes = None`. Your cell will
show no progress, and in your terminal you will receive *AttributeError: Can't get attribute 'MoneyModel' on
<module '__main__' (built-in)>*. One way to overcome this is to take your code outside of Jupyter and adjust the above
code as follows.


.. code:: python

    from multiprocessing import freeze_support

    params = {"width": 10, "height": 10, "N": range(10, 500, 10)}

    if __name__ == '__main__':
        freeze_support()
        results = batch_run(
                MoneyModel,
                parameters=params,
                iterations=5,
                max_steps=100,
                number_processes=None,
                data_collection_period=1,
                display_progress=True,
        )


If you would still like to run your code in Jupyter you will need to adjust the cell as noted above. Then you can
you can add the `nbmultitask library <(https://nbviewer.org/github/micahscopes/nbmultitask/blob/39b6f31b047e8a51a0fcb5c93ae4572684f877ce/examples.ipynb)>`__
or look at this `stackoverflow <https://stackoverflow.com/questions/50937362/multiprocessing-on-python-3-jupyter>`__.

Using multiple schedules and data collectors
-------------

One may occasionally want multiple schedules with distinct sets of agents and collect data on each of those schedules independently while allowing the agents to interact in the same model. This would be particularly useful if the agents in your model do not all have the same attributes and you want to collect data on them in groups. You can create a simple scheduler class to mix the agents in each schedule and data collect on each schedule independently.

.. code:: python
  from random import shuffle

  # simple schedule mixer
  class ScheduleMixerRandom:
      def __init__(self, schedules: list):
          self.schedules = schedules

      def step(self):
          agents = []
          for s in self.schedules:
              agents.extend(s.agents)
          agents = shuffle(agents) # step through them randomly
          for a in agents:
              a.step()

  class MyModel(Model):
      def __init__(self, ...):
          super().__init__()
          self.schedule_one = BaseScheduler()
          self.schedule_two = BaseScheduler()

          # each DataCollector instance is associated with a specific schedule (and therefore its agents)
          self.datacollector_one = DataCollector(agent_reporters = {'value_one': 'value_one'}, schedule = self.schedule_one)
          self.datacollector_two = DataCollector(agent_reporters = {'value_two': 'value_two'}, schedule = self.schedule_two)

          self.schedule_mixer = ScheduleMixerRandom(schedules=[self.schedule_one, self.schedule_two])

      def step():
          self.schedule_mixer.step() # calls step() on each agent in both schedules, mixed together
          self.datacollector_one.collect(self) # collects data on the agents in schedule_one
          self.datacollector_two.collect(self) # collects data on the agents in schedule_two


To get the data at the end of the model, simply call:

.. code:: python
  schedule_one_agent_data = model.datacollector_one.get_agent_vars_dataframe()
  schedule_two_agent_data = model.datacollector_two.get_agent_vars_dataframe()
