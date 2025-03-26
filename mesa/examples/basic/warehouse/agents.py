from queue import PriorityQueue

import mesa
from mesa.discrete_space import FixedAgent


class InventoryAgent(FixedAgent):
    """
    Represents an inventory item in the warehouse.
    """

    def __init__(self, model, cell, item: str):
        super().__init__(model, key_by_name=True)
        self.cell = cell
        self.item = item
        self.quantity = 1000  # Default quantity


class RouteAgent(mesa.Agent):
    """
    Handles path finding for agents in the warehouse.

    Intended to be a pseudo onboard GPS system for robots.
    """

    def __init__(self, model):
        super().__init__(model, key_by_name=True)

    def find_path(self, start, goal) -> list[tuple[int, int, int]] | None:
        """
        Determines the path for a robot to take using the A* algorithm.
        """

        def heuristic(a, b) -> int:
            dx = abs(a[0] - b[0])
            dy = abs(a[1] - b[1])
            return dx + dy

        open_set = PriorityQueue()
        open_set.put((0, start.coordinate))
        came_from = {}
        g_score = {start.coordinate: 0}

        while not open_set.empty():
            _, current = open_set.get()

            if current[:2] == goal.coordinate[:2]:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                path.insert(0, start.coordinate)
                path.pop()  # Remove the last location (inventory)
                return path

            for n_cell in self.model.warehouse[current].neighborhood:
                coord = n_cell.coordinate

                # Only consider orthogonal neighbors
                if abs(coord[0] - current[0]) + abs(coord[1] - current[1]) != 1:
                    continue

                tentative_g_score = g_score[current] + 1
                if not n_cell.is_empty:
                    tentative_g_score += 50  # Penalty for non-empty cells

                if coord not in g_score or tentative_g_score < g_score[coord]:
                    g_score[coord] = tentative_g_score
                    f_score = tentative_g_score + heuristic(coord, goal.coordinate)
                    open_set.put((f_score, coord))
                    came_from[coord] = current

        return None


class SensorAgent(mesa.Agent):
    """
    Detects entities in the area and handles movement along a path.

    Intended to be a pseudo onboard sensor system for robot.
    """

    def __init__(self, model):
        super().__init__(model, key_by_name=True)

    def move(
        self, coord: tuple[int, int, int], path: list[tuple[int, int, int]]
    ) -> str:
        """
        Moves the agent along the given path.
        """
        if coord not in path:
            raise ValueError("Current coordinate not in path.")

        idx = path.index(coord)
        if idx + 1 >= len(path):
            return "movement complete"

        next_cell = self.model.warehouse[path[idx + 1]]
        if next_cell.is_empty:
            self.meta_agent.cell = next_cell
            return "moving"

        # Handle obstacle
        neighbors = self.model.warehouse[self.meta_agent.cell.coordinate].neighborhood
        empty_neighbors = [n for n in neighbors if n.is_empty]
        if empty_neighbors:
            self.meta_agent.cell = self.random.choice(empty_neighbors)

        # Recalculate path
        new_path = self.meta_agent.get_subagent_instance(RouteAgent).find_path(
            self.meta_agent.cell, self.meta_agent.item.cell
        )
        self.meta_agent.path = new_path
        return "recalculating"


class WorkerAgent(mesa.Agent):
    """
    Represents a robot worker responsible for collecting and loading items.
    """

    def __init__(self, model, ld, cs):
        super().__init__(model, key_by_name=True)
        self.loading_dock = ld
        self.charging_station = cs
        self.path: list[tuple[int, int, int]] | None = None
        self.carrying: str | None = None
        self.item: InventoryAgent | None = None

    def initiate_task(self, item: InventoryAgent):
        """
        Initiates a task for the robot to perform.
        """
        self.item = item
        self.path = self.find_path(self.cell, item.cell)

    def continue_task(self):
        """
        Continues the task if the robot is able to perform it.
        """
        status = self.meta_agent.get_subagent_instance(SensorAgent).move(
            self.cell.coordinate, self.path
        )

        if status == "movement complete" and self.meta_agent.status == "inventory":
            # Pick up item and bring to loading dock
            self.meta_agent.cell = self.model.warehouse[
                *self.meta_agent.cell.coordinate[:2], self.item.cell.coordinate[2]
            ]
            self.meta_agent.status = "loading"
            self.carrying = self.item.item
            self.item.quantity -= 1
            self.meta_agent.cell = self.model.warehouse[
                *self.meta_agent.cell.coordinate[:2], 0
            ]
            self.path = self.find_path(self.cell, self.loading_dock)

        if status == "movement complete" and self.meta_agent.status == "loading":
            # Load item onto truck and return to charging station
            self.carrying = None
            self.meta_agent.status = "open"
