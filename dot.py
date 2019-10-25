import math
import random
import copy

class dot:

    def __init__(self,name,potency,duration):

        self.name = name
        self.potency = potency
        self.duration = duration
        self.endtime = 0
        self.potmod = [1]
        self.cdhstats =[]
        self.stats = []
        self.simcrits = True
        self.partymod = True
        self.activation = -1
        self.activationdelay = .7
        self.active = False
        self.ready = False
        self.totalpotency = 0
        self.totaluse = 0


    def getpotency(self,clock):
        string = str(clock) + ' : ' + str(self.name) + ' Ticks for: '

        pot = int(self.potency)

        pot = self.returndamage(pot)

        for i in self.potmod:
            pot = math.floor(pot * i)

        if self.simcrits:
            if (random.randint(1, 10001) > ((10000 * (100 - self.cdhstats[0])) / 100)):  # Check Crit
                pot = pot * self.cdhstats[1]
                string = string + '!'
            if (random.randint(1, 10001) > ((10000 * (100 - self.cdhstats[2])) / 100)):  # Check DH
                pot = pot * self.cdhstats[3]
                string = string + '@'

        pot = round(pot, 4)
        string = string + ' - ' + str(pot) + ' damage'
        self.totalpotency = self.totalpotency + pot
        self.totaluse = self.totaluse + 1
        return [pot, string]

    def returndamage(self, pot):
        JobMod = 115
        WD = self.stats[0]
        wepdelay = self.stats[1]
        dex = self.stats[2]
        det = self.stats[3]
        ss = self.stats[4]
        if self.partymod:
            dexstat = math.floor(dex * 1.05)
        else:
            dexstat = dex

        Damage = math.floor(pot * ((WD + math.floor(340 * JobMod / 1000)) * (100 + math.floor((dexstat - 340) * 165 / 340)) / 100))
        Damage = math.floor(Damage * (1000 + math.floor(130 * (det - 340) / 3300)) / 1000)
        Damage = math.floor(Damage * (1000 + math.floor(130 * (ss - 380) / 3300)) / 1000)
        Damage = math.floor(Damage * (1000 + math.floor(100 * (380 - 380) / 3300)) / 1000 / 100)

        return Damage * (random.randrange(95, 105) / 100)

    def activate(self,clock,cdhstats,potmod,stats):
        self.ready = True
        self.activation = round(clock + self.activationdelay,2)
        self.cdhstats = copy.deepcopy(cdhstats)
        self.potmod = potmod
        self.stats = copy.deepcopy(stats)

    def switchon(self,clock):
        self.active = True
        self.ready = False
        self.endtime = round(clock + self.duration,2)
        return str(clock)+ ' : Mob gains the effect of '+self.name

    def getactive(self,clock):
        return (clock <= self.endtime and self.active)

    def closetodrop(self,clock,gcd):
        return clock + gcd >= self.endtime

    def dropoff(self,clock):
        self.active = False
        return str(clock)+ ': '+self.name+' Falls off'




dex = 3916
det = 2753
ss = 1412
pot = 1200
WD = 117
JobMod = 115
wepdelay = 3.02
dexstat = dex



Damage = math.floor(pot * ((WD + math.floor(340 * JobMod / 1000)) * (wepdelay / 3)) * (100 + math.floor((dexstat - 340) * 165 / 340)) / 100)
Damage = math.floor(Damage * (1000 + math.floor(130 * (det - 340) / 3300)) / 1000)
Damage = math.floor(Damage * (1000 + math.floor(130 * (ss - 380) / 3300)) / 1000)
Damage = math.floor(Damage * (1000 + math.floor(100 * (380 - 380) / 3300)) / 1000 / 100)
Damage = Damage *1.2


print("Upper Range: "+ str(Damage*1.05))
print("Average Damage:"+str(Damage))
print("Lower Range: "+ str(Damage*.95))



