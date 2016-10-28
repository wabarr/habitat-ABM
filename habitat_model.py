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
        
    def isHappy(self):
        cell = self.model.grid[self.pos[0]][self.pos[1]]
        for agent in cell:
            try:
                return agent.habitat == self.habitat_pref
            except: #these are the patch agents, that will have no habitat_pref
                pass
    
    def step(self):
        if self.isHappy():
            pass
        else:
            possible_steps=self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
            
    
class HabitatModel(Model):
    def __init__(self, height, width, N, randPatches):
        self.running = True
        self.grid = MultiGrid(height, width, False)
        self.schedule = RandomActivation(self)
        # Create patches
        self.createPatches(height, width, randPatches)
        self.createAgents(N)
        self.datacollector = DataCollector(
            agent_reporters={ 
                             "x": lambda a: a.pos[0],
                             "y": lambda a: a.pos[1]
                             }
                         )
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
            agent = Organism(self, "Organism" + str(index), random.choice(habitat_CHOICES))
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
        
    def allHappy(self):
        responses = []
        for cell in self.grid:
            for agent in cell:
                try:
                    responses.append(agent.isHappy())
                except AttributeError:
                    pass
        return all(responses)
    
                
    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.datacollector.collect(self)
        if self.allHappy():
            self.running=False
