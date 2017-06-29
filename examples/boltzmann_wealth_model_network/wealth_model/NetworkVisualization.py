from mesa.visualization.ModularVisualization import VisualizationElement


class NetworkElement(VisualizationElement):
    local_includes = ["wealth_model/visualization_js/network_canvas.js",
                      "wealth_model/visualization_js/sigma.min.js"]

    def __init__(self, canvas_height=500, canvas_width=500):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = ("new Network_Module({}, {})".
                       format(self.canvas_width, self.canvas_height))
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        return [convert_network_to_dict(model.G)]


def convert_network_to_dict(G):
    d = dict()
    d['nodes'] = [{'id': n_id,
                   'agent_id': getattribute(n, 'unique_id'),
                   'size': 1 if n['agent'] is None else 3,
                   'color': 'green' if getattribute(n, 'wealth', default=0) > 0 else 'red',
                   'label': None if n['agent'] is None else 'Agent:' + str(n['agent'].unique_id) + ' Wealth:' + str(
                       n['agent'].wealth)
                   }
                  for n_id, n in G.nodes(data=True)]

    d['edges'] = [{'id': i, 'source': source, "target": target} for i, (source, target, d) in
                  enumerate(G.edges(data=True))]

    return d


def getattribute(n, prop_name, default=None):
    return default if n['agent'] is None else getattr(n['agent'], prop_name)
