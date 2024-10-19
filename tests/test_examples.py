# noqa: D100
from mesa.examples import (
    BoidFlockers,
    BoltzmannWealthModel,
    ConwaysGameOfLife,
    Schelling,
    VirusOnNetwork,
)

def test_boltzmann_model():
    model = BoltzmannWealthModel(seed=42)

    for _i in range(10):
        model.step()


def test_conways_game_model():
    model = ConwaysGameOfLife(seed=42)
    for _i in range(10):
        model.step()

def test_schelling_model():
    model = Schelling(seed=42)
    for _i in range(10):
        model.step()

def test_virus_on_network():
    model = VirusOnNetwork(seed=42)
    for _i in range(10):
        model.step()

def test_boid_flockers():
    model = BoidFlockers(seed=42)

    for _i in range(10):
        model.step()