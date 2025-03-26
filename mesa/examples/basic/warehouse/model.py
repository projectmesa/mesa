import mesa
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.discrete_space.cell_agent import CellAgent
from mesa.examples.basic.warehouse.agents import (
    InventoryAgent,
    RouteAgent,
    SensorAgent,
    WorkerAgent,
)
from mesa.examples.basic.warehouse.make_warehouse import make_warehouse
from mesa.experimental.meta_agents.meta_agent import create_meta_agent

# Constants for configuration
LOADING_DOCKS = [(0, 0, 0), (0, 2, 0), (0, 4, 0), (0, 6, 0), (0, 8, 0)]
CHARGING_STATIONS = [
    (21, 19, 0),
    (21, 17, 0),
    (21, 15, 0),
    (21, 13, 0),
    (21, 11, 0),
]
INVENTORY_START_ROW_OFFSET = 3


class WarehouseModel(mesa.Model):
    """
    Model for simulating warehouse management with autonomous systems where
    each autonomous system (e.g., robot) is made of numerous smaller agents
    (e.g., routing, sensors, etc.).
    """

    def __init__(self, seed=42):
        """
        Initialize the model.

        Args:
            seed (int): Random seed.
        """
        super().__init__(seed=seed)
        self.inventory = {}
        self.loading_docks = LOADING_DOCKS
        self.charging_stations = CHARGING_STATIONS

        # Create warehouse and instantiate grid
        layout = make_warehouse()
        self.warehouse = OrthogonalMooreGrid(
            (layout.shape[0], layout.shape[1], layout.shape[2]),
            torus=False,
            capacity=1,
            random=self.random,
        )

        # Create Inventory Agents
        for row in range(
            INVENTORY_START_ROW_OFFSET, layout.shape[0] - INVENTORY_START_ROW_OFFSET
        ):
            for col in range(layout.shape[1]):
                for height in range(layout.shape[2]):
                    if layout[row][col][height].strip():
                        item = layout[row][col][height]
                        InventoryAgent(self, self.warehouse[row, col, height], item)

        # Create Robot Agents
        for idx in range(len(self.loading_docks)):
            # Create sub-agents
            router = RouteAgent(self)
            sensor = SensorAgent(self)
            worker = WorkerAgent(
                self,
                self.warehouse[self.loading_docks[idx]],
                self.warehouse[self.charging_stations[idx]],
            )

            # Create meta-agent and place in warehouse
            create_meta_agent(
                self,
                "RobotAgent",
                [router, sensor, worker],
                mesa_agent_type=CellAgent,
                meta_attributes={
                    "cell": self.warehouse[self.charging_stations[idx]],
                    "status": "open",
                },
                assume_subagent_attributes=True,
                assume_subagent_methods=True,
            )

    def central_move(self, robot):
        """
        Consolidates meta-agent behavior in the model class.

        Args:
            robot: The robot meta-agent to move.
        """
        robot.move(robot.cell.coordinate, robot.path)

    def step(self):
        """
        Advance the model by one step.
        """
        for robot in self.agents_by_type["RobotAgent"]:
            if robot.status == "open":  # Assign a task to the robot
                item = self.random.choice(self.agents_by_type["InventoryAgent"])
                if item.quantity > 0:
                    robot.initiate_task(item)
                    robot.status = "inventory"
                    self.central_move(robot)
            else:
                robot.continue_task()
