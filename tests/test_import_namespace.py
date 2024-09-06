def test_import():
    # This tests the new, simpler Mesa namespace. See
    # https://github.com/projectmesa/mesa/pull/1294.
    import mesa
    from mesa.time import RandomActivation

    _ = mesa.time.RandomActivation
    _ = RandomActivation

    from mesa.space import MultiGrid

    _ = mesa.space.MultiGrid
    _ = MultiGrid

    from mesa.datacollection import DataCollector

    _ = DataCollector
    _ = mesa.DataCollector

    from mesa.batchrunner import batch_run

    _ = batch_run
    _ = mesa.batch_run
