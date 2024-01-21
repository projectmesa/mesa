from Flocking.Flocking import BoidFlockers
from Schelling.Schelling import SchellingModel
from WolfSheep.WolfSheep import WolfSheep

configurations = {
    # Schelling Model Configurations
    SchellingModel: {
        "small": {
            "seeds": 50,
            "replications": 5,
            "steps": 20,
            "parameters": {
                "height": 40,
                "width": 40,
                "homophily": 3,
                "radius": 1,
                "density": 0.625,
            },
        },
        "large": {
            "seeds": 10,
            "replications": 3,
            "steps": 10,
            "parameters": {
                "height": 100,
                "width": 100,
                "homophily": 8,
                "radius": 2,
                "density": 0.8,
            },
        },
    },
    # WolfSheep Model Configurations
    WolfSheep: {
        "small": {
            "seeds": 50,
            "replications": 5,
            "steps": 40,
            "parameters": {
                "height": 25,
                "width": 25,
                "initial_sheep": 60,
                "initial_wolves": 40,
                "sheep_reproduce": 0.2,
                "wolf_reproduce": 0.1,
                "grass_regrowth_time": 20,
            },
        },
        "large": {
            "seeds": 10,
            "replications": 3,
            "steps": 20,
            "parameters": {
                "height": 100,
                "width": 100,
                "initial_sheep": 1000,
                "initial_wolves": 500,
                "sheep_reproduce": 0.4,
                "wolf_reproduce": 0.2,
                "grass_regrowth_time": 10,
            },
        },
    },
    # BoidFlockers Model Configurations
    BoidFlockers: {
        "small": {
            "seeds": 25,
            "replications": 3,
            "steps": 20,
            "parameters": {"population": 200, "width": 100, "height": 100, "vision": 5},
        },
        "large": {
            "seeds": 10,
            "replications": 3,
            "steps": 10,
            "parameters": {
                "population": 400,
                "width": 150,
                "height": 150,
                "vision": 15,
            },
        },
    },
}
