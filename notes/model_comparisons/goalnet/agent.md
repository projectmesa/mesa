# Agent object

### Description

```
    The basic agent class.

    This agent attempts to accomplish its Tasks by communicating with other
    agents it is connected with. More description will go here as we build it.

    Attributes:
        name: The agent's unique identifier.
        world: The World (simstate) object

        propensity_to_help: The agent's initial willingness to help others
        centralization: The agent's willingness to share contacts
        greed: The proportion of task payoff an agent is inclined to keep
        beta: The discount factor on past events; currently fixed at 1.

        inbox: A list that holds the agents' messages received.Gets cleared by
               the agent every turn as the contained messages are processed
        task: Current task object; defaults to None
        possible_tasks: Tasks other agents requested help on
        turns: How many times the agent has been activated
        history: Keep track of history, who worked with and what payoff
            received, potentially how the ego felt about the payoff
        network: List of agents with whom this agent can communicate
        wealth: The total cumulative payoff received, less payoff distributed

        Willingness To Help (WTH) model:
        ===============================
            History coding:
            --------------
                Received help from B:    +1.0
                B provides introduction: +0.5
                B DOESN'T provide intro: -1.0
                B provides payoff:
                    (ActualPay - FairPay)/FairPay
```

### __init__(self, name, world, propensity_to_help, centralization, greed)

```
    name
    world
    propensity_to_help
    centralization
    greed

    inbox  #where msgs are received from others
    task
    task_contributors  #Agents who have performed subtasks
    possible_tasks
    turns  #keep track of how many turns an agent has had

    history []
    outstanding_payoffs {}

    beta # Past discount factor

    task_team []
    network []
    wtf {}  # Most recent willingness-to-help for each neighbor
    wealth  #This could be the cumulative payoffs
```

### activate(self) (aka run)

##### Description
```
The agent's sequence of actions each activation.

The sequence is:
    a. Evaluate each message in the inbox
    b. Choose an action
    c. Receive / Distribute payoffs
```
##### What happens
```
    turns -- add to the number

    # Evaluate messages
    possible_tasks

    # Choose action
    action, target = choose_action

    #Take action
        #send a message to another agent in network
            #create new Message object
            #ask for introduction
            # If working on someone else's task, send them a message.
            #look for an introduction from another agent in network
            #error, this condition should not occur at this time

        # Check to see if task complete; if so, distribute payoffs
            # Distribute payoffs
            # Compute relative payoffs
```

### Other methods

```
    _willingness_to_help(self, neighbor)
        Compute agent's Willingness to Help the specified neighbor.

        Takes into account both the interactions with that specific agent
        and with all others.

        Returns the computed WTH number, and logs it in self.wth[neighbor]

    _choose_action(self)
        Choose an action to take this turn.

        # Build task probabilities
        # Pick a task based on payoff
            # If none, decide whether to communicate or seek
```

#### Message Handling

```
    get_message(self, message)
        Receive a message from another agent.
        Args:
            message: A message object to be added to the inbox

    evaluate_message(self, message)
        Process a given message in the inbox.

        '''
        Message types
            'HelpRequest':
            'ContactRequest'
            'Acknowledgment'
            'Payoff'

    process_help_request(self, message)
        #Add the task to list of possible tasks to choose from at a later time

    process_contact_request(self, message)
        Optionally introduce the requester to a new neighbor.              #Update the networks of both the agents

    process_acknowledgment(self, message)
        Add a history event when another agent works on your task

    process_payoff(self, message)
        Record the payoff received from an agent; increment wealth and history.
        The specific increment will be based on fairness.
```
