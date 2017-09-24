from mesa import Agent, Model
from mesa.space import MultiGrid, SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random
import pandas
import os

habitat_CHOICES = ["Forest", "Grassland"]

class HabitatPatch(Agent):
    def __init__(self, model, unique_id, habitat):
        super().__init__(unique_id, model)
        self.habitat = habitat

class Organism(Agent):
    def __init__(self, model, unique_id, habitat_pref):
        super().__init__(unique_id, model)
        self.habitat_pref = habitat_pref
        self.death_rate = 0.1
        self.birth_rate = 0.1
        self.habitat_specificity = 1
        self.alive = True
        self.reported = False
        
    def isHappy(self):
        cell = self.model.grid[self.pos[0]][self.pos[1]]
        #loop over all agents in a cell
        #there will be exactly 1 HabitatPatch agent and 0 or more Organism agents
        for agent in cell:
            try:
                #the patch agent has a habitat attribute, so check if it is the same as the habitat_pref attribute of self
                return agent.habitat == self.habitat_pref
            except: 
                #any organism agents don't have a habitat attribute, so they are an exception and we pass on them
                pass
    
    def move(self):
        moveOrNot = None
        if self.isHappy():
            # if agent is happy, then decide whether to move based on habitat specificity
            if random.random() < self.habitat_specificity:
                moveOrNot = "Not"
        else:
            moveOrNot = "Move"
        if moveOrNot == "Move":
            possible_steps=self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
    
    def die(self):
        if self.alive == True:
            if random.random() < self.death_rate:
                self.alive = False
    
    def birth(self):
        if self.alive == True:
            if random.random() < self.birth_rate:
                baby = Organism(self.model, "Organism" + str(len(self.model.schedule.agents)).zfill(6), self.habitat_pref)
                self.model.grid.place_agent(baby, self.pos)
                self.model.schedule.add(baby)
            
    
    def step(self):
        self.move()
        self.die()
        self.birth()
        

class HabitatModel(Model):
    def __init__(self, height, width, N, method, outdir, filename=None):
        if method == "fromFile" and not filename:
            raise Exception("you must include a filename to create a world from a file")

        self.running = True

        self.height=height
        self.width=width
        self.N=N
        self.method=method
        self.filename=filename
        self.outdir = outdir

        self.grid = MultiGrid(self.height, self.width, False)
        self.schedule = RandomActivation(self)

        # Create patches
        self.createPatches()
        self.createAgents()
        self.datacollector = MyDataCollector(
            agent_reporters={
                             "x": lambda a: a.pos[0],
                             "y": lambda a: a.pos[1],
                             "alive": lambda a: a.alive,
                             "habitat_preference": lambda a: a.habitat_pref
                             }
                         )
    def cleanUp(self):
        outfile="fossil-record_output.csv"
        self.datacollector.get_agent_vars_dataframe().to_csv(os.path.join(self.outdir, outfile))
        
    def createPatches(self):
        if not self.method in ["random", "rectangle", "fromFile"]:
            raise Exception("unrecognized method for creating patches")
        if self.method=="random":
            for cell, index in zip(self.grid.coord_iter(), range(self.height*self.width)):
                patch = HabitatPatch(self,"patch"+str(index),random.choice(habitat_CHOICES))
                cell_content, x, y = cell
                self.grid.place_agent(patch, (x, y))
        elif self.method=="rectangle": #nonrandom habitat patches
            for cell, index in zip(self.grid.coord_iter(), range(self.height*self.width)):
                cell_content, x, y = cell
                if x < list(range(width))[len(range(width))//2]:
                    patch = HabitatPatch(self,"patch"+str(index),habitat_CHOICES[0])
                else:
                    patch = HabitatPatch(self,"patch"+str(index),habitat_CHOICES[1])
                self.grid.place_agent(patch, (x, y))
        elif self.method=="fromFile":
            df = pandas.read_csv(os.path.join(self.outdir, self.filename))
            fileWorldSize = int(df.shape[0]**(0.5)) #take square root of row count to get size of square
            if not fileWorldSize == self.grid.width or not fileWorldSize==self.grid.height:
                raise Exception("The size of the world in the file doesn't match the height and width of the HabitatModel object. Note: world must be square. ")
            for tup in df.itertuples():
                row = [int(each) for each in tup[1].split(' ')]
                index = tup[0]
                patch = HabitatPatch(self, "patch"+str(index), habitat_CHOICES[row[2]-1]) #subtract 1 to work with python zero-indexing
                self.grid.place_agent(patch,(row[0]-1,row[1]-1))


    def createAgents(self):
        for index in range(self.N):
            agent = Organism(self, "Organism" + str(index).zfill(6), random.choice(habitat_CHOICES))
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
    
    def allDead(self):
        responses = []
        for agent in self.schedule.agents:
            responses.append(agent.alive==False)
        return all(responses)
        
    def markReported(self): 
        #method to mark a dead agent as having been reported. Must be run AFTER data collection to ensure desired behavior
        for agent in self.schedule.agents:
            if agent.alive == False:
                agent.reported = True
        
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.markReported()
        if self.allDead():
            self.cleanUp()
            self.running=False
        
            
            
class MyDataCollector(DataCollector):
    ## subclass DataCollector to only collect data on dead agents that haven't been reported yet
    def collect(self, model):
        """ Collect all the data for the given model object. """
        if self.model_reporters:
            for var, reporter in self.model_reporters.items():
                self.model_vars[var].append(reporter(model))

        if self.agent_reporters:
            for var, reporter in self.agent_reporters.items():
                agent_records = []
                for agent in model.schedule.agents:
                    if agent.alive == False and agent.reported == False:
                        agent_records.append((agent.unique_id, reporter(agent)))
                self.agent_vars[var].append(agent_records)