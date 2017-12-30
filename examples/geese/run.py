from swarms.model import EnvironmentModel
from swarms.agent import SwarmAgent

import argparse

## Global variables for width and height
width = 50
height = 50

def main():
    
    env = EnvironmentModel(10, width, height)

    for i in range(1000):
        env.step()

    for agent in env.schedule.agents:
        print (agent.unique_id, agent.wealth)

if __name__ == '__main__':
    main()