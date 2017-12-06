import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import TextElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import NetworkModule

from .model import VirusModel, State, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        if agent.state is State.INFECTED:
            return '#FF0000'
        elif agent.state is State.SUSCEPTIBLE:
            return '#008000'
        else:
            return '#808080'

    def edge_color(agent1, agent2):
        if agent1.state is State.RESISTANT or agent2.state is State.RESISTANT:
            return '#000000'
        return '#e8e8e8'

    def edge_width(agent1, agent2):
        if agent1.state is State.RESISTANT or agent2.state is State.RESISTANT:
            return 3
        return 2

    portrayal = dict()
    portrayal['nodes'] = [{'id': n_id,
                           'agent_id': n['agent'][0].unique_id,
                           'size': 2,
                           'color': node_color(n['agent'][0]),
                           }
                          for n_id, n in G.nodes(data=True)]

    portrayal['edges'] = [{'id': i,
                           'source': source,
                           'target': target,
                           'color': edge_color(G.node[source]['agent'][0], G.node[target]['agent'][0]),
                           'width': edge_width(G.node[source]['agent'][0], G.node[target]['agent'][0]),
                           }
                          for i, (source, target, _) in enumerate(G.edges(data=True))]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library='d3')
chart = ChartModule([{'Label': 'Infected', 'Color': '#FF0000'},
                     {'Label': 'Susceptible', 'Color': '#008000'},
                     {'Label': 'Resistant', 'Color': '#808080'}])


class RatioElement(TextElement):
    def render(self, model):
        ratio = model.resistant_susceptible_ratio()
        ratio_text = '&infin;' if ratio is math.inf else '{0:.2f}'.format(ratio)
        return 'Resistant/Susceptible Ratio: ' + ratio_text


class InfectedRemainingElement(TextElement):
    def render(self, model):
        infected = number_infected(model)
        return 'Infected Remaining: ' + str(infected)


text = RatioElement(), InfectedRemainingElement()

model_params = {
    'num_nodes': UserSettableParameter('slider', 'Number of agents', 10, 10, 100, 1,
                                       description='Choose how many agents to include in the model'),
    'avg_node_degree': UserSettableParameter('slider', 'Avg Node Degree', 3, 3, 8, 1,
                                             description='Avg Node Degree'),
    'initial_outbreak_size': UserSettableParameter('slider', 'Initial Outbreak Size', 1, 1, 10, 1,
                                                   description='Initial Outbreak Size'),
    'virus_spread_chance': UserSettableParameter('slider', 'Virus Spread Chance', 0.4, 0.0, 1.0, 0.1,
                                                 description='Probability that susceptible neighbor will be infected'),
    'virus_check_frequency': UserSettableParameter('slider', 'Virus Check Frequency', 0.4, 0.0, 1.0, 0.1,
                                                   description='Frequency the nodes check whether they are infected by '
                                                               'a virus'),
    'recovery_chance': UserSettableParameter('slider', 'Recovery Chance', 0.3, 0.0, 1.0, 0.1,
                                             description='Probability that the virus will be removed'),
    'gain_resistance_chance': UserSettableParameter('slider', 'Gain Resistance Chance', 0.5, 0.0, 1.0, 0.1,
                                                    description='Probability that a recovered agent will become '
                                                                'resistant to this virus in the future'),
}

server = ModularServer(VirusModel, [network, chart, *text], 'Virus Model', model_params)
server.port = 8521
