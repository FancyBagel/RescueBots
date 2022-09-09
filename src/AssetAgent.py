import mesa
import mesa.model
from src.Utility import *


class AssetAgent(mesa.Agent):
    def __init__(self, unique_id: int, weight: int, value: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.weight = weight
        self.value = value
        self.owner = None
        self.nextPos = None
        self.type = AgentType.Asset

    def getType(self):
        return self.type

    def setOwner(self, agent):
        self.owner = agent

    def setForRetrieval(self):
        self.owner = None
        self.model.retrieve()

    def step(self):
        pass

    def advance(self) -> None:
        if self.owner == None:
            return
        self.model.grid.move_agent(self, self.owner.nextPos)
