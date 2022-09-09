from ctypes import Array
import queue
import mesa
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from src.AssetAgent import *
from src.HumanAgent import *
from src.ExitField import *
from src.RobotAgent import *
from queue import Queue
        


class RescueModel(mesa.Model):
    def __init__(self, T: int, m: int, n: int, R: int, A: int, P: int,
                 assets: Array,
                 people: Array,
                 exitFields: Array,
                 returnQueue: Queue=None) -> None:
        self.current_id = 0
        self.timeLimit = T
        self.assets = set()
        self.exitFields = set()
        self.returnQueue = returnQueue
        self.humans = set()
        self.robots = set()
        self.rescued = set()
        self.retrieved = set()
        self.marked = set()
        self.met = set()
        self.grid = MultiGrid(m, n, False)
        self.schedule = SimultaneousActivation(self)
        self.rescuedConscious = 0
        self.rescuedUnconscious = 0
        self.assetValue = 0
        self.datacollector = DataCollector(
            model_reporters={
                "rescuedConscious": "rescuedConscious",
                "rescuedUnconscious": "rescuedUnconscious",
                "assetValue": "assetValue"},
            tables={"Saved": ["time", "id", "posX", "posY"]}
        )
        for human in people:
            humanAgent = generateHuman(self.next_id(), human["isConscious"], self)
            self.schedule.add(humanAgent)
            self.humans.add(humanAgent)
            self.grid.place_agent(humanAgent, human["pos"])

        for asset in assets:
            assetAgent = AssetAgent(self.next_id(), asset["weight"], asset["value"], self)
            self.schedule.add(assetAgent)
            self.assets.add(assetAgent)
            self.grid.place_agent(assetAgent, asset["pos"])
        
        for exitField in exitFields:
            exitAgent = ExitField(self.next_id(), self)
            self.schedule.add(exitAgent)
            self.exitFields.add(exitAgent)
            self.grid.place_agent(exitAgent, exitField["pos"])
        
        for _ in range(R):
            robotAgent = DirectRobot(self.next_id(), self)
            self.schedule.add(robotAgent)
            self.robots.add(robotAgent)
            #Robot sam wybiera, gdzie startuje symulację
        self.marked = set()
        
        self.running = True
    
    def meet(self, human:HumanAgent):
        self.met.add(human)
    
    def unmeet(self, human:HumanAgent):
        self.met.discard(human)

    #isMet - czy dany człowiek jest już eskortowany
    def isMet(self, human:HumanAgent):
        return human in self.met

    def mark(self, human:HumanAgent):
        self.marked.add(human)
    
    def unmark(self, human:HumanAgent):
        self.marked.discard(human)

    #isMarked - czy dany człowiek jest oznaczony do uratowania
    def isMarked(self, human:HumanAgent):
        return human in self.marked
    
    def timeLeft(self):
        return self.timeLimit - self.schedule.time

    #Po każdej turze model usuwa każdego uratowanego człowieka
    #i odnotowuje ratunek w logach
    def noteRescues(self):
        for rescue in self.rescued:
            (x, y) = rescue.pos
            self.schedule.remove(rescue)
            self.grid.remove_agent(rescue)
            if rescue.isConscious:
                self.rescuedConscious += 1
            else:
                self.rescuedUnconscious += 1
            self.met.discard(rescue)
            self.marked.discard(rescue)
            self.humans.discard(rescue)
            self.datacollector.add_table_row("Saved", 
                                             {"time": self.schedule.time,
                                              "id": rescue.unique_id,
                                              "posX": x,
                                              "posY": y})
        self.rescued = set()
    
    #Po każdej turze model usuwa każdy wyniesiony obiekt
    #i odnotowuje wyniesienie w logach
    def noteRetrievals(self):
        for retrieval in self.retrieved:
            self.schedule.remove(retrieval)
            self.grid.remove_agent(retrieval)
            self.assetValue += retrieval.value
        self.retrieved = set()
    
    def rescue(self, agent):
        self.rescued.add(agent)
    
    def retrieve(self, agent):
        self.retrieved.add(agent)
    
    #implementacja step() obsługuje również funkcjonalność
    #run_model() kończenia symulacji po spełnieniu warunku
    #ze względu na (według mnie) wadliwą implementację
    #modułu wizualizatora Mesy, który przeprowadza symulację
    #samodzielnie wywołując funkcję step() modelu, ignorując
    #funkcję run_model(), czyli (według specyfikacji) również
    #wartość atrybutu model.running, którego używa do określenia
    #czy należy zakończyć wizualizację

    #W przypadku przekazania do modelu kolejki do komunikacji między
    #wątkami jest ona używana do przekazania logów do wątku zbierającego;
    #Funkcjonalność na potrzeby przeprowadzenia pełnoprawnej symulacji
    #przy użyciu wizualizatora
    
    def step(self):
        if not self.running:
            return
        self.schedule.step()
        self.noteRescues()
        self.noteRetrievals()
        self.datacollector.collect(self)
        if self.timeLeft() <= 0 or len(self.humans) == 0:
            self.running = False
            if self.returnQueue == None:
                return
            modelDF = self.datacollector.get_model_vars_dataframe()
            tableDF = self.datacollector.get_table_dataframe("Saved")
            self.returnQueue.put((modelDF, tableDF))
    
    def run_model(self) -> None:
        for _ in range(self.timeLimit):
            self.step()
            if len(self.humans) == 0:
                self.running = False
                break
