# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 11:39:17 2017

@title: Bilateral Shapely Value
@author: Tom Pike
"""

import networkx as nx
from operator import attrgetter


class BSV:
    '''
    Tasks:
        1. Establish two networks graphs based on agent attributes
        2. Execute Bilateral Shapely Value
        3. Store results in three ways, list of coaltions,
           list of coalitions with attributes,
           dictionary of coalitions and their attributes.

    Purpose: Pass in the agents and specificed attributes and run through
             the bilateral Shapely value
    '''

    def __init__(self, agents, power_attribute, preference_attribute,
                 efficiency_parameter=1.5, agent_id="unique_id",
                 compromise=0.95, verbose=True):
        self.agent_list = agents
        self.net = nx.Graph()
        # create duplicate graph to reference for heirarchial networks
        self.orignet = nx.Graph()
        # determines when coalitions optimized
        self.coalesced = False
        self.efficiency = efficiency_parameter
        self.comp = compromise
        # verbose parameter for print updates
        self.verbose = verbose
        # create empty dictionary for subnets
        self.subnets = {}
        # variable to make process more computationally efficient
        self.most = 0
        # use attrgetter to extract inputed strings
        agent_id = attrgetter(agent_id)
        power = attrgetter(power_attribute)
        preference = attrgetter(preference_attribute)
        # add agents into nodes- requires two
        # so can reference individual agent
        for a in self.agent_list:
            node = agent_id(a)
            # May need to undo later for final result
            if isinstance(node, str):
                pass
            else:
                node = str(node)
            # primary
            self.net.add_node(node)
            # duplicate
            self.orignet.add_node(node)
            # primary
            self.net.node[node]["power"] = power(a)
            # duplicate
            self.orignet.node[node]["power"] = power(a)
            # primary
            self.net.node[node]["preference"] = preference(a)
            # duplicate
            self.orignet.node[node]['preference'] = preference(a)
            # primary
            self.net.node[node]["maybe_mates"] = []
            # duplicate
            self.orignet.node[node]["maybe_mates"] = []
            # primary
            self.net.node[node]['g_dis'] = False
            # duplicate
            self.orignet.node[node]["g_dis"] = False
        # Results storage objects
        self.result = None
        self.result_verbose = None
        self.subresults = None
        # Run the algorithm
        self.execution()

    '''
    HELPER FUNCTION

    1. Make subnet - Allows for detailed look of each coalition

    '''

    def make_subnets(self, newname, node1, node2, newpref):
        '''
        Tasks:
            1. Make network graph of each coalition
            2. Store each agents power and preference variables
        '''
        # empty list to track groups in subnetwork
        group_list = []
        # Get agent names out
        start = 0
        stop = 0
        # Iterate through name to look for periods and append to group list
        for l in range(len(newname)):
            if newname[l] == '.':
                stop = l
                group = newname[start: stop]
                group_list.append(group)
                start = stop + 1
        # get last name
        group_list.append(newname[start:])
        # print (tribename)
        # print (tribe_list)
        # check if both sub_network exists
        self.subnets[newname] = nx.Graph()
        # add each node with attributes
        for each in group_list:
            # calculate new preference
            diff = self.orignet.node[each]['preference'] \
                   + ((newpref - self.orignet.node[each]['preference'])
                      * self.comp)
            self.subnets[newname].add_node(each)
            self.subnets[newname].node[each]['preference'] = diff
            self.orignet[each]['preference'] = diff
            # update reference dictionary with
            # new afFinity value based on alliances
            self.subnets[newname].node[each]['power'] = \
                self.orignet.node[each]['power']
            self.subnets[newname].node[each]['maybe_mates'] = \
                self.orignet.node[each]['maybe_mates']
            self.subnets[newname].node[each]['g_dis'] = \
                self.orignet.node[each]['g_dis']

        if node1 in self.subnets.keys():
            self.subnets.pop(node1)
        if node2 in self.subnets.keys():
            self.subnets.pop(node2)

    '''
    MAIN FUNCTIONS

    1. assess_coalitions: determines best matches for every agent
    2. make_alliance: find best option based on
    all the combinations and form link
    3. new_node: create new nodes form aligned
    agents and remove them as a stand alon agent
    '''

    def assess_coalitions(self, network):

        '''
        Tasks:
        1. As a node iterate through each node
        2. assess the expected utility of a coalition formation
        3. find the best possible match
        4. store as an attirbute of the node

        Purpose: To look over all combinations and find the best alliance
        '''

        # iterate over graph and create links with those most like you
        for n1, d1 in network.nodes(data=True):
            # reset maybe_mates for each round of coalition formation
            d1["maybe_mates"] = []

            # iterate over nodes to find allies
            for n2, d2 in network.nodes(data=True):
                # ensure nodes does not link to self
                if n1 != n2:
                    # determine expected utility of alliance
                    pot_eu = ((d1['power'] + d2['power'] * self.efficiency)) \
                             * (1 - (abs(d1['preference'] - d2['preference'])))

                    # determine bilateral shapely value for both agents
                    shape1 = 0.5 * d1['power'] + 0.5 * (pot_eu - (d2['power']))
                    shape2 = 0.5 * d2['power'] + 0.5 * (pot_eu - (d1['power']))
                    # ensure no alliance is made which result
                    # in a decrease in either parties utility
                    if shape1 > d1['power'] and shape2 > d2['power']:
                        # if a coalition increases both utilities
                        # then add to list of node1
                        d1['maybe_mates'].append([shape1, n2, pot_eu])

            # sort list of possible alliances for highest shapely value
            d1['maybe_mates'].sort(key=lambda x: x[0], reverse=True)

            # ensures unecessary calculations are prevented in
            # make alliance function (belowO by finding max length of tribes
            if len(d1['maybe_mates']) > self.most:
                self.most = len(d1['maybe_mates'])

            # append index number (i.e. rank) of each tribe to list
            for each in d1['maybe_mates']:
                each.append(d1['maybe_mates'].index(each))

    def make_alliance(self, network, level):
        '''
        Tasks:
        1. iterate through each possible alliance
        increasing index value (poss variable)
        2. if best bet form link

        Purpose: A computationally efficient way to find
        best link for each node
        '''

        # empty list to keep track of nodes with edges
        allied = []
        # iterate through nodes
        poss = 1
        # keep creating links while value is shorter
        # then the greatest number of possible alliances
        while poss < self.most:
            # iterate through nodes
            for each in network.nodes(data=True):
                # if in allied list pass (already has an edge)
                if each[0] in allied:
                    pass
                # look at data of potential allies
                else:
                    # iterate through possible mates 1 index is name
                    for e in each[1]['maybe_mates']:
                        if e[3] <= poss:
                            # ensure node isnot already allied
                            if e[1] not in allied and each[0] not in allied:
                                # iterate through possible mates
                                for i in network.node[e[1]]["maybe_mates"]:
                                    # see if node is a possible mate
                                    if i[1] == each[0]:
                                        # ensure less than current value
                                        if network.node[e[1]]['maybe_mates'].\
                                                index(i) <= poss:
                                            # make alliance
                                            network.add_edge(each[0], e[1])
                                            # add both nodes to list
                                            allied.append(each[0])
                                            allied.append(e[1])
            # increase value of poss to explore next best option
            poss += 1
        if level == 'two':
            self.coalesced = True

        # if no more alliances are made change variable to stop
        if len(allied) == 0:
            self.coalesced = True

    def new_node(self, network):

        '''
        Tasks:
            1. Calculate new agents based on those
            agents who established a link
            2. Form subnet of agents based on agents who joined
            3. Remove individuals agents form network
            who are not part of coalition

        Purpose: Create heirarchies of networks
        '''

        # iterate through each group which has an edge and put in list
        new_nodes = []
        new_pows = []
        new_prefs = []
        for one, two in network.edges():
            # use aggressive caching
            prefA = network.node[one]['preference']
            prefB = network.node[two]['preference']
            powA = network.node[one]['power']
            powB = network.node[two]['power']
            # calculate new preference
            newpref = ((prefA * powA) + (prefB * powB))/(powA + powB)
            new_prefs.append(newpref)
            # calculate new power
            newpow = (powA + powB) * self.efficiency
            new_pows.append(newpow)
            # new node name
            new_nodes.append([one, two])

        # iterate through list of alliances
        for i in new_nodes:
            # print (i)
            # combine goroup names into a new name
            newname = i[0] + "." + i[1]
            # print (newname)
            # get index of item
            idx = new_nodes.index(i)
            # add the new combined node
            network.add_node(newname)
            # add new power attribute
            network.node[newname]['power'] = new_pows[idx]
            # add new affinity attributes
            network.node[newname]['preference'] = new_prefs[idx]
            # create empy possible mates key
            network.node[newname]['maybe_mates'] = []
            network.node[newname]['g_dis'] = 'False'

            ##################################################################
            # SUBNET COMMAND
            ################################################################
            # make new subnetwork
            self.make_subnets(newname, i[0], i[1], new_prefs[idx])

            # remove node from graph
            network.remove_node(i[0])
            network.remove_node(i[1])

    def check_alliances(self, subs, nets):

        '''
        Tasks:
        1. Determine if any memeber of a coalition wants to leave
        2. Remove from coalition and add back into population

        Purpose: Ensure each agent in the colation still wants to belong
        '''

        dis = []
        c = 0
        for key, sub in subs.items():
            for group in sub.nodes(data=True):
                # print (nets.node[key]['power'])
                # print (list(sub.nodes()), group[0])
                # determine potential utility for primary group
                # and each sub agent wihtin the group
                pot_eu = ((nets.node[key]['power']
                           + group[1]['power'] * self.efficiency)) \
                           * (1 - (abs(nets.node[key]['preference']
                                   - group[1]['preference'])))
                # print (pot_eu)
                # determine bilateral shapely value for both agents
                shape1 = 0.5 * nets.node[key]['power'] \
                    + 0.5 * (pot_eu - (group[1]['power']))
                shape2 = 0.5 * group[1]['power'] \
                    + 0.5 * (pot_eu - nets.node[key]['power'])

                if shape1 < nets.node[key]['power'] or \
                        shape2 < group[1]['power']:
                    # if no longer beneficial to stay in group remove
                    # create dummy example to determine who to remove
                    first = group[0] + "."
                    mid = "." + group[0] + "."
                    end = "." + group[0]
                    if mid in key:
                        dis.append([group[0], mid, key])

                    elif first in key:
                        dis.append([group[0], first, key])

                    elif end in key:
                        dis.append([group[0], end, key])

                    group[1]['g_dis'] = 'True'
                    c += 1

        for item in dis:
            # remove node from subnet
            subs[item[2]].remove_node(item[0])
            # print (item[0])
            # add node back into population
            nets.add_node(item[0])
            nets.node[item[0]]['power'] = \
                self.orignet.node[item[0]]['power']
            nets.node[item[0]]['preference'] = \
                self.orignet.node[item[0]]['preference']
            nets.node[item[0]]['maybe_mates'] = []
            nets.node[item[0]]['g_dis'] = "True"

        # remove any empty nodes
        empty_nets = []
        for key, graph in subs.items():
            nodes = list(graph.nodes())
            if len(nodes) == 0:
                empty_nets.append(key)

        # print (empty_nets)
        for g in empty_nets:
            del subs[g]
            nets.remove_node(g)

    def execution(self):

        '''
        Tasks:
            1. Run three main functions to form alliance
            2. After colaitions form, see if agents still want to be in group
            3. Store results

        Purpose: Run algorithm and store results
        '''

        count = 1
        while not self.coalesced:
            if self.verbose:
                print("Iteration: " + str(count))
                print("Assessing Coalitions")
            self.assess_coalitions(self.net)
            if self.verbose:
                print("Forming Coalitions")
            self.make_alliance(self.net, 'one')
            if self.verbose:
                print("Making New Agent Population \n\n")
            self.new_node(self.net)
            count += 1

        for each in self.subnets.items():
            self.coalesced = False
            # print (each)
            while not self.coalesced:
                self.assess_coalitions(each[1])
                self.make_alliance(each[1], 'two')
        self.check_alliances(self.subnets, self.net)
        self.result = (list(self.net.nodes()))
        self.result_verbose = (list(self.net.nodes(data=True)))
        subresults = {}
        for i in self.subnets.keys():
            subresults[i] = list(self.subnets[i].nodes(data=True))
        self.subresults = subresults
        # END
