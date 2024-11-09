# noqa: D100
from mesa.examples import (
    BoidFlockers,
    BoltzmannWealth,
    ConwaysGameOfLife,
    EpsteinCivilViolence,
    PdGrid,
    Schelling,
    SugarscapeG1mt,
    VirusOnNetwork,
    WolfSheep,
)


def test_boltzmann_model():  # noqa: D103
    model = BoltzmannWealth(seed=42)

    for _i in range(10):
        model.step()


def test_conways_game_model():  # noqa: D103
    model = ConwaysGameOfLife(seed=42)
    for _i in range(10):
        model.step()


def test_schelling_model():  # noqa: D103
    model = Schelling(seed=42)
    for _i in range(10):
        model.step()


def test_virus_on_network():  # noqa: D103
    model = VirusOnNetwork(seed=42)
    for _i in range(10):
        model.step()


def test_boid_flockers():  # noqa: D103
    model = BoidFlockers(seed=42)

    for _i in range(10):
        model.step()


def test_epstein():  # noqa: D103
    model = EpsteinCivilViolence(seed=42)

    for _i in range(10):
        model.step()


def test_pd_grid():  # noqa: D103
    model = PdGrid(seed=42)

    for _i in range(10):
        model.step()


def test_sugarscape_g1mt():  # noqa: D103
    model = SugarscapeG1mt(seed=42)

    for _i in range(10):
        model.step()


def test_wolf_sheep():  # noqa: D103
    from mesa.experimental.devs import ABMSimulator

    simulator = ABMSimulator()
    WolfSheep(seed=42, simulator=simulator)
    simulator.run_for(10)
