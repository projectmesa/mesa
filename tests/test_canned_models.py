from mesa.models import boltzmann_wealth_model


def test_boltzmann_wealth_model():
    model = boltzmann_wealth_model.BoltzmannWealthModel()
    assert model.running is True
    boltzmann_wealth_model.compute_gini(model)
