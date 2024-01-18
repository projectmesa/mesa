configurations = {
    # Schelling Model Configurations
    "Schelling": {
        'small': {'seeds': 100, 'replications': 5, 'steps': 20, 'height': 40, 'width': 40, 'homophily': 3, 'radius': 1, 'density': 0.625},
        'large': {'seeds': 25, 'replications': 5, 'steps': 20, 'height': 100, 'width': 100, 'homophily': 8, 'radius': 2, 'density': 0.8}
    },

    # WolfSheep Model Configurations
    "WolfSheep": {
        'small': {'seeds': 100, 'replications': 5, 'steps': 100, 'height': 25, 'width': 25, 'initial_sheep': 60, 'initial_wolves': 40, 'sheep_reproduce': 0.2, 'wolf_reproduce': 0.1, 'grass_regrowth_time': 20},
        'large': {'seeds': 25, 'replications': 5, 'steps': 100, 'height': 100, 'width': 100, 'initial_sheep': 1000, 'initial_wolves': 500, 'sheep_reproduce': 0.4, 'wolf_reproduce': 0.2, 'grass_regrowth_time': 10}
    },

    # BoidFlockers Model Configurations
    "Flocking": {
        'small': {'seeds': 100, 'replications': 5, 'steps': 100, 'population': 200, 'width': 100, 'height': 100, 'vision': 5},
        'large': {'seeds': 25, 'replications': 5, 'steps': 100, 'population': 400, 'width': 150, 'height': 150, 'vision': 15}
    },
}
