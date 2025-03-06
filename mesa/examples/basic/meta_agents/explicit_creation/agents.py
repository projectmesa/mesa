from queue import PriorityQueue

import mesa


class RouteAgent(mesa.Agent):
    """
    Psuedo of on board routing entity that the agent will take
    """

    def __init__(self, model):
        super().__init__(model)

    def find_path(self, start, goal):
        """
        Determines path for robot to take
        """

        # A* path finding algorithm
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def _get_neighbors(self, position):
            row, col = position
            potential_moves = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
            ]
            return [
                move for move in potential_moves if self.warehouse.is_walkable(move)
            ]

        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}

        while not open_set.empty():
            _, current = open_set.get()

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self._get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score, neighbor))
                    came_from[neighbor] = current

        return None


class SensorAgent(mesa.Agent):
    """
    Psuedo sensor that detects other entities in the area

    """

    def __init__(self, model):
        super().__init__(model)

    def check_path(self, next_position):
        """
        Detects obstacles in the area
        """
