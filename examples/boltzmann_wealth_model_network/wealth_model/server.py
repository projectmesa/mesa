from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from .model import MoneyModel
from .NetworkVisualization import NetworkElement


def network_portrayal(G):
    portrayal = dict()
    portrayal['nodes'] = [{'id': n_id,
                           'agent_id': None if n['agent'] is None else n['agent'].unique_id,
                           'size': 1 if n['agent'] is None else 3,
                           'color': 'red' if n['agent'] is None or n['agent'].wealth == 0 else 'green',
                           'label': None if n['agent'] is None else 'Agent:{} Wealth:{}'.format(n['agent'].unique_id,
                                                                                                n['agent'].wealth),
                           }
                          for n_id, n in G.nodes(data=True)]

    portrayal['edges'] = [{'id': i,
                           'source': source,
                           'target': target,
                           }
                          for i, (source, target, d) in enumerate(G.edges(data=True))]

    return portrayal


grid = NetworkElement(network_portrayal, 500, 500)
chart = ChartModule([
    {"Label": "Gini", "Color": "Black"}],
    data_collector_name='datacollector'
)

model_params = {
    "num_agents": UserSettableParameter('slider', "Number of agents", 7, 7, 10, 1,
                                        description="Choose how many agents to include in the model"),
    "num_nodes": UserSettableParameter('slider', "Number of nodes", 10, 10, 12, 1,
                                       description="Choose how many nodes to include in the model")
}

server = ModularServer(MoneyModel, [grid, chart], "Money Model", model_params)
server.port = 8521
