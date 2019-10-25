import math
import random

#Need to define charged, charges and maxCD for charges abilities
class ability:

    def __init__(self, name, abiltype, targtype, cooldown, potency, nextuse, combopotency):
        self.name = name
        self.abiltype = abiltype
        self.targtype = targtype
        self.cooldown = cooldown
        self.potency = potency
        self.nextuse = nextuse
        self.combopotency = combopotency
        self.charged = False
        self.charges = 0
        self.maxcooldown = self.charges * self.cooldown
        self.partymod = True
        self.simcrits = True
        self.totalpotency = 0
        self.totaluse = 0

    #Calculated damage and creates log if needed
    def getpotency(self, time, cdhstats, potmod, stats, combo):
        Auto = False
        if self.name == 'Auto Attack':
            Auto = True

        pot = 0
        string = str(time) + ' : You use ' + str(self.name)
        if combo and self.combopotency > 0:
            pot = int(self.combopotency)
        else:
            pot = int(self.potency)

        pot = self.returndamage(pot, Auto, stats)


        for i in potmod:
            pot = math.floor(pot*i)

        if self.simcrits:
            if (random.randint(1, 10001) > ((10000 * (100 - cdhstats[0]))/100)): #Check Crit
                pot = pot * cdhstats[1]
                string = string + '!'
            if (random.randint(1, 10001) > ((10000 * (100 - cdhstats[2]))/100)): #Check DH
                pot = pot * cdhstats[3]
                string = string + '@'


        pot = round(pot,4)
        string = string+' - '+str(pot)+ ' damage'
        self.putonCD(time)
        self.totalpotency = self.totalpotency + pot
        self.totaluse = self.totaluse + 1
        return [pot, string]

    def returncharges(self,time):
        if not self.charged:
            print('Incorrect Charged Ability')
            return 0
        else:
            return math.trunc(self.charges - (self.nextuse - time) / self.cooldown)

    #puts ability on CD
    def putonCD(self,time):
        if not self.charged:
            self.nextuse = round(time + self.cooldown, 2)
        else:
            if self.nextuse - time < 0:
                self.nextuse = time + self.cooldown
            else:
                self.nextuse = self.nextuse + self.cooldown

    #Checks if ability is vailable
    def available(self,time):
        if not self.charged:
            return time >= self.nextuse
        else:
            return math.trunc(self.charges - (self.nextuse - time) / self.cooldown) > 0

    #check the recast time
    def getrecast(self,time):
        if time >= self.nextuse:
            return 0
        else:
            return self.nextuse - time

    #put ability on CD
    def setCD(self, newCD):
        self.cooldown = newCD

    # reset values
    def reset(self):
        self.nextuse = 0

    def returndamage(self, pot, auto, stats):
        JobMod = 115
        WD = stats[0]
        wepdelay = stats[1]
        dex = stats[2]
        det = stats[3]
        ss = stats[4]
        if self.partymod:
            dexstat = math.floor(dex * 1.05)
        else:
            dexstat = dex
        Damage = 0
        if auto:
            Damage = math.floor(pot * ((WD + math.floor(340 * JobMod / 1000)) * (wepdelay / 3)) * (100 + math.floor((dexstat - 340) * 165 / 340)) / 100)
            Damage = math.floor(Damage * (1000 + math.floor(130 * (det - 340) / 3300)) / 1000)
            Damage = math.floor(Damage * (1000 + math.floor(130 * (ss - 380) / 3300)) / 1000)
            Damage = math.floor(Damage * (1000 + math.floor(100 * (380 - 380) / 3300)) / 1000 / 100)
        else:
            Damage = math.floor(pot * (WD + math.floor(340 * JobMod / 1000)) * (100 + math.floor((dexstat - 340) * 165 / 340)) / 100)
            Damage = math.floor(Damage * (1000 + math.floor(130 * (det - 340) / 3300)) / 1000)
            Damage = math.floor(Damage * (1000 + math.floor(100 * (380 - 380) / 3300)) / 1000 / 100)

        return Damage * (random.randrange(95, 105) / 100)

    def apexpotency(self,time,cdhstats,potmod,stats,combo,sv):
        self.potency = math.floor(sv*6)
        return self.getpotency(time, cdhstats, potmod, stats, combo)

    def pitchpotency(self,time,cdhstats,potmod,stats,combo,rep):
        if rep == 3:
            self.potency = 450
        elif rep == 2:
            self.potency = 240
        else:
            self.potency = 100
        return self.getpotency(time,cdhstats,potmod,stats,combo)

    def resetcd(self,time):
        if not self.charged:
            self.nextuse = time
        else:
            if self.nextuse - self.cooldown < time:
                self.nextuse = time
            else:
                self.nextuse = self.nextuse - self.cooldown