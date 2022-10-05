from mesa.model import Model


def test_model_set_up():
    model = Model()
    assert model.running is True
    assert model.schedule is None
    assert model.current_id == 0
    assert model.current_id + 1 == model.next_id()
    assert model.current_id == 1
    model.step()


def test_running():
    class TestModel(Model):
        steps = 0

        def step(self):
            """Increase steps until 10."""
            self.steps += 1
            if self.steps == 10:
                self.running = False

    model = TestModel()
    model.run_model()


def test_seed(seed=23):
    model = Model(seed=seed)
    assert model._seed == seed
    model2 = Model(seed=seed + 1)
    assert model2._seed == seed + 1
    assert model._seed == seed


def test_reset_randomizer(newseed=42):
    model = Model()
    oldseed = model._seed
    model.reset_randomizer()
    assert model._seed == oldseed
    model.reset_randomizer(seed=newseed)
    assert model._seed == newseed
