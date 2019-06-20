from card import card
from buff import buff
from ability import ability
from action import action
from scheduler import scheduler
import simdictionary
import random
import copy
import logging


class astmodule:

    def __init__(self, number, priority, fight, log):

        logging.basicConfig(filename='AST_Sim_Log' + str(number), filemode='w', format='%(message)s',level=logging.INFO)
        self.priority = priority
        self.fight = fight
        self.fightpos = 0
        self.delaystart = self.fight[self.fightpos][0]
        self.delayend = self.fight[self.fightpos][1]
        self.delaybuffs = self.fight[self.fightpos][2]
        self.createlog = log
        build = simdictionary.genast()
        self.abilities = copy.deepcopy(build[0])
        self.buffs = copy.deepcopy(build[1])
        self.deck = copy.deepcopy(build[2])
        self.Lunar = False
        self.Solar = False
        self.Celestial = False
        self.seals = []
        self.abilitydelay = .7
        self.gcd = 2.4
        self.clock = 0
        self.nextgcd = 0
        self.nextaction = 0
        self.posinopen = 0


        self.buildasttable()
        self.buildschedule()
        self.inopener = True

        self.draw()
        self.inplay = True
        self.minor = False
        self.stacks = 0

        self.dummy = card('Fake','Fake',False)


    def buildasttable(self):
        opener = ['Hold .7', 'GCD', 'Play', 'oGCD', 'GCD', 'Draw', 'Sleeve Draw', 'GCD', 'Play', 'Draw', 'Redraw',
                  'GCD', 'Redraw', 'Redraw', 'Play', 'GCD', 'Divination']

        actiontable = []
        astrecast = self.gcd
        for i in opener:
            self.clock = round(self.clock, 2)
            if i.split()[0] == 'Hold':
                actiontable.append(action(19, 'Hold', self.clock))
                self.clock = self.clock + float(i.split()[1])
            elif i.split()[0] == 'GCD':
                if self.nextgcd > self.clock:
                    self.clock = round(self.nextgcd, 2)
                if self.nextaction > self.clock:
                    self.clock = round(self.nextaction, 2)
                actiontable.append(action(100, 'GCD', self.clock))
                self.nextgcd = round(self.clock + astrecast, 2)
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Play':
                actiontable.append(action(100, 'Play', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'oGCD':
                actiontable.append(action(100, 'oGCD', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Draw':
                actiontable.append(action(100, 'Draw', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Sleeve':
                actiontable.append(action(100, 'Sleeve Draw', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Redraw':
                actiontable.append(action(100, 'Redraw', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Divination':
                actiontable.append(action(100, 'Divination', self.clock))
                self.nextaction = round(self.clock + self.abilitydelay, 2)
                self.clock = round(self.clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Minor':
                actiontable.append(action(100, 'Minor Arcana', self.clock))

        self.action = actiontable
        self.nextaction = 0
        self.next = 0
        self.clock = 0

    def buildschedule(self):
        sets = set()
        sets.add(0)
        for i in self.action:
            sets.add(i.actiontime)

        self.schedule = scheduler(sets)

    def draw(self):
        x = random.randrange(0, 6)
        self.card = self.deck[x]
        if self.createlog:
            logging.info(str(self.clock)+' : AST : Drew a '+self.card.name)

    def redraw(self):
        oldname = self.card.name
        while(self.card.name == oldname):
            x = random.randrange(0, 6)
            self.card = self.deck[x]
        if self.createlog:
            logging.info(str(self.clock)+' : AST : Redrew '+self.card.name)

    def allseals(self):
        return self.Lunar and self.Solar and self.Celestial

    def resetseals(self):
        self.Lunar = False
        self.Solar = False
        self.Celestial = False
        self.seals = []

    def checkseal(self):
        if self.card.seal == 'Lunar':
            return self.Lunar
        elif self.card.seal =='Solar':
            return self.Solar
        else:
            return self.Celestial
    
    def buildseal(self):
        if self.card.seal == 'Lunar':
            self.Lunar = True
        elif self.card.seal == 'Solar':
            self.Solar = True
        else:
            self.Celestial = True
        self.seals.append(self.card.seal)

    def countseal(self):
        return len(self.seals)

    def sim(self,time):
        
        key = "None"
        self.clock = time

        if self.clock == self.delaystart:
            self.nextgcd = round(self.delayend, 2)
            self.nextaction = round(self.delayend, 2)
            if self.createlog:
                logging.info(str(self.clock) + ': AST : Boss has jumped')
            self.inopener = False  # To avoid complications)

        elif self.clock == self.delayend:
            if self.createlog:
                logging.info(str(self.clock) + ': AST : Boss has Returned')
            self.fightpos = self.fightpos + 1
            if self.fightpos < len(self.fight):
                self.delaystart = round(self.fight[self.fightpos][0], 2)
                self.delayend = round(self.fight[self.fightposs][1], 2)
                self.delaybuffs = self.fight[self.fightpos][2]
                self.schedule.addtime(self.delaystart)
                self.schedule.addtime(self.delayend)
            else:
                delaystart = 1000000
                delayend = 10000001

        if self.inplay and self.card.name == 'Fake':
            self.inplay = False

        for i in self.buffs.values():
            if self.clock == i.activation:
                string = i.switchon(self.clock)
                self.schedule.addtime(i.endtime + .01)
                if self.createlog:
                    logging.info(string)
            elif i.available and not i.getactive(self.clock) and i.active:
                string = i.dropbuff(self.clock)
                if self.createlog:
                    logging.info(string)

        if self.inopener:
            if self.action[self.posinopen].actiontime == self.clock:
                currentaction = self.action[self.posinopen]
                if currentaction.name == 'Play':
                    if not self.card.name == 'Fake':
                        if self.card.buff:
                            if not self.priority and not self.buffs['Not My Card'].getactive(self.clock):
                                    self.buffs['Not My Card'].activate(self.clock)
                                    self.schedule.addtime(self.buffs['Not My Card'].activation)
                                    if self.createlog:
                                        logging.info(str(self.clock) + ' : AST : Played Card on another Ranged Member')
                            elif not self.buffs['Bole'].getactive(self.clock):
                                self.buffs['Bole'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Bole'].activation)
                                key = 'Bole'
                                if self.createlog:
                                    logging.info(str(self.clock) + ' : AST : Played 6% Card on you')
                            else:
                                self.buffs['Not My Card'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Not My Card'].activation)
                                if self.createlog:
                                    logging.info(str(self.clock) + ' : AST : Played Card on another Ranged Member')
                        else:
                            if self.createlog:
                                logging.info(str(self.clock)+' : AST : Played Card on another Member')
                        self.buildseal()
                        self.card = self.dummy
                        self.posinopen = self.posinopen + 1
                        self.nextaction = round(self.clock + .7, 2)
                        self.inplay = False
                elif currentaction.name == 'Draw':
                    self.draw()
                    self.abilities['Draw'].putonCD(self.clock)
                    self.posinopen = self.posinopen + 1
                    self.nextaction = round(self.clock + .7, 2)
                    if self.buffs['Sleeve Draw'].getactive(self.clock):
                        self.stacks = self.stacks - 1
                    self.inplay = True
                elif currentaction.name == 'Sleeve Draw':
                    self.buffs['Sleeve Draw'].activate(self.clock)
                    self.schedule.addtime(self.buffs['Sleeve Draw'].activation)
                    self.stacks = 2
                    self.abilities['Sleeve Draw'].putonCD(self.clock)
                    self.abilities['Draw'].setCD(3)
                    self.abilities['Draw'].nextuse = round(self.clock, 2)
                    self.posinopen = self.posinopen + 1
                    self.nextaction = round(self.clock + .7, 2)
                    if self.createlog:
                        logging.info(str(self.clock)+ ': AST : Used Sleeve Draw')
                elif currentaction.name == 'Divination':
                    self.buffs['Divination'].specialactivate(self.clock, self.allseals())
                    self.schedule.addtime(self.buffs['Divination'].activation)
                    self.abilities['Divination'].putonCD(self.clock)
                    if self.allseals():
                        key = 'Divination 6'
                    else:
                        key = 'Divination 3'
                    if self.createlog:
                        if self.allseals():
                            logging.info(str(self.clock)+' : AST : 6% Divination')
                        else:
                            logging.info(str(self.clock) + ' : AST : 3% Divination')
                    self.resetseals()
                    self.posinopen = self.posinopen + 1
                    self.nextaction = round(self.clock + .7, 2)

                elif currentaction.name == 'Redraw':
                    if self.checkseal():
                        self.redraw()
                        self.abilities['Redraw'].putonCD(self.clock)
                        if self.createlog:
                            logging.info(str(self.clock) + ' : AST : Used Redraw')
                    self.posinopen = self.posinopen + 1
                    self.nextaction = round(self.clock + .7, 2)
                elif currentaction.name == 'GCD':
                    self.nextaction = round(self.clock + .7, 2)
                    self.nextgcd = round(self.clock + .7, 2)
                    self.posinopen = self.posinopen + 1
                elif currentaction.name == 'oGCD':
                    self.posinopen = self.posinopen + 1
                    self.nextaction = round(self.clock + .7, 2)
                elif currentaction.name == 'Hold':
                    self.posinopen = self.posinopen + 1
            if self.posinopen >= len(self.action):
                self.inopener = False
                self.nextaction = self.action[self.posinopen-1].actiontime
                self.nexgcd = self.action[self.posinopen - 1].actiontime
                if self.nextaction > self.nextgcd:
                    self.nextgcd = round(self.nextaction, 2)

                if self.nextaction + .7 > self.nextgcd:
                    self.nextaction = round(self.nextgcd, 2)

        else:
            if self.buffs['Sleeve Draw'].getactive(self.clock) and self.stacks == 0:
                self.buffs['Sleeve Draw'].dropbuff(self.clock)
                self.abilities['Draw'].setCD(30)
            elif not self.buffs['Sleeve Draw'].getactive(self.clock) and self.stacks > 0:
                self.abilities['Draw'].setCD(30)
                self.stacks = 0
            elif self.buffs['Sleeve Draw'].getactive(self.clock):
                self.abilities['Draw'].setCD(3)


            if self.clock == self.nextgcd:
                self.nextgcd = round(self.clock + self.gcd, 2)
                self.nextaction = round(self.clock + .7, 2)
            elif self.nextaction == self.clock:
                if self.abilities['Sleeve Draw'].available(self.clock) and not self.abilities['Draw'].available(self.clock) and self.countseal() < 2 and self.delaystart - self.clock > 20:
                    self.abilities['Sleeve Draw'].putonCD(self.clock)
                    self.buffs['Sleeve Draw'].activate(self.clock)
                    self.schedule.addtime(self.buffs['Sleeve Draw'].activation)
                    self.stacks = 2
                    self.abilities['Draw'].nextuse = self.clock
                    self.nextaction = round(self.clock + .7, 2)
                    if self.createlog:
                        logging.info(str(self.clock)+' : AST : Used Sleeve Draw')
                elif self.abilities['Sleeve Draw'].available(self.clock) and not self.abilities['Draw'].available(self.clock) and self.abilities['Divination'].getrecast(self.clock) < 5 and self.delaystart - self.clock > 20:
                    self.abilities['Sleeve Draw'].putonCD(self.clock)
                    self.buffs['Sleeve Draw'].activate(self.clock)
                    self.schedule.addtime(self.buffs['Sleeve Draw'].activation)
                    self.stacks = 2
                    self.abilities['Draw'].nextuse = self.clock
                    self.nextaction = round(self.clock + .7, 2)
                elif self.abilities['Divination'].available(self.clock) and self.countseal() > 2 and self.delaystart - self.clock > 20:
                    self.buffs['Divination'].specialactivate(self.clock, self.allseals())
                    self.abilities['Divination'].putonCD(self.clock)
                    if self.createlog:
                        if self.allseals():
                            logging.info(str(self.clock)+' : AST : 6% Divination')
                        else:
                            logging.info(str(self.clock) + ' : AST : 3% Divination')
                    self.resetseals()
                    self.nextaction = round(self.clock + .7, 2)
                elif self.inplay and self.checkseal() and self.abilities['Redraw'].available(self.clock):
                    if self.createlog:
                        logging.info(str(self.clock)+ " : AST : Used Redraw")
                    self.redraw()
                    self.abilities['Redraw'].putonCD(self.clock)
                    self.nextaction = round(self.clock + .7, 2)
                elif not self.inplay and self.abilities['Draw'].available(self.clock):
                    self.draw()
                    if self.buffs['Sleeve Draw'].getactive:
                        self.stacks = self.stacks - 1
                    self.nextaction = round(self.clock + .7, 2)
                    self.abilities['Draw'].putonCD(self.clock)
                    self.inplay = True
                elif self.inplay and not self.priority and self.abilities['Divination'].getrecast(self.clock) < 20 and not self.allseals():
                    if self.card.buff:
                        if not self.buffs['Not My Card'].getactive(self.clock) or self.buffs['Bole'].getactive(self.clock) or self.buffs['Lady'].getactive(self.clock):
                            self.buffs['Not My Card'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Not My Card'].activation)
                            if self.createlog:
                                logging.info(str(self.clock)+' : AST : Played a card on another member')
                        else:
                            if not self.minor:
                                self.buffs['Bole'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Bole'].activation)
                                if self.createlog:
                                    logging.info(str(self.clock) + ' : AST : Played a 6% Card on you')
                                key = 'Bole'
                            else:
                                self.buffs['Lady'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Lady'].activation)
                                if self.createlog:
                                    logging.info(str(self.clock) + ' : AST : Played a 8% Card on you')
                                key = 'Lady'
                        if not self.minor:
                            self.buildseal()
                        self.minor = False
                    elif not self.card == 'Fake':
                        self.buildseal()
                        self.card = self.dummy
                    self.inplay = False
                elif self.inplay and not (self.checkseal() or self.minor) and not self.card.buff:
                    self.inplay = False
                    self.buildseal()
                    if self.createlog:
                        logging.info(str(self.clock)+' : AST : Played Card on a melee')
                    self.card = self.dummy
                    self.minor = False
                elif self.inplay and not self.minor and (not self.abilities['Redraw'].available(self.clock) or self.allseals()):
                    self.minor = True
                    if self.createlog:
                        logging.info(str(self.clock)+' : AST : Use Minor Arcana')
                    self.nextaction = round(self.clock + .7, 2)
                elif self.inplay and not self.priority and not self.buffs['Not My Card'].getactive(self.clock):
                    if not self.minor:
                        if not self.buffs['Not My Card'].getactive(self.clock) and self.card.buff:
                            self.buffs['Not My Card'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Not My Card'].activation)
                        self.inplay = False
                        self.buildseal()
                    elif self.minor:
                        if not self.buffs['Not My Card'].getactive(self.clock) and self.card.buff:
                            self.buffs['Not My Card'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Not My Card'].activation)
                        self.inplay = False
                        self.minor = False
                    if self.createlog:
                        logging.info(str(self.clock)+' : AST : Played card on other member')
                    self.nextaction = round(self.clock + .7, 2)
                elif self.inplay and self.priority and (not (self.buffs['Bole'].getactive(self.clock) or self.buffs['Lady'].getactive(self.clock)) or self.buffs['Sleeve Draw'].getactive(self.clock)):
                    if not self.minor:
                        if (not self.buffs['Bole'].getactive(self.clock) or not self.buffs['Lady'].getactive(self.clock)) and self.card.buff:
                            self.buffs['Bole'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Bole'].activation)
                            key = 'Bole'
                        self.inplay = False
                        self.buildseal()
                        if self.createlog:
                            logging.info(str(self.clock)+' : AST : Played 6% Card on you')
                    elif self.minor:
                        if (not self.buffs['Bole'].getactive(self.clock) or not self.buffs['Lady'].getactive(self.clock)) and self.card.buff:
                            self.buffs['Lady'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Lady'].activation)
                            key = 'Lady'
                        self.inplay = False
                        self.minor = False
                        if self.createlog:
                            logging.info(str(self.clock)+' : AST : Played 8% Card on you')
                    self.nextaction = round(self.clock + .7, 2)
                else:
                    self.nextaction = round(self.nextgcd, 2)

            if self.nextaction > self.nextgcd:
                self.nextgcd = round(self.nextaction, 2)

            if self.nextaction + .7 > self.nextgcd:
                self.nextaction = round(self.nextgcd, 2)
            
            if not self.inopener:
                self.schedule.addtime(self.nextaction)
                self.schedule.addtime(self.nextgcd)
            
        return [self.schedule.nexttime(), key]








