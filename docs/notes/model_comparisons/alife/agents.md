
# Agent object

```
    __init__
        x
        y
        genone
        coords

        id
        species
        alive - bool
        env
        inc
        stop_delta
        temp
        anneal_rate

        who_are_parents

        energy
        energy_move_delta

        ### how much energy do I spend in mating and childbirth?
        energy_mating_delta
        energy_childbirth_delta

        max_lifespan

        movement_rate

        vision_radius

        size
        growth_energy_threshold
        growth_rate

        food_source
        consumption_rate

    run(self)
        fov
        avoid obstacles

        energy
        die

        i am scared()
        i am hungry()
        i want a baby()

        #Check for neighbors; if you see an agent of same species, come closer
        #Otherwise, RUN!

    avoid_obstacles(self,fav)
        calculate obs

    getFOV(self)
        fov

    i_am_scared(self)
        am I prey?
        move away.

    i_am_hungry(self)
        eat some grass if needed

    i_want_a_baby
        ##### MUST PREVENT INCEST!
        stuff w/ neighbors
        mate

    get_food_cells(self,fov)
        find cells around me that have food

    expend_energy(self,units)
        recalculate energy

    get_neighbors
        get neighbors based on radius and vision

    move_towards_agent(self,agent)

    move_toward_cell(self,x,y)

    move_away_from_agent(self,agent)

    move(self)

    eat_grass
        ### TODO: consume the food at the current patch
        ### OR -- if I'm a predator -- consume my prey at the consumption rate

    eat_critter(self, agent)
        energy
        die
        removeAgent()

    mate(self)
        ### if next to me is a member of my species (i.e. genome match > 70%)
        ### then we should mate and make babies
        neighbor check

    mate_with_agent(self,agent)
        ### perform genome crossover
        ##### MUST PREVENT INCEST!
        ### make some babies

    fight(self)
        ### if next to me is another animal, fight with them
        ### the outcome is determined by the size and energy difference
        pass

    die(self)
        ### did our energy run out? or did we just get eaten?
        alive - False
        removeAgent

    fitness(self, x)
        #return nk.fitness(x,self.weights)
        ### return estimated value of changing my own genome
        return 1

    random_x(self)
        [random() for z in range(self.dim)]

    anneal(self,x)
        """ make a small move in a direction that results in improvement in fitness"""

    hillclimb_agent(self)
        genome
        fitness

    anneal_agent(self)
        genome
        fitness

    hillclimb(self,x)
        """ make a small move in a direction that results in improvement in fitness"""

```
