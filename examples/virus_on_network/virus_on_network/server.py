from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import NetworkModule

from .model import VirusModel


def network_portrayal(G):
    portrayal = dict()
    portrayal['nodes'] = [{'id': n_id,
                           'agent_id': n['agent'].unique_id,
                           'size': 2,
                           'color': '#CC0000' if n['agent'].infected is True else '#007959',
                           }
                          for n_id, n in G.nodes(data=True)]

    portrayal['edges'] = [{'id': i,
                           'source': source,
                           'target': target,
                           'color': '#000000',
                           }
                          for i, (source, target, _) in enumerate(G.edges(data=True))]

    return portrayal


grid = NetworkModule(network_portrayal, 500, 500)
chart = ChartModule([
    {"Label": "Nodes_Infected", "Color": "Black"}],
    data_collector_name='datacollector'
)

model_params = {
    "num_nodes": UserSettableParameter('slider', "Number of agents", 10, 10, 100, 1,
                                       description="Choose how many agents to include in the model"),
    "avg_node_degree": UserSettableParameter('slider', "Avg Node Degree", 3, 3, 8, 1,
                                             description="Avg Node Degree"),
    "initial_outbreak_size": UserSettableParameter('slider', "Initial Outbreak Size", 1, 1, 3, 1,
                                                   description="Initial Outbreak Size"),
    "spread_probability": UserSettableParameter('slider', "Spread Probability", 0.3, 0.0, 1.0, 0.1,
                                                description="Spread Probability"),
}

server = ModularServer(VirusModel, [grid, chart], "Virus Model", model_params)
server.port = 8521
