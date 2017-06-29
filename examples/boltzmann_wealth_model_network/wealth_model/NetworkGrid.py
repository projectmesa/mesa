import networkx as nx


class NetworkGrid:
    def __init__(self, G):
        self.G = G
        nx.set_node_attributes(self.G, 'agent', None)

    def place_agent(self, agent, node_id):
        """ Place a new agent in the space. """

        self._place_agent(agent, node_id)
        agent.pos = node_id

    def get_neighbors(self, node_id, include_center=False):
        """ Get all adjacent nodes """

        neighbors = self.G.neighbors(node_id)
        if include_center:
            neighbors.append(node_id)

        return neighbors

    def move_agent(self, agent, node_id):
        """ Move an agent from its current node to a new node. """

        self._remove_agent(agent, agent.pos)
        self._place_agent(agent, node_id)
        agent.pos = node_id

    def _place_agent(self, agent, node_id):
        """ Place the agent at the correct node. """

        self.G.node[node_id]['agent'] = agent

    def _remove_agent(self, agent, node_id):
        """ Remove an agent at a given point, and update the internal grid. """

        self.G.node[node_id]['agent'] = None

    def is_cell_empty(self, node_id):
        """ Returns a bool of the contents of a cell. """
        return True if self.G.node[node_id]['agent'] is None else False

    def get_cell_list_contents(self, cell_list):
        return list(self.iter_cell_list_contents(cell_list))

    def iter_cell_list_contents(self, cell_list):
        return [self.G.node[node_id]['agent'] for node_id in cell_list if not self.is_cell_empty(node_id)]
