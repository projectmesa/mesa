"""
The following code was adapted from the Bank Reserves model included in Netlogo
Model information can be found at: http://ccl.northwestern.edu/netlogo/models/BankReserves
Accessed on: November 2, 2017
Author of NetLogo code:
    Wilensky, U. (1998). NetLogo Bank Reserves model.
    http://ccl.northwestern.edu/netlogo/models/BankReserves.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.

This version of the model has a BatchRunner at the bottom. This
is for collecting data on parameter sweeps. It is not meant to
be run with run.py, since run.py starts up a server for visualization, which
isn't necessary for the BatchRunner. To run a parameter sweep, call
batch_run.py in the command line.

The BatchRunner is set up to collect step by step data of the model. It does
this by collecting the DataCollector object in a model_reporter (i.e. the
DataCollector is collecting itself every step).

The end result of the batch run will be a csv file created in the same
directory from which Python was run. The csv file will contain the data from
every step of every run.
"""

from bank_reserves.agents import Bank, Person
import itertools
from mesa import Model
from mesa.batchrunner import BatchRunner
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np
import pandas as pd

# Start of datacollector functions


def get_num_rich_agents(model):
    """list of rich agents"""

    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    # return number of rich agents
    return len(rich_agents)


def get_num_poor_agents(model):
    """list of poor agents"""

    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    # return number of poor agents
    return len(poor_agents)


def get_num_mid_agents(model):
    """list of middle class agents"""

    mid_agents = [a for a in model.schedule.agents if
                  a.loans < 10 and a.savings < model.rich_threshold]
    # return number of middle class agents
    return len(mid_agents)


def get_total_savings(model):
    """list of amounts of all agents' savings"""

    agent_savings = [a.savings for a in model.schedule.agents]
    # return the sum of agents' savings
    return np.sum(agent_savings)


def get_total_wallets(model):
    """list of amounts of all agents' wallets"""

    agent_wallets = [a.wallet for a in model.schedule.agents]
    # return the sum of all agents' wallets
    return np.sum(agent_wallets)


def get_total_money(model):
    """sum of all agents' wallets"""

    wallet_money = get_total_wallets(model)
    # sum of all agents' savings
    savings_money = get_total_savings(model)
    # return sum of agents' wallets and savings for total money
    return wallet_money + savings_money


def get_total_loans(model):
    """list of amounts of all agents' loans"""

    agent_loans = [a.loans for a in model.schedule.agents]
    # return sum of all agents' loans
    return np.sum(agent_loans)


def track_params(model):
    return (model.init_people,
            model.rich_threshold,
            model.reserve_percent)


def track_run(model):
    return model.uid


class BankReservesModel(Model):
    # id generator to track run number in batch run data
    id_gen = itertools.count(1)

    # grid height
    grid_h = 20
    # grid width
    grid_w = 20

    """init parameters "init_people", "rich_threshold", and "reserve_percent"
       are all UserSettableParameters"""
    def __init__(self, height=grid_h, width=grid_w, init_people=2, rich_threshold=10,
                 reserve_percent=50,):
        self.uid = next(self.id_gen)
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        # rich_threshold is the amount of savings a person needs to be considered "rich"
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent
        # see datacollector functions above
        self.datacollector = DataCollector(model_reporters={
                                           "Rich": get_num_rich_agents,
                                           "Poor": get_num_poor_agents,
                                           "Middle Class": get_num_mid_agents,
                                           "Savings": get_total_savings,
                                           "Wallets": get_total_wallets,
                                           "Money": get_total_money,
                                           "Loans": get_total_loans,
                                           "Model Params": track_params,
                                           "Run": track_run},
                                           agent_reporters={
                                           "Wealth": lambda x: x.wealth})

        # create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent)

        # create people for the model according to number of people set by user
        for i in range(self.init_people):
            # set x coordinate as a random number within the width of the grid
            x = self.random.randrange(self.width)
            # set y coordinate as a random number within the height of the grid
            y = self.random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            # place the Person object on the grid at coordinates (x, y)
            self.grid.place_agent(p, (x, y))
            # add the Person object to the model schedule
            self.schedule.add(p)

        self.running = True

    def step(self):
        # collect data
        self.datacollector.collect(self)
        # tell all the agents in the model to run their step function
        self.schedule.step()

    def run_model(self):
        for i in range(self.run_time):
            self.step()


# parameter lists for each parameter to be tested in batch run
br_params = {"init_people": [25, 100, 150, 200],
             "rich_threshold": [5, 10, 15, 20],
             "reserve_percent": [0, 50, 100]}

br = BatchRunner(BankReservesModel,
                 br_params,
                 iterations=1,
                 max_steps=1000,
                 model_reporters={"Data Collector": lambda m: m.datacollector})

if __name__ == '__main__':
    br.run_all()
    br_df = br.get_model_vars_dataframe()
    br_step_data = pd.DataFrame()
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = br_df["Data Collector"][i].get_model_vars_dataframe()
            br_step_data = br_step_data.append(i_run_data, ignore_index=True)
    br_step_data.to_csv("BankReservesModel_Step_Data.csv")
