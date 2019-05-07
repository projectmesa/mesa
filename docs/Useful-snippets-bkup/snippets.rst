Useful Snippets
===============

A collection of useful code snippets. Here you can find code that allows you to get to get started on common tasks in Mesa.

Models with Discrete Time
-------------------------
If you have `Multiple` type agents and one of them has time attribute you can still build a model that is run by discrete time. In this example, each step of the model, and the agents have a time attribute that is equal to the discrete time to run its own step.

.. code:: python

if self.model.schedule.time in self.discrete_time:
  self.model.space.move_agent(self, new_pos)
