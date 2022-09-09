import mesa
from src.Utility import *

#nadklasa człowieka, implementacje metod podstawowych czynności,
#niezależnych od zachowań
class HumanAgent(mesa.Agent):
    def __init__(self, unique_id: int, isConscious: bool, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.isConscious = isConscious
        self.type = AgentType.Human
        self.exiting = False
        self.guide = None
        self.payload = None

    def getType(self):
        return self.type

    def step(self):
        raise NotImplementedError

    def advance(self):
        raise NotImplementedError

    def joinGuide(self, guide: mesa.Agent):
        if self.guide == None:
            self.model.meet(self)
            self.model.unmark(self)
            self.guide = guide


    def getGuide(self):
        return self.guide

    def setForRescue(self):
        self.guide = None
        self.model.rescue(self)
        self.exiting = True

    def noteExit(self):
        self.setForRescue()

    def pickUp(self, thing: mesa.Agent):
        self.payload = thing

    def drop(self):
        self.payload = None

    def getPayload(self):
        return self.payload
    
    def randomMove(self):
        (x, y) = self.pos
        l = 0 if self.model.grid.out_of_bounds((x - 1, y)) else -1
        u = 0 if self.model.grid.out_of_bounds((x + 1, y)) else 1
        dx = self.model.random.randint(l, u)
        l = 0 if self.model.grid.out_of_bounds((x, y - 1)) else -1
        u = 0 if self.model.grid.out_of_bounds((x, y + 1)) else 1
        dy = self.model.random.randint(l, u)
        return (x + dx, y + dy)
        

#człowiek testowy, stojący w miejscu i dołączający się do pierwszego robota
#dzielącego z nim pole
class TestHuman(HumanAgent):
    def __init__(self, unique_id: int, isConscious: bool, model: mesa.Model) -> None:
        super().__init__(unique_id, isConscious, model)
        self.dir = 1

    def step(self):
        if not self.isConscious or self.getGuide() != None:
            return

        neighbors = self.model.grid.get_cell_list_contents([self.pos])
        for neigh in neighbors:
            if neigh.getType() == AgentType.Robot:
                self.joinGuide(neigh)
                break

            if neigh.getType() == AgentType.Exit:
                self.noteExit()
                break

    def advance(self):
        if not self.isConscious or self.getGuide() == None:
            return
        self.model.grid.move_agent(self, self.getGuide().nextPos)

#"Przeciętny" człowiek, porusza się losowo dopóki nie zobaczy robota
#albo wyjścia, wtedy idzie w ich stronę, chyba że jest częścią grupy prowadzonej
#przez robota - wtedy idzie za nim wszędzie dopóki nie staną na polu wyjściowym
class RegularHuman(HumanAgent):
    def __init__(self, unique_id: int, isConscious: bool, model: mesa.Model) -> None:
        super().__init__(unique_id, isConscious, model)
        self.targetPos = None

    def step(self):
        #print(self.unique_id)
        #print(self.pos)
        #Priorytety człowieka:
        #1. Jeśli jest na polu wyjściowym, wychodzi/jest ratowany
        #2. Jeśli jest nieprzytomny/częścią grupy, nie podejmuje własnych decyzji
        #3. Jeśli nie przynależy do grupy i dzieli pole z robotem, dołącza do niego
        #4. Jeśli jest sam i widzi pole wyjściowe, idzie w jego stronę
        #5. Jeśli jest sam i widzi robota, idzie w jego stronę
        #6. Chodzi losowo

        for neigh in self.model.grid.get_cell_list_contents([self.pos]):
            if neigh.getType() == AgentType.Exit:
                self.noteExit()
                break

        if self.exiting: #1
            return

        if not self.isConscious or self.getGuide() != None: #2
            return

        for neigh in self.model.grid.get_cell_list_contents([self.pos]):
            if neigh.getType() == AgentType.Robot:
                self.joinGuide(neigh)
                break

        if self.getGuide() != None: #3
            return

        visible = self.model.grid.get_neighbors(self.pos, True)

        for agent in visible:
            if agent.getType() == AgentType.Exit:
                self.targetPos = agent.pos
                break

        if self.targetPos != None: #4
            return 

        for agent in visible:
            if agent.getType() == AgentType.Robot:
                self.targetPos = agent.pos
        
        if self.targetPos != None: #5
            return
        
        self.targetPos = self.randomMove() #6


    def advance(self):
        #jeśli wychodzi/jest nieprzytomny - nigdzie nie idzie
        if self.exiting or not self.isConscious: 
            return
        
        #jeśli jest częścią grupy - idzie za przewodnikiem
        if self.getGuide() != None:
            self.model.grid.move_agent(self, self.getGuide().nextPos)
            return
        
        #jeśli ma własny cel - idzie za nim
        self.model.grid.move_agent(self, self.targetPos)
        self.targetPos = None
        
        
        


def generateHuman(i, isConscious, model):  # PLACEHOLDER
    return RegularHuman(i, isConscious, model)
