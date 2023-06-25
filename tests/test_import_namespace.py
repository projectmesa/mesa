def test_import():
    # This tests the new, simpler Mesa namespace. See
    # https://github.com/projectmesa/mesa/pull/1294.
    import mesa
    import mesa.flat as mf
    from mesa.time import RandomActivation

    _ = mesa.time.RandomActivation
    _ = RandomActivation
    _ = mf.RandomActivation

    from mesa.space import MultiGrid

    _ = mesa.space.MultiGrid
    _ = MultiGrid
    _ = mf.MultiGrid

    from mesa.visualization.ModularVisualization import ModularServer

    _ = mesa.visualization.ModularServer
    _ = ModularServer
    _ = mf.ModularServer

    from mesa.datacollection import DataCollector

    _ = DataCollector
    _ = mesa.DataCollector
    _ = mf.DataCollector

    from mesa.batchrunner import batch_run

    _ = batch_run
    _ = mesa.batch_run
