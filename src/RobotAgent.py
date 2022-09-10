from cmath import inf
import mesa
from src.Utility import *


# nadklasa robota, implementacje metod podstawowych czynności,
# niezależnych od zachowań
class RobotAgent(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.type = AgentType.Robot
        self.payload = None
        self.nextPos = None
        self.group = set()
        self.loot = set()
        self.isGroupBurdened = False

    def getType(self):
        return self.type

    def getNextPos(self):
        return self.nextPos

    def step(self):
        raise NotImplementedError

    def advance(self):
        self.model.grid.move_agent(self, self.nextPos)

    def appendGroup(self, human):
        self.group.add(human)
        if not human.isConscious:
            self.isGroupBurdened = True

    def appendLoot(self, asset):
        self.loot.add(asset)
        self.isGroupBurdened = True

    def dropLoot(self):
        for asset in self.loot:
            asset.setForRetrieval()
        self.loot = {}

    def depositUnconscious(self):
        for human in self.group():
            if not human.isConscious:
                human.setForRescue()
                self.group.discard(human)
            else:
                human.noteExit()
                if human.getGuide() == None:
                    self.group.discard(human)

    def pickUp(self, thing: mesa.Agent):
        self.payload = thing
        self.isGroupBurdened = True

    def drop(self):
        self.payload = None


# Robot testowy, chodzi zygzakiem po planszy
class TestRobot(RobotAgent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.dirX = 1
        self.dirY = 1

        x = self.model.random.randrange(self.model.grid.width)
        y = self.model.random.randrange(self.model.grid.height)
        self.model.grid.place_agent(self, (x, y))

    def step(self):
        (x, y) = self.pos
        if self.model.grid.out_of_bounds((x + self.dirX, y)):
            self.dirX *= -1

        if self.model.grid.out_of_bounds((x, y + self.dirY)):
            self.dirY *= -1
            x += self.dirX
            y -= self.dirY
        y += self.dirY
        self.nextPos = (x, y)


# "Bezpośredni" robot, idzie w strone najbliższego człowieka, który nie jest
# jeszcze oznaczony przez innego robota do uratowania. Jeśli brak ludzi
# nieoznaczonych do uratowania, idzie do najbliższego wyjścia.
# Ignoruje nieprzytomnych i przedmioty wartościowe.
# Startuje z pola najbliższego do jeszcze nie oznaczonego człowieka
class DirectRobot(RobotAgent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.pickedTarget = None
        self.waiting = False
        minDist = inf
        closestExit = None
        closestHuman = None

        for exit in self.model.exitFields:
            for human in self.model.humans:
                if self.model.isMarked(human) or not human.isConscious:
                    continue
                dist = distSquared(exit, human)
                if minDist > dist:
                    minDist = dist
                    closestExit = exit
                    closestHuman = human

        # Każdy człowiek ma robota idącego w jego stronę - startuje gdziekolwiek
        if closestHuman == None:
            closestExit = self.model.random.choice(self.model.exitFields)
        # Oznacza wybranego człowieka, startuje z najbliższego pola wyjściowego
        else:
            self.model.mark(closestHuman)
        self.model.grid.place_agent(self, closestExit.pos)

    #Jeśli robot nie ma wybranego celu lub jego cel ma już przewodnika,
    #szuka nowego celu. Spośród przytomnych, nieoznaczonych i nieeskortowanych ludzi
    #wybiera najbliższego. Jeśli takiego nie ma, wybiera najbliższe wyjście
    def pickTarget(self):
        if (self.pickedTarget != None and
            distSquared(self, self.pickedTarget) > 0 and
                self.pickedTarget.getGuide() == None):
            return
        self.model.unmark(self.pickedTarget)
        self.pickedTarget = None

        minDist = inf
        for human in self.model.humans:
            if (self.model.isMarked(human) or not human.isConscious or
                    self.model.isMet(human) or human.exiting):
                continue

            dist = distSquared(human, self)
            if minDist > dist:
                minDist = dist
                self.pickedTarget = human

        if self.pickedTarget != None:
            self.model.mark(self.pickedTarget)
            return

        for exit in self.model.exitFields:
            dist = distSquared(exit, self)
            if minDist > dist:
                minDist = dist
                self.pickedTarget = exit

    def step(self):
        self.pickTarget()  # Wybór celu

        # Jeśli na którymś z sąsiadujących pól jest nieeskortowany człowiek,
        # robot zatrzymuje się na jedną turę i daje człowiekowi szansę na
        # podejście
        for thing in self.model.grid.get_neighbors(self.pos, True):
            if (thing.getType() == AgentType.Human and
                    not self.model.isMet(thing)):
                self.waiting = 1
                break

        # Robot wyznacza kierunek, który najbardziej zbliża go do celu
        (dx, dy) = minDistDir(self.pos, self.pickedTarget.pos)
        (x, y) = self.pos
        # Jeśli nie czeka, robot planuje ruch na następną turę
        self.nextPos = (x + dx, y + dy) if not self.waiting else self.pos

        # Robot kończy czekanie od następnej tury
        self.waiting = 0

    def advance(self):
        super().advance()
        #self.model.unmark(self.pickedTarget)
        #self.pickedTarget = None

# "Naiwny" robot, w każdej turze od nowa wybiera najbliższego człowieka, który nie jest
# jeszcze oznaczony przez innego robota do uratowania. Jeśli brak ludzi
# nieoznaczonych do uratowania, idzie do najbliższego wyjścia.
# Ignoruje nieprzytomnych i przedmioty wartościowe.
# Startuje z pola najbliższego do jeszcze nie oznaczonego człowieka
class NaiveRobot(RobotAgent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.pickedTarget = None
        self.waiting = False
        minDist = inf
        closestExit = None
        closestHuman = None

        for exit in self.model.exitFields:
            for human in self.model.humans:
                if self.model.isMarked(human) or not human.isConscious:
                    continue
                dist = distSquared(exit, human)
                if minDist > dist:
                    minDist = dist
                    closestExit = exit
                    closestHuman = human

        # Każdy człowiek ma robota idącego w jego stronę - startuje gdziekolwiek
        if closestHuman == None:
            closestExit = self.model.random.choice(self.model.exitFields)
        # Oznacza wybranego człowieka, startuje z najbliższego pola wyjściowego
        else:
            self.model.mark(closestHuman)
        self.model.grid.place_agent(self, closestExit.pos)

    #Spośród przytomnych, nieoznaczonych i nieeskortowanych ludzi robot
    #wybiera najbliższego. Jeśli takiego nie ma, wybiera najbliższe wyjście
    def pickTarget(self):
        minDist = inf
        for human in self.model.humans:
            if (self.model.isMarked(human) or not human.isConscious or
                    self.model.isMet(human) or human.exiting):
                continue

            dist = distSquared(human, self)
            if minDist > dist:
                minDist = dist
                self.pickedTarget = human

        if self.pickedTarget != None:
            self.model.mark(self.pickedTarget)
            return

        for exit in self.model.exitFields:
            dist = distSquared(exit, self)
            if minDist > dist:
                minDist = dist
                self.pickedTarget = exit

    def step(self):
        self.pickTarget()  # Wybór celu

        # Jeśli na którymś z sąsiadujących pól jest nieeskortowany człowiek,
        # robot zatrzymuje się na jedną turę i daje człowiekowi szansę na
        # podejście
        for thing in self.model.grid.get_neighbors(self.pos, True):
            if (thing.getType() == AgentType.Human and
                    not self.model.isMet(thing)):
                self.waiting = 1
                break

        # Robot wyznacza kierunek, który najbardziej zbliża go do celu
        (dx, dy) = minDistDir(self.pos, self.pickedTarget.pos)
        (x, y) = self.pos
        # Jeśli nie czeka, robot planuje ruch na następną turę
        self.nextPos = (x + dx, y + dy) if not self.waiting else self.pos

        # Robot kończy czekanie od następnej tury
        self.waiting = 0

    def advance(self):
        super().advance()
        self.model.unmark(self.pickedTarget)
        self.pickedTarget = None

#Typ do zaimplementowania: CompetentRobot
#Dopóki są przytomni ludzie, robot działa jak DirectRobot, ale zawsze
#pilnuje czasu i najbliższego wyjścia - jeśli pozostały czas jest równy
#czasowi dojścia, robot ignoruje wszystko i idzie do wyjścia.
#Jeśli wszyscy ludzie są oznaczeni/eskortowani, robot szuka najbliższego
#nieprzytomnego człowieka, a jeśli nie ma żadnego - najbliższego przedmiotu
#(albo o najmniejszej odległości podzielonej przez czynnik zależny od wartości)
#o wadze umożliwiającej podniesienie przez grupę.
#Cały czas pilnuje czasu i odległości do wyjścia - po podniesieniu czegoś
#przemnożonej przez 2