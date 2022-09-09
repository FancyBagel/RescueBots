from functools import singledispatch
import mesa
from src.Utility import *


    


def agentPortrayal(agent):
    humanPortrayal = {
        "Shape": "circle",
        "r": 0.4,
        "Layer": 1,
        "Filled": "True",
        "Color": "green",
        "xAlign": 0.75,
        "yAlign": 0.25,
        "text_color": "white"
    }
    
    assetPortrayal = {
        "Shape": "circle",
        "r": 0.4,
        "Layer": 1,
        "Filled": "True",
        "Color": "red",
        "xAlign": 0.25,
        "yAlign": 0.75,
        "text_color": "white"
    }

    robotPortrayal = {
        "Shape": "circle",
        "r": 0.4,
        "Layer": 1,
        "Filled": "True",
        "Color": "black",
        "xAlign": 0.25,
        "yAlign": 0.25,
        "text_color": "white"
    }
    
    exitPortrayal = {
        "Shape": "exit.png",
        "Scale": 1,
        "Layer": 0
    }
    
    def robotsInCell(agent):
        totalRobots = 0
        for neigh in agent.model.grid.get_cell_list_contents([agent.pos]):
            if neigh.type == AgentType.Robot:
                totalRobots += 1
        return totalRobots

    def valueInCell(agent):
        totalValue = 0
        for neigh in agent.model.grid.get_cell_list_contents([agent.pos]):
            if neigh.type == AgentType.Asset:
                totalValue += neigh.value
        return totalValue

    def consciousInCell(agent):
        totalConscious = 0
        for neigh in agent.model.grid.get_cell_list_contents([agent.pos]):
            if neigh.type == AgentType.Human:
                totalConscious += 1 if neigh.isConscious else 0
        return totalConscious

    def unconsciousInCell(agent):
        totalUnconscious = 0
        for neigh in agent.model.grid.get_cell_list_contents([agent.pos]):
            if neigh.type == AgentType.Human:
                totalUnconscious += 0 if neigh.isConscious else 1
        return totalUnconscious

    match agent.type:
        case AgentType.Exit:
            portrayal = exitPortrayal
            return portrayal
        case AgentType.Asset:
            portrayal = assetPortrayal
            totalValue = valueInCell(agent)
            portrayal["text"] = str(totalValue)
            #portrayal["text"] = str(agent.unique_id)
            return portrayal
            
        case AgentType.Human:
            portrayal = humanPortrayal
            if agent.isConscious == False:
                portrayal["Color"] = "blue"
                portrayal["xAlign"] = 0.75
                portrayal["yAlign"] = 0.75
                portrayal["text"] = str(unconsciousInCell(agent))
                #portrayal["text"] = str(agent.unique_id)
            else:
                portrayal["text"] = str(consciousInCell(agent))
                #portrayal["text"] = str(agent.unique_id)
                
            return portrayal
        
        case AgentType.Robot:
            portrayal = robotPortrayal
            totalRobots = robotsInCell(agent)
            portrayal["text"] = str(totalRobots)
            #portrayal["text"] = str(agent.unique_id)
            return portrayal
        
        case _:
            return {}
