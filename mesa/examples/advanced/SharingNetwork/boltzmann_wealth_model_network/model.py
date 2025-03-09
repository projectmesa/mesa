import decimal
import math
import random
from itertools import combinations

import networkx as nx
from mesa_old import Agent, Model
from mesa_old.datacollection import DataCollector
from mesa_old.space import NetworkGrid
from mesa_old.time import RandomActivation

# probability of attack, impact, cost to attacker, and index number, respectively, for 4 attack types
# 1:malware, 2:web-based, 3:DOS, 4:malicious insider
attacks = [
    [0.25, 2600, 50, 0],
    [0.20, 2300, 60, 1],
    [0.20, 1700, 70, 2],
    [0.15, 1600, 65, 3],
]
att_combos = list()
for n in range(len(attacks) + 1):
    att_combos += list(combinations(attacks, n))
att_combos.remove(())

# prob of mitigating attack 1-4, investment, and annual cost, respectively, for 6 counter measure types
# 1:security sharing, 2:access management, 3:cyber behavior analytics, 4:cryptography, 5:policy management, 6:enterprise governance
countermeasure = [
    [0.6, 0.5, 0.4, 0.5, 100, 25],
    [0.4, 0.6, 0.4, 0.6, 80, 30],
    [0.5, 0.5, 0.4, 0.6, 110, 30],
    [0.4, 0.5, 0.3, 0.4, 100, 5],
    [0.5, 0.4, 0.3, 0.5, 80, 45],
    [0.5, 0.5, 0.4, 0.5, 300, 50],
]
cm_combos = list()
for n in range(len(countermeasure) + 1):
    cm_combos += list(combinations(countermeasure, n))
cm_combos.remove(())
# cm_combos[combo set][countermeasure][value]


class DefenderNetworkModel(Model):
    """A model with some number of agents."""

    """add description of network, change class names"""

    def __init__(
        self,
        num_groups=7,
        num_members=6,
        prob_add_friend=0.5,
        punish=0,
        alphaM=45,
        betaM=45,
        punish_cost=50,
        penalty=100,
    ):
        self.num_agents = num_groups * num_members
        self.num_nodes = self.num_agents
        self.G = nx.planted_partition_graph(num_groups, num_members, 0.5, 0.1)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.rosi = 0
        self.datacollector = DataCollector(
            model_reporters={
                "prob_of_contr": self.prob_of_contr,
                "gain": self.gain,
                "wealth": self.wealth,
                "freeriders": self.freeriders,
                "friends": self.friends,
                "altruism": self.altruism,
                "contribution_value": self.contribution_value,
                "cmlist": self.cmlist,
                "attlist": self.attlist,
                "graph": self.graph,
                "alpha": self.alpha,
                "beta": self.beta,
            },
            agent_reporters={
                "Contribution %": lambda _: _.prob_of_contr,
                "Altruism": lambda _: _.gain,
            },
        )

        list_of_random_nodes = self.random.sample(self.G.nodes(), self.num_agents)

        # Create agents
        for i in range(self.num_agents):
            a = Defender(
                i, self, prob_add_friend, punish, alphaM, betaM, punish_cost, penalty
            )
            self.schedule.add(a)
            # Add the agent to a random node
            self.grid.place_agent(a, list_of_random_nodes[i])

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def datacollect(self):
        return self.datacollector.get_model_vars_dataframe()

    def prob_of_contr(self):
        y = [agent.prob_of_contr for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def wealth(self):
        y = [agent.wealth for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def gain(self):
        y = [agent.gain for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def freeriders(self):
        y = [agent.k for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def friends(self):
        y = [len(agent.friends) for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def altruism(self):
        y = [agent.altruism for agent in self.schedule.agents]
        # x = [agent.prob_of_contr <= 0 for agent in self.schedule.agents]
        return y

    def contribution_value(self):
        y = [agent.cmValue + agent.attValue for agent in self.schedule.agents]
        return y

    def cmlist(self):
        y = [agent.cmlist for agent in self.schedule.agents]
        return y

    def attlist(self):
        y = [agent.attlist for agent in self.schedule.agents]
        return y

    def alpha(self):
        y = [agent.alpha for agent in self.schedule.agents]
        return y

    def beta(self):
        y = [agent.beta for agent in self.schedule.agents]
        return y

    def graph(self):
        return self.G

    def run_model(self, n):
        for i in range(n):
            self.step()


class Defender(Agent):
    """An agent with fixed initial wealth."""

    def __init__(
        self,
        unique_id,
        model,
        prob_add_friend,
        punish,
        alphaM,
        betaM,
        punish_cost,
        penalty,
    ):
        super().__init__(unique_id, model)
        self.wealth = int(random.uniform(2000, 8000))
        self.prob_of_contr = float(round(random.random(), 2))
        self.altruism = int(random.uniform(1, 100))
        self.altlist = [self.altruism]
        self.contrlist = [1]
        self.cmlist = []
        self.attlist = []
        self.cmValue = 0
        self.attValue = 0
        self.cm_from_neighbors = [[]]
        self.att_from_neighbors = [[]]
        self.past_cm = [[]]
        self.past_att = [[]]
        self.neighValue = []
        self.AV = int(random.uniform(400, 1600))
        self.friend_list = []
        self.i = 0  # number of rounds
        self.k = 0  # percentage of freeriders
        self.alpha = alphaM  # used to calculate altruism
        self.beta = betaM  # used to calculate altruism
        self.contribution = 1
        self.rosi = 0
        self.gain = round((self.wealth - self.contribution + self.rosi), 2)
        self.all_nodes = []
        self.G = model.G
        self.model = model
        self.id = unique_id
        self.roa = 0
        self.friends = []
        self.prob_add_friend = prob_add_friend
        self.punish = punish
        self.penalty = penalty
        self.punish_cost = punish_cost
        self.prob_of_pun = 1
        self.neighbor_prob_of_pun = 1

    # manages which attack set will be chosen &
    # which countermeasure set will be chosen
    def attack(self):
        att_num = random.randrange(4)  # which attack will be considered

        RMmin = 0
        RMmax = 0
        RMaC = 1
        aRMaC = 1
        csi = 0
        cmValue = 0
        possibleAttacks = random.choice(self.att_from_neighbors)

        """determines attack set that optimizes roa"""
        for att_set in att_combos:
            gi = 0
            cost = 0
            attValue = 0
            roa = 0
            for att in att_set:
                gi += att[1]
                cost += att[2]

                # value of attack data
                attValue += att[1]
                # aRMaC determined by combining most effective cm
                if att == attacks[0]:
                    armac = countermeasure[random.randrange(5)][0]
                    aRMaC *= armac
                elif att == attacks[1]:
                    armac = countermeasure[random.randrange(5)][1]
                    aRMaC *= armac
                elif att == attacks[2]:
                    armac = countermeasure[random.randrange(5)][2]
                    aRMaC *= armac
                elif att == attacks[3]:
                    armac = countermeasure[random.randrange(5)][3]
                    aRMaC *= armac
                else:
                    print("error occurred determining ROA")
            roa = (gi - (gi * aRMaC) - cost) / cost
            if self.roa < roa:
                self.roa = roa
                # print(att_set)
                self.attlist = att_set
                self.attValue = attValue
            aRMaC = 1

        """picks set of counter measures based on best ROSI"""
        # cm_combos[cm_set][cmeasure][value]
        for cm_set in cm_combos:
            RMmax = 0
            RMmin = 0
            RMaC = 1
            csi = 0
            cmValue = 0
            possibleAttacks = random.choice(self.att_from_neighbors)

            # (Annual Loss Expectancy) = (Number of Incidents per Year) X (Potential Loss per Incident)
            # ALE is determined from data shared from friends, otherwise is random if no friends have shared
            if possibleAttacks == []:
                ale = (self.AV * (self.AV / self.wealth)) * attacks[att_num][0]
            else:
                ale = 0
                for attack in possibleAttacks:
                    ale += (self.AV * (self.AV / self.wealth)) * attack[0]

            # determines risk mitigation, RMaC, from combined cm's from cm_set bounded by RMmin <= RMaC <= RMmax
            for cmeasure in cm_set:
                """update to consider either attack set or empty possible attcks"""
                for rm in cm_set:
                    if rm[att_num] > RMmin:
                        RMmin = rm[att_num]

            for cmeasure2 in cm_set:
                if possibleAttacks == []:
                    # max mitigation is the minimum of 1 or the sum of all rm's from each cm in the set
                    RMmax += cmeasure2[attacks[att_num][3]]

                    # combine rm probabilities
                    RMaC *= cmeasure2[attacks[att_num][3]]
                else:
                    for attack in possibleAttacks:
                        RMmax += cmeasure2[attack[3]]
                        RMaC *= cmeasure2[attack[3]]

                # sum all countermeasure costs in the set
                csi += cmeasure2[5]

                # monetary value of cm data
                cmValue += cmeasure2[4]

            RMmax = min(1, RMmax)

            # ensures RMaC is in the within stated bounds
            if RMmin > (1 - RMaC):
                RMaC = RMmin
            if RMaC > RMmax:
                RMaC = RMmax

            # updates selected cm's and ROSI from those cm's
            rositemp = (ale - (ale * (1 - RMaC)) - csi) / csi
            # print("rositemp = ", rositemp, "ALE = ", ale, "RMaC = ", RMaC, "csi = ", csi)
            if rositemp > self.rosi:
                self.rosi = rositemp
                self.cmlist = cm_set
                self.cmValue = cmValue

        """need to add only attempted attacks to attack list"""
        # determine if attack will take place, if so, update wealth
        for att in self.attlist:
            # print(att, " being attempted")
            if random.random() <= att[0]:
                # attack is attempted
                # print(att, " attempted in round ", self.i, "for agent ", self.unique_id)
                if random.random() < (1 - RMaC):
                    # attack was successful
                    # print(att, " successful in round ", self.i, "for agent ", self.unique_id)
                    self.wealth -= att[1]
                """else:
                    #print(att, " failed to succeed")
            else:
                #print(att, " failed to attempt")"""

    # manages edge connections in the graph
    def friend_manager(self):
        # updates all nodes in the network
        self.all_nodes = self.model.grid.get_all_cell_contents()
        self.neighValue.append(self.cmValue + self.attValue)

        if self.i < 2:
            # gets initial friend list of agaent
            neighbors_nodes = self.model.grid.get_neighbors(
                self.pos, include_center=False
            )
            self.friends = self.model.grid.get_cell_list_contents(neighbors_nodes)
        else:
            # add new neighbors
            if len(self.friends) <= self.model.num_agents:
                for friend in self.friend_list:
                    if friend in self.friends:
                        continue
                    if friend.altruism > 99 and (
                        sum(friend.contrlist) / len(friend.contrlist)
                        > self.prob_add_friend
                    ):
                        self.friends.append(friend)

            # remove bad friends
            for friend in self.friends:
                if sum(friend.neighValue) / sum(friend.contrlist) > 100:
                    self.friends.remove(friend)

            # apply to be peoples friend
            for node in self.all_nodes:
                reciprocity = sum(node.contrlist) / len(node.contrlist)
                if reciprocity > 0.6 and node.gain > self.gain:
                    node.friend_list.append(self)

    # determine punishment
    def punisher(self):
        p = (
            abs(math.atan2(self.beta, self.alpha)) * (self.penalty - self.punish_cost)
        ) / (2 * self.punish_cost)
        self.prob_of_pun = min(p, 1)
        if random.random() <= self.prob_of_pun:
            for fr in self.all_nodes:
                if fr.contribution == 0:
                    """NEEDS REVIEW"""
                    fr.wealth -= self.penalty
                    self.wealth -= self.punish_cost
                    np = (
                        abs(math.atan(fr.beta)) * (self.penalty - self.punish_cost)
                    ) / 2
                    self.neighbor_prob_of_pun = min(np, 1)

    # calculate altruism
    def altruism_handler(self, other):
        for node in self.friends:
            tempAltList = []
            tempAlt = round(
                (
                    self.gain
                    - self.alpha * max(self.gain - other.gain, 0)
                    - self.beta * max(self.gain - other.gain, 0)
                ),
                2,
            )
            if tempAlt > 100:
                tempAlt = 100
            if tempAlt < -100:
                tempAlt = -100
            tempAltList.append(tempAlt)
        self.altruism = sum(tempAltList) / len(tempAltList)

    def give_money(self):
        self.friend_manager()

        # one random agent
        other = self.random.choice(self.all_nodes)

        # calculate free riders
        agent_contribution = [agent.contribution for agent in self.all_nodes]
        x = sum(agent_contribution)
        self.k = x / len(agent_contribution)  # % of free riders

        # punish
        if self.punish:
            self.punisher()

        # adjust altruism
        if len(self.friends) > 0:
            for node in self.friends:
                tempAltList = []
                tempAlt = round(
                    (
                        self.gain
                        - self.alpha * max(self.gain - other.gain, 0)
                        - self.beta * max(self.gain - other.gain, 0)
                    ),
                    2,
                )
                if tempAlt > 100:
                    tempAlt = 100
                if tempAlt < -100:
                    tempAlt = -100
                tempAltList.append(tempAlt)
            self.altruism = sum(tempAltList) / len(tempAltList)

        if len(self.friends) > 0:
            # calculate probability of contribution
            self.altlist.append(self.altruism)
            if self.k <= 0:  # if there are no freeriders, contribute
                self.prob_of_contr = 1
            else:
                a = decimal.Decimal(self.altruism - self.altlist[-2])
                b = decimal.Decimal(a) / decimal.Decimal(self.k)
                c = decimal.Decimal(1) + decimal.Decimal(math.e) ** b
                self.prob_of_contr = round(float(1 / c), 2)

            # decides if it will contribute
            if (random.random() <= self.prob_of_contr) and (self.wealth > 0):
                for node in self.friends:
                    node.cm_from_neighbors.append(self.cmlist)
                    node.att_from_neighbors.append(self.attlist)
                    node.neighValue.append(self.cmValue + self.attValue)
                    node.wealth += self.cmValue + self.attValue
                    self.wealth -= (self.cmValue + self.attValue) * 0.2
                self.contribution = 1
                self.contrlist.append(self.contribution)
            else:
                self.contribution = 0
                self.contrlist.append(self.contribution)
        else:
            self.contribution = 0
            self.contrlist.append(self.contribution)

    def step(self):
        if self.wealth > 0:
            self.attack()
            self.give_money()
            if self.punish:
                self.model.rosi = self.rosi + self.model.rosi
                self.gain = round(
                    (
                        self.wealth
                        - (self.cmValue + self.attValue)
                        + self.model.rosi
                        - (self.punish_cost * self.prob_of_pun)
                        - (self.penalty * self.neighbor_prob_of_pun)
                    ),
                    2,
                )
            else:
                model.rosi = self.rosi + model.rosi
                self.gain = round(
                    (self.wealth - (self.cmValue + self.attValue) + self.model.rosi), 2
                )
            self.i = self.i + 1
