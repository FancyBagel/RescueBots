import mesa
from threading import Thread
from queue import Queue
from src.Utility import parseInput
from src.Visuals import agentPortrayal
from src.RescueModel import RescueModel
from pandas import DataFrame
import sys

path = str(sys.argv[1])

model, assets, people, exits = parseInput(path)

q = Queue()


def getAndSaveData(queue):
    (rescuedInfo, eventLog) = queue.get()
    rescuedConscious = rescuedInfo.iloc[-1]["rescuedConscious"]
    rescuedUnconscious = rescuedInfo.iloc[-1]["rescuedUnconscious"]
    assetValue = rescuedInfo.iloc[-1]["assetValue"]
    eventLog.to_csv("results/eventLog.csv")
    finalScore = open("results/finalScore.txt", "w+")
    finalScore.write(str(rescuedConscious) + " " +
                     str(rescuedUnconscious) + " " +
                     str(assetValue))
    finalScore.close()


simThread = Thread(None, getAndSaveData, "logThread", (q, ))
simThread.start()


grid = mesa.visualization.CanvasGrid(agentPortrayal,
                                     model["width"],
                                     model["height"],
                                     600, 600)

chart = mesa.visualization.ChartModule([{
    "Label": "rescuedConscious",
    "Color": "Black"}],
    data_collector_name="datacollector")


server = mesa.visualization.ModularServer(
    RescueModel, [grid, chart], "Rescue Model", {
        "T": model["timeLimit"],
        "m": model["width"],
        "n": model["height"],
        "R": model["robotCount"],
        "A": model["assetCount"],
        "P": model["peopleCount"],
        "assets": assets,
        "people": people,
        "exitFields": exits,
        "returnQueue": q
    }
)
server.launch()
