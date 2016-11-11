from mesa import Agent, Model
from mesa.space import MultiGrid, SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random


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
        self.habitat_specificity = 0.9
        self.alive = True
        self.reported = False
        
    def isHappy(self):
        cell = self.model.grid[self.pos[0]][self.pos[1]]
        for agent in cell:
            try:
                return agent.habitat == self.habitat_pref
            except: #these are the patch agents, that will have no habitat_pref
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
    def __init__(self, height, width, N, randPatches):
        self.running = True
        self.grid = MultiGrid(height, width, False)
        self.schedule = RandomActivation(self)
        # Create patches
        self.createPatches(height, width, randPatches)
        self.createAgents(N)
        self.datacollector = MyDataCollector(
            agent_reporters={
                             "x": lambda a: a.pos[0],
                             "y": lambda a: a.pos[1],
                             "alive": lambda a: a.alive,
                             "habitat_preference": lambda a: a.habitat_pref
                             }
                         )
    def cleanUp(self):
        self.datacollector.get_agent_vars_dataframe().to_csv("./output.csv")
        
    def createPatches(self, height, width, randPatches):
        if randPatches==True:
            for cell, index in zip(self.grid.coord_iter(), range(height*width)):
                patch = HabitatPatch(self,"patch"+str(index),random.choice(habitat_CHOICES))
                #self.schedule.add(patch)
                cell_content, x, y = cell
                self.grid.place_agent(patch, (x, y))
        else: #nonrandom habitat patches
            for cell, index in zip(self.grid.coord_iter(), range(height*width)):
                cell_content, x, y = cell
                if x < list(range(width))[len(range(width))//2]:
                    patch = HabitatPatch(self,"patch"+str(index),habitat_CHOICES[0])
                else:
                    patch = HabitatPatch(self,"patch"+str(index),habitat_CHOICES[1])
                self.grid.place_agent(patch, (x, y))
                
            
    def createAgents(self, N):
        for index in range(N):
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