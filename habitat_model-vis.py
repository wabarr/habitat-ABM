from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from habitat_model import HabitatModel, HabitatPatch, Organism

def agent_portrayal(agent):
    try: #patches have habitat attributes
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
    except AttributeError: #these are the agents because theyhave no habitat attribute
        if agent.alive:
            if agent.habitat_pref == "Grassland":
                color = "#efe883"
            elif agent.habitat_pref == "Forest":
                color = "#69c452"
            portrayal = {"Shape": "circle",
                         "Color": color,
                         "Layer": 1, 
                         "Filled":"true",
                         "r":0.5}
        else:
            return None
    return portrayal

grid = CanvasGrid(agent_portrayal, 100, 100, 800 , 800)
server = ModularServer(HabitatModel,
                       [grid],
                       "Habitat Grid", 
                      100, 100, N=200, method="fromFile", filename="patchyworld.csv")
server.port = 8889
server.launch()
