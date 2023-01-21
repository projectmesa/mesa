def test_import():
    # This tests the new, simpler Mesa namespace. See
    # https://github.com/projectmesa/mesa/pull/1294.
    import mesa
    import mesa.flat as mf
    from mesa.time import RandomActivation

    mesa.time.RandomActivation
    RandomActivation
    mf.RandomActivation

    from mesa.space import MultiGrid

    mesa.space.MultiGrid
    MultiGrid
    mf.MultiGrid

    from mesa.visualization.ModularVisualization import ModularServer

    mesa.visualization.ModularServer
    ModularServer
    mf.ModularServer

    from mesa.datacollection import DataCollector

    DataCollector
    mesa.DataCollector
    mf.DataCollector

    from mesa.batchrunner import batch_run

    batch_run
    mesa.batch_run
