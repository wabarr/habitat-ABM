from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from habitat_model import HabitatModel, HabitatPatch, Organism

def agent_portrayal(agent):
    if isinstance(agent, HabitatPatch):
        if agent.habitat == "Grassland":
            color = "#ccc133"
        elif agent.habitat == "Forest":
            color = "#347026"
        portrayal = {"Shape": "rect",
                 "Color": color,
                 "Filled": "true",
                 "Layer": 0,
                 "w":1,
                 "h":1}
    if isinstance(agent, Organism):
        if agent.habitat_pref == "Grassland":
            color = "#efe883"
        elif agent.habitat_pref == "Forest":
            color = "#69c452"
        portrayal = {"Shape": "circle",
                     "Color": color,
                     "Layer": 1, 
                     "Filled":"true",
                     "r":0.5}
    return portrayal

grid = CanvasGrid(agent_portrayal, 20, 20, 500 , 500)
server = ModularServer(HabitatModel,
                       [grid],
                       "Habitat Grid", 
                      20, 20, 100, False)
server.port = 8889
server.launch()