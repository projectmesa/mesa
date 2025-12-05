"""Comprehensive tests for unified time and event scheduling API."""

import pytest

from mesa import Agent, Model
from mesa.experimental.devs import Priority


class TestEventScheduling:
    """Test core event scheduling functionality."""

    def test_schedule_at_absolute_time(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append(5), at=5.0)
        model.schedule(lambda: results.append(10), at=10.0)

        model.run(until=15)
        assert results == [5, 10]
        assert model.time == 15.0

    def test_schedule_after_relative_time(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append("a"), after=2.0)
        model.schedule(lambda: results.append("b"), after=5.0)

        model.run(until=10)
        assert results == ["a", "b"]

    def test_schedule_with_args_kwargs(self):
        model = Model()
        results = []

        def callback(x, y=0):
            results.append(x + y)

        model.schedule(callback, at=5.0, args=[10], kwargs={"y": 20})
        model.run(until=10)

        assert results == [30]

    def test_exactly_one_of_at_or_after_required(self):
        model = Model()

        with pytest.raises(ValueError, match="exactly one"):
            model.schedule(lambda: None)

        with pytest.raises(ValueError, match="exactly one"):
            model.schedule(lambda: None, at=5, after=5)

    def test_cannot_schedule_in_past(self):
        model = Model()
        model.time = 10.0

        with pytest.raises(ValueError, match="past"):
            model.schedule(lambda: None, at=5.0)

    def test_event_cancellation(self):
        model = Model()
        results = []

        event1 = model.schedule(lambda: results.append(1), at=5.0)
        model.schedule(lambda: results.append(2), at=10.0)

        model.cancel(event1)
        model.run(until=15)

        assert results == [2]

    def test_event_at_current_time(self):
        model = Model()
        results = []
        model.time = 5.0

        model.schedule(lambda: results.append("now"), at=5.0)
        model.run(until=10)

        assert results == ["now"]


class TestEventPriority:
    """Test event priority system."""

    def test_priority_ordering_same_time(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append("default"), at=5.0)
        model.schedule(lambda: results.append("high"), at=5.0, priority=Priority.HIGH)
        model.schedule(lambda: results.append("low"), at=5.0, priority=Priority.LOW)

        model.run(until=10)
        assert results == ["high", "default", "low"]

    def test_priority_with_arguments(self):
        model = Model()
        results = []

        def callback(val):
            results.append(val)

        model.schedule(callback, at=5.0, args=[1])
        model.schedule(callback, at=5.0, args=[2], priority=Priority.HIGH)
        model.schedule(callback, at=5.0, args=[3], priority=Priority.LOW)

        model.run(until=10)
        assert results == [2, 1, 3]


class TestRunMethods:
    """Test different run() termination conditions."""

    def test_run_until(self):
        model = Model()
        model.schedule(lambda: None, at=5.0)

        model.run(until=10.0)
        assert model.time == 10.0

    def test_run_duration(self):
        model = Model()
        model.time = 5.0
        model.schedule(lambda: None, at=8.0)

        model.run(duration=10.0)
        assert model.time == 15.0

    def test_run_steps_with_step_method(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1

        model = StepModel()
        model.run(steps=5)

        assert model.steps == 5
        assert model.time == 5.0
        assert model.count == 5

    def test_run_condition(self):
        class ConditionalModel(Model):
            def __init__(self):
                super().__init__()
                self.counter = 0

            def step(self):
                self.counter += 1
                if self.counter >= 3:
                    self.running = False

        model = ConditionalModel()
        model.run(condition=lambda m: m.running)

        assert model.counter == 3

    def test_run_requires_at_least_one_argument(self):
        model = Model()

        with pytest.raises(ValueError, match="at least one"):
            model.run()

    def test_run_until_stops_when_no_events(self):
        model = Model()

        model.run(until=100.0)
        assert model.time == 100.0


class TestLegacyStepBehavior:
    """Test backward compatibility with step-based models."""

    def test_step_increments_time_and_counter(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.user_counter = 0

            def step(self):
                self.user_counter += 1

        model = StepModel()
        model.step()

        assert model.steps == 1
        assert model.time == 1.0
        assert model.user_counter == 1

    def test_manual_step_loop(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.user_counter = 0

            def step(self):
                self.user_counter += 1

        model = StepModel()
        for _ in range(10):
            model.step()

        assert model.steps == 10
        assert model.time == 10.0
        assert model.user_counter == 10

    def test_run_steps_calls_step_n_times(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.calls = []

            def step(self):
                self.calls.append(self.time)

        model = StepModel()
        model.run(steps=3)

        assert model.calls == [1.0, 2.0, 3.0]

    def test_run_until_with_step(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1

        model = StepModel()
        model.run(until=5.0)

        assert model.time == 5.0
        assert model.count == 5

    def test_run_duration_with_step(self):
        class StepModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1

        model = StepModel()
        model.time = 10.0
        model.run(duration=5.0)

        assert model.time == 15.0
        assert model.count == 5


class TestMixedStepAndEvents:
    """Test combining step() with scheduled events."""

    def test_step_with_scheduled_events(self):
        class MixedModel(Model):
            def __init__(self):
                super().__init__()
                self.step_calls = 0
                self.event_calls = 0

            def step(self):
                self.step_calls += 1

            def event(self):
                self.event_calls += 1

        model = MixedModel()
        model.schedule(model.event, at=5.0)
        model.run(steps=10)

        # When events are scheduled, scheduler takes over
        # Step is not auto-called in event-driven mode
        assert model.event_calls == 1

    def test_scheduling_during_step(self):
        class DynamicModel(Model):
            def __init__(self):
                super().__init__()
                self.events = []

            def step(self):
                if self.steps == 3:
                    self.schedule(lambda: self.events.append("dynamic"), at=7.0)

        model = DynamicModel()
        model.schedule(lambda: model.events.append("static"), at=5.0)
        model.run(steps=10)

        assert "static" in model.events
        assert "dynamic" in model.events


class TestAgentScheduling:
    """Test agents scheduling their own events."""

    def test_agent_schedules_callback(self):
        class SchedulingAgent(Agent):
            def __init__(self, model):
                super().__init__(model)
                self.wakeups = 0

            def wakeup(self):
                self.wakeups += 1

        model = Model()
        agent = SchedulingAgent(model)

        model.schedule(agent.wakeup, at=5.0)
        model.schedule(agent.wakeup, at=10.0)

        model.run(until=15)
        assert agent.wakeups == 2

    def test_agent_recursive_scheduling(self):
        class RecursiveAgent(Agent):
            def __init__(self, model):
                super().__init__(model)
                self.ticks = 0

            def tick(self):
                self.ticks += 1
                if self.ticks < 5:
                    self.model.schedule(self.tick, after=1.0)

        model = Model()
        agent = RecursiveAgent(model)
        model.schedule(agent.tick, at=0.0)

        model.run(until=10)
        assert agent.ticks == 5


class TestPureEventDriven:
    """Test pure event-driven simulation without step()."""

    def test_model_without_step(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append(1), at=5.0)
        model.schedule(lambda: results.append(2), at=10.0)
        model.schedule(lambda: results.append(3), at=15.0)

        model.run(until=20)

        assert results == [1, 2, 3]
        assert model.time == 20.0
        assert model.steps == 0  # No step() called

    def test_discrete_event_simulation_pattern(self):
        class QueueModel(Model):
            def __init__(self):
                super().__init__()
                self.arrivals = 0

            def arrival(self):
                self.arrivals += 1
                if self.arrivals < 5:
                    delay = self.random.expovariate(2.0)
                    self.schedule(self.arrival, after=delay)

        model = QueueModel()
        model.schedule(model.arrival, at=0.0)
        model.run(until=100)

        assert model.arrivals == 5

    def test_time_jumps_between_events(self):
        model = Model()
        times = []

        model.schedule(lambda: times.append(model.time), at=5.0)
        model.schedule(lambda: times.append(model.time), at=50.0)
        model.schedule(lambda: times.append(model.time), at=100.0)

        model.run(until=150)

        assert times == [5.0, 50.0, 100.0]


class TestTimeAdvancement:
    """Test time advancement behavior."""

    def test_time_only_advances_to_events_or_end(self):
        model = Model()

        model.schedule(lambda: None, at=10.0)
        model.run(until=50)

        assert model.time == 50.0

    def test_fractional_time(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append(model.time), at=0.5)
        model.schedule(lambda: results.append(model.time), at=1.5)
        model.schedule(lambda: results.append(model.time), at=2.5)

        model.run(until=3.0)
        assert results == [0.5, 1.5, 2.5]

    def test_multiple_events_same_time(self):
        model = Model()
        results = []

        for i in range(5):
            model.schedule(lambda x=i: results.append(x), at=5.0)

        model.run(until=10)

        assert len(results) == 5
        assert sorted(results) == [0, 1, 2, 3, 4]


class TestRunConditions:
    """Test run() with various stopping conditions."""

    def test_condition_stops_execution(self):
        class ConditionalModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1
                if self.count >= 5:
                    self.running = False

        model = ConditionalModel()
        model.run(condition=lambda m: m.running)

        assert model.count == 5
        assert not model.running

    def test_condition_false_immediately(self):
        class ImmediateStop(Model):
            def step(self):
                pass

        model = ImmediateStop()
        model.running = False

        model.run(condition=lambda m: m.running)

        assert model.steps == 0

    def test_multiple_conditions(self):
        class MultiCondModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1

        model = MultiCondModel()

        # Should stop at 3 steps OR time 10, whichever first
        model.run(steps=10, condition=lambda m: m.count < 3)

        assert model.count == 3


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_event_list_with_until(self):
        model = Model()
        model.run(until=10.0)
        assert model.time == 10.0

    def test_cancel_last_event(self):
        model = Model()
        event = model.schedule(lambda: None, at=5.0)
        model.cancel(event)

        model.run(until=10)
        assert model.time == 10.0

    def test_event_beyond_end_time(self):
        model = Model()
        results = []

        model.schedule(lambda: results.append(5), at=5.0)
        model.schedule(lambda: results.append(100), at=100.0)

        model.run(until=50)

        assert results == [5]
        assert 100 not in results


class TestDeprecations:
    """Test deprecated features."""

    def test_run_model_deprecated(self):
        class StoppingModel(Model):
            def __init__(self):
                super().__init__()
                self.count = 0

            def step(self):
                self.count += 1
                if self.count >= 3:
                    self.running = False

        model = StoppingModel()

        with pytest.warns(DeprecationWarning, match="run_model"):
            model.run_model()

        assert model.count == 3
