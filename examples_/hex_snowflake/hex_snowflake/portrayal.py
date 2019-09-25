def portrayCell(cell):
    '''
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the cell in its current state.
    :param cell:  the cell in the simulation
    :return: the portrayal dictionary.
    '''
    assert cell is not None
    return {
        "Shape": "hex",
        "r": 1,
        "Filled": "true",
        "Layer": 0,
        "x": cell.x,
        "y": cell.y,
        "Color": "black" if cell.isAlive else "white"
    }
