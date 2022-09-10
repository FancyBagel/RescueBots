import mesa

from src.Utility import *


class ExitField(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.type = AgentType.Exit

    def getType(self):
        return self.type
    
    def getGuide(self):
        return None

    def step(self):
        pass

    def advance(self):
        pass
