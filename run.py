from src.RescueModel import RescueModel
from src.Utility import parseInput, ensureResultLocation
import sys


path = str(sys.argv[1])

modelInfo, assets, people, exits = parseInput(path)

model = RescueModel(
    modelInfo["timeLimit"],
    modelInfo["width"],
    modelInfo["height"],
    modelInfo["robotCount"],
    modelInfo["assetCount"],
    modelInfo["peopleCount"],
    assets,
    people,
    exits
)

model.run_model()

rescuedInfo = model.datacollector.get_model_vars_dataframe()
eventLog = model.datacollector.get_table_dataframe("Saved")

rescuedConscious = rescuedInfo.iloc[-1]["rescuedConscious"]
rescuedUnconscious = rescuedInfo.iloc[-1]["rescuedUnconscious"]
assetValue = rescuedInfo.iloc[-1]["assetValue"]

ensureResultLocation("results/")
eventLog.to_csv("results/eventLog.csv")
finalScore = open("results/finalScore.txt", "w+")
finalScore.write(str(rescuedConscious) + " " +
                 str(rescuedUnconscious) + " " +
                 str(assetValue))
finalScore.close()