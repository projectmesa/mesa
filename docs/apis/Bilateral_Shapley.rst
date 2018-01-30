
Bilateral Shapley Value API
================================

What is the Bilateral Shapley Value?
------------------------------------

The Shapley value is a key part of coalition game theory and was developed by Lloyd Shapley (https://en.wikipedia.org/wiki/Lloyd_Shapley). The central question of coalition game theory is the division of payoffs to the coalition of agents [Shoham and Leyton-Brown, 2009]. In other words, when we work together to get some payoff, how do we split up the payoff? The Shapley Value splits by marginal contribution, so the payoff is divided up by each agents relative contribution. This particular instantiation of the Shapley value borrows from two agent based implementations. First, Steven Ketchpel description "Coalition Formation Among Autonomous Agents" [1995] and second Mark Abdollahian, Zining Yang and Hal Nelson's implementation in "Techno-Social Energy Infrastructure Siting: Sustainable Energy Modeling Programming (SEMPro)" [2013]. A more detailed description of how specifically the module runs can be found below the implementation description. 

Uses
~~~~~
To assess how different agents may coalesce into groups. 

Dependencies
~~~~~~~~~~~~
The Bilateral Shapley module uses networkx 2.0

Implementation
--------------

.. code:: python

    from mesa.BilateralShapley import BSV

    coalition = BSV(agents, power_attribute, preference_attribute, efficiency_parameter, agent_id, compromise_parameter, verbose)

    # Show a list of how agents group together
    print (coalition.result)

    # Show a list of how agents grouped together and each groups power and preference attribute
    print (coalition.result_verbose)

    # Show a dictionary of each group, the agents within that group and each agents updated power and preference value based on their assimilation into the group
    print (coalition.subresults)

Required Parameters 
~~~~~~~~~~~~~~~~~~~~
**agents:** requires list of agent objects 
    
            self.schedule.agents from mesa module is an easy choice 

**power_attribute:** requires string

             agent attribute which assigns a numerical value of each agents relative power

**preference_attribute:** requires string

             agent attribute which assigns a numerical preference on a one-dimensional spectrum of each agents relative preference

Default Parameters 
~~~~~~~~~~~~~~~~~~~~
**efficiency_parameter:**  default = 1.5, requires float

             interesting coalition formations typically fall between > 1.0 and < 2.0. 1.0 or less results in no incentive to join a coalition (i.e. no coalitions) and usually more than 2.0 results in everyone joining the same coalition

**agent_id:**  default = "unique_id", requires string

             uses mesa unique_id attribute as default, module treats this value as a string

**compromise_parameter:** default = 0.95, requires float between 0 and 1

             at 1.0 when agents join a coalition their preference will become that of the coalitions; at 0.0 the agents will not alter their preference

**verbose:**  default = True, True or False input

             if True module will print out progress of algorithm showing how many iterations were required until optimal group formation

Example Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from mesa import Model
    from mesa.time import RandomActivation
    from mesa import Agent
    from BilateralShapley import BSV
    import numpy as np


    class TestAgent(Agent):
        '''Initialize agents with values for power and preference (in this case affinity as preference)'''
        def __init__(self, unique_id, model, maxaffinity, maxeconomic, maxmilitary):
            # use Mesa agent module
            super().__init__(unique_id, model)
            # preference attribute of each agent
            self.affinity = np.random.uniform(1, maxaffinity)
            # economic value of each agent which is combined with military for power
            self.economic = np.random.uniform(1,maxeconomic)
            # military value of each agent which is combined with economic for power
            self.military = np.random.uniform(1,maxmilitary)
            # calculate power as average economic and military power
            self.power = (self.economic+self.military) / 2


    class TestModel(Model):
        '''Initialize model'''
        def __init__(self, N, maxaffinity, maxeconomic, maxmilitary):
            self.numagents = N
            self.schedule = RandomActivation(self)
            for i in range(self.numagents):
                a = TestAgent(i, self, maxaffinity, maxeconomic, maxmilitary)
                self.schedule.add(a)
                
        
        '''Call the bsv module'''        
        def execution(self):
            testnet = BSV(self.schedule.agents, "power", "affinity", verbose = False)
            return testnet    


    test = TestModel(500, 20, 100, 100)
    test = test.execution()
    print ("Numer of Groups: ", len(test.result))
    print ("Group list: ", test.result)


Detailed Description of Module
------------------------------

Description
~~~~~~~~~~~

    This implementation of the Bilateral Shapley Value has three methods. 

    **Method 1: self.assess_coalitions(self.net)**

    Each agent computes the Shapley value with every other agent (see flow diagram) and creates a sorted list of the most preferred alliances  

    **Method 2: self.make_alliance(self.net, 'one')**

    Each agent tries to form a coalition with the most preferred agent in its sorted list of preferred coalitions. The combinations can get tricky as each agent may want to form a coalition with one agent. For example, in a list of 3 agent objects, Agent 1 and 2's most preferred agent may be agent 3. Whichever agent, agent 3 prefers the most will be the two who form a coalition. If they are all equal then the coalition will form based on the the order determined by the python sort function. As the function will iterate until no more alliance can be formed, the specific order becomes inconsequential if every agent has the same value. The one input indicates the algorithm is performing at the group level and not inside the groups. 

    **Method 3: self.new_node(self.net)**

    Once each agent has found their preferred coalition they then form a new node in the network graph with a new name, which is each agent's identifier separated by a "." (e.g. agent1.agent2). The coalition preference and power is calculated and a new graph which retains the information of each individual agent is created and stored in the sub results. 

    **Breaking alliances**

    After the coalition has been optimized, the module will go through each subgraph (agents within the coalition) and make sure each agent still wants to be a part of the coalition based on the coalition's preference and power relative to the individual agent's preference and power. If the agent no longer wants to participate then the agent leaves the coalition.   

    **Module Flow Diagram**


            .. image:: images/bilateralshapley/BilateralShapleyFlow.jpg

Weaknesses and Choices
~~~~~~~~~~~~~~~~~~~~~~

    As cooperative game theory examines combinations, increased agents increases computation time exponentially. Therefore, this module can not efficiently handle thousands of agents. 

    In order to reduce the computational burden and prevent the possibility of an infinite loop the module makes the choice for agents only to reexamine their alliances after the optimal coalition has been formed. As opposed to reexamining if an agent should be stay after each iteration of bilateral coalition formation. If the user wants the agents to reexamine their participation in the coalition after each iteration they can do this by simply tabbing lines #403 to #408 to be inside the primary loop. 


Happy Modeling!
----------------

This document is a work in progress. If you see any errors, exclusions
or have any problems please contact
`us <https://github.com/projectmesa/mesa/issues>`__.

``virtual environment``:
http://docs.python-guide.org/en/latest/dev/virtualenvs/

[2013] Abdollahian, Mark, Yang Zinig, and Hal Nelson. 2013. “Techno-Social Energy Infrastructure Siting : Sustainable Energy Modeling Programming ( SEMPro ).” Journal of Artifical Socieities and Simulation 16 (3): 1–12.

[1995] Ketchpel, S P. 1995. “Coalition Formation among Autonomous Agents.” From Reaction to Cognition, no. 957: 73–88.

[Shoham and Leyton-Brown, 2009] Yoav, Shoham, and Kevin Leyton-Brown. 2009. Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations. Kindle. New York: Cambridge University Press.

