
class NetworkGrid:
    """ Network Grid where each node contains zero or more agents. """

    def __init__(self, G):
        self.G = G
        for node_id in self.G.nodes:
            G.nodes[node_id]["agent"] = list()

    def place_agent(self, agent, node_id):
        """ Place a agent in a node. """

        self._place_agent(agent, node_id)
        agent.pos = node_id

    def get_neighbors(self, node_id, include_center=False):
        """ Get all adjacent nodes """

        neighbors = list(self.G.neighbors(node_id))
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

        self.G.nodes[node_id]["agent"].append(agent)

    def _remove_agent(self, agent, node_id):
        """ Remove an agent from a node. """

        self.G.nodes[node_id]["agent"].remove(agent)

    def is_cell_empty(self, node_id):
        """ Returns a bool of the contents of a cell. """
        return not self.G.nodes[node_id]["agent"]

    def get_cell_list_contents(self, cell_list):
        return list(self.iter_cell_list_contents(cell_list))

    def get_all_cell_contents(self):
        return list(self.iter_cell_list_contents(self.G))

    def iter_cell_list_contents(self, cell_list):
        list_of_lists = [
            self.G.nodes[node_id]["agent"]
            for node_id in cell_list
            if not self.is_cell_empty(node_id)
        ]
        return [item for sublist in list_of_lists for item in sublist]
