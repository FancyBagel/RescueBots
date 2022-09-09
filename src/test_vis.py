from os import wait
from time import sleep
import mesa
from Visuals import *
from RescueModel import *

assets = [
    {"weight": 1,
     "value": 1,
     "pos": (1, 1)},
    {"weight": 1,
     "value": 1,
     "pos": (2, 10)},
    {"weight": 1,
     "value": 1,
     "pos": (3, 13)},
    {"weight": 1,
     "value": 1,
     "pos": (4, 9)},
    {"weight": 1,
     "value": 1,
     "pos": (5, 0)}
]

humans = [
    {"isConscious": True,
     "pos": (9, 3)},
    {"isConscious": True,
     "pos": (2, 8)},
    {"isConscious": True,
     "pos": (10, 8)},
    {"isConscious": True,
     "pos": (4, 11)},
    {"isConscious": True,
     "pos": (0, 14)},
    {"isConscious": True,
     "pos": (9, 13)},
    {"isConscious": True,
     "pos": (8, 2)},
    {"isConscious": True,
     "pos": (12, 4)},
    {"isConscious": True,
     "pos": (5, 1)},
    {"isConscious": True,
     "pos": (14, 14)},
]

exitFields = [
    {"pos": (0, 0)},
    {"pos": (0, 2)},
    {"pos": (0, 5)},
    {"pos": (5, 0)},
]

#model = RescueModel(1000, 15, 15, 0, 5, 5, assets, humans, [], [])
#
#for i in range(10):
#    model.step()
#    print("STEP " + str(i))
#    for agent in model.schedule.agents:
#        print(str(agent.unique_id) + " " + str(agent.pos))
#
#humanGrid = mesa.visualization.CanvasGrid(humanPortrayal, 15, 15, 750, 750)
grid = mesa.visualization.CanvasGrid(agentPortrayal, 15, 15, 750, 750)
chart = mesa.visualization.ChartModule([{
        "Label": "rescuedConscious",
        "Color": "Black"}],
        data_collector_name="datacollector")
server = mesa.visualization.ModularServer(
    RescueModel, [grid,chart], "Rescue Model", {
        "T": 1000,
        "m": 15,
        "n": 15,
        "R": 2,
        "A": 5,
        "P": 10,
        "assets": assets,
        "people": humans,
        "personalities": [],
        "exitFields": exitFields 
    }
)

server.port = 8521
server.launch()

while server.model.running:
    sleep(1)
    print("Simulation")

print("Simulation finished")