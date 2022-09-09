from enum import Enum, auto
from functools import singledispatch
from math import floor, pi, sqrt
from mesa import Agent
import numpy as np
import os
from pathlib import Path

#------------MODEL UTILITIES--------------#

class AgentType(Enum):
    Robot = auto()
    Human = auto()
    Asset = auto()
    Exit = auto()

#------------SPATIAL MATHS--------------#


def distSquared(a: Agent, b: Agent):
    (xa, ya) = a.pos
    (xb, yb) = b.pos
    return (xa - xb)**2 + (ya - yb)**2


def unitVector(vector):
    return vector / np.linalg.norm(vector)


def angleBetween(v1, v2):
    v1_u = unitVector(v1)
    v2_u = unitVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def minDistDir(s, t):
    dirMap = [(1, 0),
              (1, 1),
              (0, 1),
              (-1, 1),
              (-1, 0),
              (-1, -1),
              (0, -1),
              (1, -1)]
    (sx, sy) = s
    (tx, ty) = t
    if sx == tx and sy == ty:
        return (0, 0)
    angle = angleBetween((tx - sx, ty - sy), (1, 0))
    if ty < sy:
        angle = 2.0 * pi - angle
    #print("Calculated direction angle " + str(angle / pi * 180.0))
    dirIndex = floor((angle + pi/8.0)/(pi/4.0)) % 8
    (x, y) = dirMap[dirIndex]
    return dirMap[dirIndex]


#---------------------INPUT PARSING-----------------#

def parseAssets(assetStrList: list(str())):
    assetList = []
    for assetDesc in assetStrList:
        [posX, posY, value, weight] = assetDesc.split(" ")
        asset = {
            "weight" : int(weight),
            "value": int(value),
            "pos": (int(posX), int(posY)) 
        }
        assetList.append(asset)
    
    return assetList

def parsePeople(peopleStrList: list(str())):
    peopleList = []
    for personDesc in peopleStrList:
        [posX, posY, isConscious] = personDesc.split(" ")
        person = {
            "pos": (int(posX), int(posY)),
            "isConscious": bool(isConscious)
        }
        peopleList.append(person)
    
    return peopleList

def parseExits(exitStrList: list(str())):
    exitList = []
    for exitDesc in exitStrList:
        [posX, posY] = exitDesc.split(" ")
        exit = {
            "pos": (int(posX), int(posY))
        }
        exitList.append(exit)
    
    return exitList

def parseInput(path):
    if not os.path.isfile(path):
        raise FileNotFoundError()

    inputFile = open(path, "r")
    inputStr = inputFile.read()
    inputFile.close()

    inputLines = inputStr.split("\n")
    modelInput = inputLines[0]
    [timeLimit, width, height, noRobots, noAssets, noPeople, noExits] = modelInput.split(" ")
    model = {
        "timeLimit": int(timeLimit),
        "width": int(width),
        "height": int(height),
        "robotCount": int(noRobots),
        "assetCount": int(noAssets),
        "peopleCount": int(noPeople),
        "exitCount": int(noExits)
    }
    index = 1
    assets = parseAssets(inputLines[index : index + model["assetCount"]])
    index += model["assetCount"]
    people = parsePeople(inputLines[index : index + model["peopleCount"]])
    index += model["peopleCount"]
    exits = parseExits(inputLines[index : index + model["exitCount"]])
    

    return model, assets, people, exits

#------------------OUTPUT MANAGEMENT--------------#
def ensureResultLocation(path):
    if os.path.exists(path):
        return
    os.makedirs(str(Path(path).resolve()))