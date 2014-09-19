

# Model

#From schelling
#model.grid.get_neighbors(self.x, self.y, moore=True)

empty
it may or may not have grid
it may have a scheduler; you can probably assume this

Scheduler maintains a list of agents
To kill and agent, you remove it from the scheduler
Then it won't exist. (You have to explicitly)



# Agent
# What do agents have

Attributes:
    unique id
        starting at 1 and counting up

step()
    do this when you are activated
    this is a tick

__init__()
    set the unique id




