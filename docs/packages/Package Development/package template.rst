
.. _package-template:

Package Template
=================

   **THIS IS JUST AN EXAMPLE------ADJUST, ADD OR DELETE AS YOU SEE FIT**

   Critical parts of the API are (1) describe the theory your instantiating and (2) cite your sources

   Flow diagrams are always encouraged

Provide an overview of your package?
------------------------------------

What is the theory, what is some background on when and how it was developed? What field does it fall in? ANy greate sucess or known uses?  

Uses
~~~~~
Generically, how is it used--how does it influence agent behavior or the environment  

Dependencies
~~~~~~~~~~~~
List other python libraries and version your package may depend on (or delete)

Implementation
--------------

show 

.. code:: python

    from <packagefilename> import <main class>

    <object> = <initiaition method>(parameter1, parameter2, parameter3)

    # provide some examples
    print (<object>.example1)

    # example2
    print (<object>.example2)

    


Required Parameters 
~~~~~~~~~~~~~~~~~~~~
Describe parameters your package requires---connection to Mesa as needed (add or delete as needed)

**Parameter1:** requires list of agent objects 
    
            self.schedule.agents from mesa module is an easy choice 

**Parameter2:** requires string

             agent attribute defined in agent instantiation

**Parameter3:** requires string

             agent attribute defined in agent instantiation

Default Parameters 
~~~~~~~~~~~~~~~~~~~~
Describe Default Parameters

**default_parameter1:**  default = 1.5, requires float

             add any illuminating details

**defauly_parameter2:**  default = "unique_id", requires string

             uses mesa unique_id attribute as default, module treats this value as a string

**verbose:**  default = True, True or False input

             if True module will print out lots of details about the package in progress

Example Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

If practicable provide an exmaple implmentation which produces a toy model

.. code:: python

    from mesa import Model
    from mesa.time import RandomActivation
    from mesa import Agent
    from <packagefilename> import <main class>
    import numpy as np


    class TestAgent(Agent):
        '''Initialize agents with values for paraemeter1 and parameter2'''
        def __init__(self, unique_id, model, maxparameter1, maxparameter2):
            # use Mesa agent module
            super().__init__(unique_id, model)
            # parameter1 attribute of each agent
            self.parameter1 = np.random.uniform(1, maxparameter1)
            # parameter2 value of each agent 
            self.parameter2 = np.random.uniform(1, maxparameter2)
            


    class TestModel(Model):
        '''Initialize model'''
        def __init__(self, N, maxparameter1, maxparameter2):
            self.numagents = N
            self.schedule = RandomActivation(self)
            for i in range(self.numagents):
                a = TestAgent(i, self, maxparameter1, maxparameter2)
                self.schedule.add(a)
                
        
        '''Call the bsv module'''        
        def execution(self):
            testnet = main(self.schedule.agents, "parameter1", "parameter2", verbose = False)
            return testnet    


    test = TestModel(500, 20, 100, 100)
    test = test.execution()
    print ("Numer of Groups: ", len(test.result))
    print ("Group list: ", test.result)


Detailed Description of Module
------------------------------
Provide a detailed description of your model

Description
~~~~~~~~~~~

    This implementation of the Super awesome theory has three methods. 

    **Method 1: self.method1(self.net)**

    Each agent computes the super awesome (see flow diagram) and chooses to do X or Y bases on their local situation

    **Method 2: self.method2(self.net)**

    The super awesome is calcuated and printed out
    

    **Key Points**

    Some things to consider or understand about your implementation   

    **Module Flow Diagram**

            Provide folder path and image name for a flow daigram or any other picutres you may want to add
            .. image:: images/folder/flowdiagram.jpg

Weaknesses and Choices
~~~~~~~~~~~~~~~~~~~~~~

    Every instantiation of a theory has problems and requires the programmer to make choices....discuss these


Appearance in Journals and Conferences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Not yet!



Happy Modeling!
----------------

This document is a work in progress. If you see any errors, exclusions
or have any problems please contact
`us <https://github.com/projectmesa/mesa/issues>`__.

``virtual environment``:
http://docs.python-guide.org/en/latest/dev/virtualenvs/

***sources you documentation cites!!!!!!**
