from buff import buff
from ability import ability
from action import action
from scheduler import scheduler
from astmodule import astmodule
from job import job
from card import card
from dot import dot
import logging
import random
import math
import asyncio
import copy

class sim:
        #stat table build out = WD,Wepdelay,Dex,Critrate,Critdamage,Directrate,Det,skillspeed,gcd
                    #int,     int,  table, table, table,   dict,   dict,    dict, dict   bool, bool,   bool
    def __init__(self,number,length, open, fight, stats, abilities, party, pbuffs, buffs,dots, potion, astpriority, dncpartner, log):

        logging.basicConfig(filename='BRD_Sim_Log'+str(number),filemode='w',format='%(message)s',level=logging.INFO)
        self.length = length
        self.opener = open
        self.fight = fight
        self.stats = copy.deepcopy(stats)
        self.party = copy.deepcopy(party)
        self.abilities = copy.deepcopy(abilities)
        self.buffs = copy.deepcopy(buffs)
        self.dots = copy.deepcopy(dots)
        self.pbuffs = copy.deepcopy(pbuffs)
        self.createlog = log
        self.potion = potion
        self.gcd = self.stats[8]
        self.defaultgcd = self.stats[8]
        self.defaultstats = stats
        self.CDHStats= [self.stats[3],self.stats[4],self.stats[5],1.25]
        self.damagestats = [self.stats[0],self.stats[1],self.stats[2],self.stats[6],self.stats[7]]
        self.autotime = self.stats[1]
        self.abilitydelay = .7

        self.precastpotion = False
        self.prepullpottime = 0
        self.precastraging = False
        self.prepullragingtime = 0

        self.rep = 0
        self.soulvoice = 0

        self.clock = 0
        self.potency = 0
        self.astime = -1

        self.timetable = []
        self.viewtime = 5
        self.gettimetable = True

        if 'AST' in self.party.keys():
            self.ast = astmodule(number,astpriority,self.fight,False)
            goodcard = buff('Bole', 15, 0, 1.06, 0, 'pot')
            bigcard = buff('Lady', 15, 0, 1.08, 0, 'pot')
            divination = buff('Divination', 15, 0, 1.06, 180, 'pot')
            self.astbuff = [goodcard,bigcard,divination]
            self.astbuffs = {}
            for i in self.astbuff:
                self.astbuffs[i.name] = i
            self.astime = 0
        if 'DNC' in self.party.keys():
            if dncpartner:
                self.partner = True
            else:
                self.partner = False
        else:
            self.partner = False

    def buildopentable(self):

            actiontable = []
            clock = 0
            nextgcd = 0
            nextaction = 0

            for i in self.opener:
                clock = round(clock, 2)
                if i.split()[0] == 'AutoGCD':
                    if nextgcd > clock:
                        clock = round(nextgcd, 2)
                    if nextaction > clock:
                        clock = round(nextaction, 2)
                    actiontable.append(action(19, 'AutoGCD', clock))
                    nextgcd = round(clock + self.gcd, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
                elif i.split()[0] == 'AutoGCDIJ':
                    if nextgcd > clock:
                        clock = round(nextgcd, 2)
                    if nextaction > clock:
                        clock = round(nextaction, 2)
                    actiontable.append(action(19, 'AutoGCDIJ', clock))
                    nextgcd = round(clock + self.gcd, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
                elif i.split()[0] == 'AutoOGCD':
                    limit = int(i.split()[1])
                    counter = 0
                    while limit > counter:
                        counter = counter + 1
                        if nextaction > clock:
                            clock = round(nextaction, 2)
                        actiontable.append(action(19, 'AutoOGCD', clock))
                        nextaction = round(clock + self.abilitydelay, 2)
                elif i.split()[0] == 'Potion':
                    actiontable.append(action(19, 'Potion', clock))
                    nextaction = round(clock + 1.5, 2)
                    clock = round(clock + 1.5, 2)
                elif i.split()[0] == 'PotionPre':
                    self.precastpotion = True
                    self.prepullpottime = round(0 - float(i.split()[1]), 2)
                elif i.split()[0] == 'PreRaging':
                    self.precastraging = True
                    self.prepullragingtime = round(0 - float(i.split()[1]), 2)
                elif i.split()[0] == 'AutoPP':
                    limit = int(i.split()[1])
                    counter = 0
                    while limit > counter:
                        counter = counter + 1
                        if nextaction > clock:
                            clock = round(nextaction, 2)
                        actiontable.append(action(19, 'AutoPP', clock))
                        nextaction = round(clock + self.abilitydelay, 2)
                else:
                    identify = 0
                    for u in self.abilities.values():
                        if u.name == i:
                            if u.abiltype == 'GCD':
                                if nextgcd > clock:
                                    clock = round(nextgcd, 2)
                                if nextaction > clock:
                                    clock = round(nextaction, 2)
                                actiontable.append(action(identify, u.name, clock))
                                nextgcd = round(clock + self.gcd, 2)
                                nextaction = round(clock + self.abilitydelay, 2)
                                clock = round(clock + self.abilitydelay, 2)
                            else:
                                if nextaction > clock:
                                    clock = round(nextaction, 2)
                                actiontable.append(action(identify, u.name, clock))
                                nextaction = round(clock + self.abilitydelay, 2)
                                clock = round(clock + self.abilitydelay, 2)
                        identify = identify + 1
            self.action = actiontable

    def checkproc(self,rate):
        return (random.randint(1, 10001) > 10000 * (1-rate))

    def handlerep(self):
        if self.buffs['Minuet'].getactive(self.clock):
            if self.rep < 3:
                self.rep = self.rep + 1
            else:
                if self.createlog:
                    logging.info(str(self.clock)+' You lost a proc')
            if self.soulvoice < 100:
                self.soulvoice = self.soulvoice + 5
            else:
                if self.createlog:
                    logging.info(str(self.clock) + ' Too much Soul Voice')
        elif self.buffs['Ballad'].getactive(self.clock):
            if self.abilities['Bloodletter'].available(self.clock):
                if self.createlog:
                    logging.info(str(self.clock)+' You lost a proc')
            else:
                self.abilities['Bloodletter'].resetcd(self.clock)
            if self.soulvoice < 100:
                self.soulvoice = self.soulvoice + 5
            else:
                if self.createlog:
                    logging.info(str(self.clock) + ' Too much Soul Voice')
        elif self.buffs['Paeon'].getactive(self.clock):
            if self.rep < 4:
                self.rep = self.rep + 1
            if self.soulvoice < 100:
                self.soulvoice = self.soulvoice +5
            else:
                if self.createlog:
                    logging.info(str(self.clock)+' Too much Soul Voice')

    def handlemuse(self):
        if self.rep == 4:
            self.buffs['Armys Muse'].potency = 12
        elif self.rep == 3:
            self.buffs['Armys Muse'].potency = 4
        elif self.rep == 3:
            self.buffs['Armys Muse'].potency = 2
        elif self.rep == 1:
            self.buffs['Armys Muse'].potency = 1

    def determinemodgcd(self):
        x = 0
        if self.buffs['Paeon'].getactive(self.clock):
            x = self.rep*4
        elif self.buffs['Armys Muse'].getactive(self.clock):
            x = self.buffs['Armys Muse'].potency
        GCDm = math.floor((1000 - math.floor(130 * (self.stats[7] - 380) / 3300)) * 2500 / 1000)
        A = math.floor(math.floor(math.floor(math.floor((100 - 0) * (100 - 0) / 100) * (100 - 0) / 100)) - 0)
        B = (100 - x) / 100
        GCDc = math.floor(math.floor(math.floor(math.ceil(A * B) * GCDm / 100) * 100 / 1000) * 100 / 100)

        self.gcd = GCDc / 100
        self.autotime = self.damagestats[1] * B

    def buildschedule(self):
        sets = set()
        sets.add(0)
        for i in self.pbuffs.values():
            sets.add(i.default)
        for i in self.party.values():
            sets.add(i.nextgcd)
        for i in self.action:
            sets.add(i.actiontime)
        ###AST Logic Here later###        
        if self.gettimetable:
            for i in range(self.length):
                sets.add(i)
        self.schedule = scheduler(sets)
            
    def buildpotency(self,pot):
        if self.createlog:
            logging.info(pot[1])
        self.potency = self.potency + pot[0]

    def songlogic(self,songname, nexttick, delaystart):
        # Song logic
        # Minuet - If its available and Ballad isn't active or ballad will end before the next tick
        #Ballad - If its available and minuet isnpt active or it will fall before the next tick
        #Paeon - If its available and Ballad and Minuet aren't active or will fall before the next tick
        if songname == 'Minuet':
            if self.abilities['Minuet'].available(self.clock) and (not self.buffs['Ballad'].getactive(self.clock) or self.buffs['Ballad'].endtime < nexttick):
                return True
            else:
                return False
        elif songname == 'Ballad':
            if self.abilities['Ballad'].available(self.clock) and (not self.buffs['Minuet'].getactive(self.clock) or self.buffs['Minuet'].endtime < nexttick):
                return True
            else:
                return False
        else:
            if self.abilities['Paeon'].available(self.clock) and (not self.buffs['Ballad'].getactive(self.clock) or self.buffs['Ballad'].endtime < nexttick) and (not self.buffs['Minuet'].getactive(self.clock) or self.buffs['Minuet'].endtime < nexttick):
                return True
            else:
                return False

    def ealogic(self, nexttick, future, nextgcd):
        #Ea Logic
        #If EA is available
        # If we are in minuet and have 3 rep don't go
        # If we are in ballad and Bloodletter is available don't go
        # If we are in ballad and we don't have time to use the BL proc before next tick, don't go

        if not future:
            if self.abilities['Empyreal Arrow'].available(self.clock):
                if self.buffs['Minuet'].getactive(self.clock) and self.rep > 2:
                    return False
                elif self.buffs['Minuet'].getactive(self.clock) and self.rep > 2 and self.clock - nexttick < self.abilitydelay:
                    return False
                elif self.buffs['Ballad'].getactive(self.clock) and self.abilities['Bloodletter'].available(self.clock):
                    return False
                elif self.buffs['Ballad'].getactive(self.clock) and nexttick - self.clock < self.abilitydelay:
                    return False
                else:
                    return True
            else:
                return False
        else:
            if self.abilities['Empyreal Arrow'].available(nextgcd):
                if self.buffs['Minuet'].getactive(nextgcd) and self.rep > 2:
                    return False
                elif self.buffs['Minuet'].getactive(nextgcd) and self.rep > 1 and nextgcd - nexttick < self.abilitydelay:
                    return False
                elif self.buffs['Ballad'].getactive(nextgcd) and self.abilities['Bloodletter'].available(self.clock):
                    return False
                elif self.buffs['Ballad'].getactive(nextgcd) and nexttick - nextgcd < self.abilitydelay:
                    return False
                else:
                    return True

    def cliplogic(self, nexttick):
        #Clip logic
        # If minuet is up and will drop off within the next gcd and we have more rep than 0 and next tick - .7 is greater than minuets end time - clip
        # if we are in ballad and bl is available and the next tick is within 1.5 seconds, clip
        if self.buffs['Minuet'].getactive(self.clock) and self.buffs['Minuet'].closetodrop(self.clock,self.gcd) and self.rep > 0 and nexttick - self.abilitydelay > self.buffs['Minuet'].endtime:
            return True
        elif self.buffs['Ballad'].getactive(self.clock) and self.abilities['Bloodletter'].available(self.clock) and nexttick - self.clock < 1.5:
            return True
        else:
            return False

    def modprod(self,potmod):
        prod = 1
        for i in potmod:
            prod = prod * i

        return prod

    def snaplogic(self, potmod):
        #Snap logic
        # if the mod on the current dot is great than our current mod don't snap
        # if raging strikes isn't up, don't snap
        # else if our dot time is less than 10 and RS is close to drop, snap
        # if no conditions are met don't snap
        if self.modprod(self.dots['Stormbite'].potmod) > self.modprod(potmod):
            return False
        if not self.buffs['Raging Strikes'].getactive(self.clock):
            return False
        if self.buffs['Raging Strikes'].closetodrop(self.clock, self.gcd) and self.dots['Stormbite'].endtime - self.clock < 10:
            return True
        return False
        ##if self.dots['Stormbite'].endtime - self.clock > 15:
        ##    return False
        ##besttime = 100000000


        ##for i in self.pbuffs.values():
        ##    if i.active:
        ##        if i.type == 'pot':
        ##            if besttime > i.endtime:
        ##                besttime = i.endtime
        ##if self.buffs['Raging Strikes'].getactive(self.clock) and self.buffs['Raging Strikes'].endtime < besttime:
        ##    besttime = self.buffs['Raging Strikes'].endtime

        ##if self.clock + self.gcd > besttime:
        ##    print('Snap')
        ##    return True
        ##else:
        ##    return False



    def futuresonglogic(self,time,songname,nexttick,delaystart):
        if songname == 'Minuet':
            if self.abilities['Minuet'].available(time) and (
                    not self.buffs['Ballad'].getactive(time) or self.buffs['Ballad'].endtime < nexttick):
                return True
            else:
                return False
        elif songname == 'Ballad':
            if self.abilities['Ballad'].available(time) and (
                    not self.buffs['Minuet'].getactive(time) or self.buffs['Minuet'].endtime < nexttick):
                return True
            else:
                return False
        else:
            if self.abilities['Paeon'].available(time) and (not self.buffs['Ballad'].getactive(time) or self.buffs['Ballad'].endtime < nexttick) and (not self.buffs['Minuet'].getactive(time) or self.buffs['Minuet'].endtime < nexttick):
                return True
            else:
                return False

            
    async def sim(self):
        
        self.buildopentable()
        self.buildschedule()


        dex = self.stats[2]
        critrate = self.stats[3]
        critdam = self.stats[4]
        direct = self.stats[5]
        det = self.stats[6]
        sks = self.stats[7]
        
        
        delayedpos = 0
        delayeddance = 0
        delay = False
        delaystart = 0
        delayend = 0
        buffdelay = 0
        gcd = 0

        buffwindow = True
        buffwindowend = 0
        stillinopener = True
        posinopen = 0
        lastbuffwindow = 0

        # Next GCD / Action and Server Tick Trackers
        nextgcd = 0
        oldgcd = 0
        nextaction = 0
        nexttick = round(random.randint(0,300)/100,2)
        self.schedule.addtime(nexttick)
        clip = False


        # Auto Information
        nextauto = 1
        self.schedule.addtime(1)
        # Values to keep track and help print updates

        oldpot = 0
        oldrep = 0
        oldsv = 0

        if self.precastpotion:
            self.buffs['Potion'].activate(self.prepullpottime)
            self.abilities['Potion'].putonCD(self.prepullpottime)
            if self.buffs['Potion'].activation > 0:
                self.schedule.addtime(self.buffs['Potion'].activation)
            else:
                string = self.buffs['Potion'].switchon(self.buffs['Potion'].activation)
                self.schedule.addtime(self.buffs['Potion'].endtime)
                if self.createlog:
                    logging.info(string)

        if self.precastraging:
            self.buffs['Raging Strikes'].activate(self.prepullragingtime)
            self.abilities['Raging Strikes'].putonCD(self.prepullragingtime)
            if self.buffs['Raging Strikes'].activation > 0:
                self.schedule.addtime(self.buffs['Potion'].activation)
            else:
                string = self.buffs['Raging Strikes'].switchon(self.buffs['Raging Strikes'].activation)
                self.schedule.addtime(self.buffs['Raging Strikes'].endtime)
                if self.createlog:
                    logging.info(string)
        #### Sim Start ###
        delaystart = round(self.fight[delayedpos][0], 2)
        delayend = round(self.fight[delayedpos][1], 2)
        buffdelay = self.fight[delayedpos][2]
        self.schedule.addtime(delaystart)
        self.schedule.addtime(delayend)
        while self.clock < self.length:

            oldgcd = nextgcd
            ## Check if we have entered a delay in the fight
            if self.clock == delaystart:
                nextgcd = round(delayend, 2)
                nextaction = round(delayend, 2)
                nextauto = round(delayend,2)
                delayeddance = round(delayend - 14, 2)
                self.schedule.addtime(nextgcd)
                self.schedule.addtime(nextaction)
                self.schedule.addtime(delayeddance)
                if self.createlog:
                    logging.info(str(self.clock) + ' : Boss has jumped')
                delay = True
                stillinopener = False  # To avoid complications)

            elif self.clock == delayend:
                if self.createlog:
                    logging.info(str(self.clock) + ' : Boss has Returned')
                delay = False
                delayedpos = delayedpos + 1
                if delayedpos < len(self.fight):
                    delaystart = round(self.fight[delayedpos][0], 2)
                    delayend = round(self.fight[delayedpos][1], 2)
                    buffdelay = self.fight[delayedpos][2]
                    self.schedule.addtime(delaystart)
                    self.schedule.addtime(delayend)
                else:
                    delaystart = 1000000
                    delayend = 10000001

            
            ## Set Defaults
            potmod = [1.20]
            automod = [1]
            dex = self.stats[2]
            critrate = self.stats[3]
            critdam = self.stats[4]
            direct = self.stats[5]
            det = self.stats[6]
            sks = self.stats[7]

            if self.partner:
                potmod.append(1.05)
            
            # Activate potion value if its available
            if self.buffs['Potion'].available:
                if self.buffs['Potion'].ready and self.buffs['Potion'].activation == self.clock:
                    string = self.buffs['Potion'].switchon(self.clock)
                    if self.createlog:
                        logging.info(string)
                if self.buffs['Potion'].getactive(self.clock):
                    if dex * self.buffs['Potion'].potency > 339:
                        dex = dex + 339
                    else:
                        dex = dex + (dex * self.buffs['Potion'].potency)
                elif self.buffs['Potion'].active:
                    string = self.buffs['Potion'].dropbuff(self.clock)
                    if self.createlog:
                        logging.info(string)
                    dex = self.stats[2]
                    
            # Run Ast Module then see whic buffs are one
            if self.astime == self.clock:
                block = self.ast.sim(self.clock)
                self.astime = block[0]
                astkey = block[1]
                if astkey == '6':
                    self.astbuffs['Divination'].specialactivate(self.clock, 6)
                    self.schedule.addtime(self.astbuffs['Divination'].activation)
                elif astkey == '4':
                    self.astbuffs['Divination'].specialactivate(self.clock, 4)
                    self.schedule.addtime(self.astbuffs['Divination'].activation)
                elif astkey == '2':
                    self.astbuffs['Divination'].specialactivate(self.clock, 2)
                    self.schedule.addtime(self.astbuffs['Divination'].activation)
                elif not astkey == 'None':
                    self.astbuffs[astkey].activate(self.clock)
                    self.schedule.addtime(self.astbuffs[astkey].activation)
                self.schedule.addtime(self.astime)

            if 'AST' in self.party.keys():
                for i in self.astbuffs.values():
                    if i.activation == self.clock:
                        string = i.switchon(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.schedule.addtime(round(i.endtime+.01, 2))
                    elif not i.getactive(self.clock) and i.active:
                        string = i.dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                    elif i.getactive(self.clock):
                        potmod.append(i.getpotency(self.clock))
                        automod.append(i.getpotency(self.clock))




            
            for i in self.pbuffs.values():
                if i.available:
                    if delayedpos < len(self.fight):
                        if i.starttime + (i.duration - 2) > delaystart or (delay and i.starttime < delayend) and i.starttime <= delayend + i.default:
                            if buffdelay:
                                i.starttime = round(delayend + i.default, 2)
                                self.schedule.addtime(i.starttime)
                            else:
                                i.starttime = round(delayend + 1, 2)
                                self.schedule.addtime(i.starttime)
                    if i.ready and i.activation == self.clock:
                        string = i.switchon(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.schedule.addtime(round(i.endtime + .01,2))
                        self.schedule.addtime(i.starttime)
                    if not i.ready and i.starttime == self.clock:
                        i.activate(self.clock)
                        self.schedule.addtime(i.activation)
                    if i.getactive(self.clock):
                        if i.type == 'pot':
                            potmod.append(i.getpotency(self.clock))
                            automod.append(i.getpotency(self.clock))
                        elif i.type == 'ch':
                            critrate = round(critrate + i.getpotency(self.clock), 2)
                        elif i.type == 'dh':
                            direct = round(direct + i.getpotency(self.clock),2)
                    elif i.available and not i.getactive(self.clock) and i.active:
                        string = i.dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        
            for i in self.buffs.values():
                if i.ready and i.activation == self.clock:
                    if i.type == 'Song':
                        for u in self.buffs.values():
                            if u.type == 'Song' and u.getactive(self.clock):
                                if u.name == 'Paeon':
                                    self.handlemuse()
                                    self.buffs['Armys Muse'].activate(self.clock)
                                    self.schedule.addtime(self.buffs['Armys Muse'].activation)
                                string = u.dropbuff(self.clock)
                                if self.createlog:
                                    logging.info(string)
                                self.rep = 0
                        if self.buffs['Armys Ethos'].getactive(self.clock):
                            self.rep = self.buffs['Armys Ethos'].potency
                            string = self.rep = self.buffs['Armys Ethos'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.handlemuse()
                            self.buffs['Armys Muse'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Armys Muse'].activation)
                            self.rep = 0
                    string = i.switchon(self.clock)
                    if self.createlog:
                        logging.info(string)
                    self.schedule.addtime(round(i.endtime+.01, 2))
                    self.schedule.addtime(i.starttime)

            for i in self.dots.values():
                if i.ready and i.activation == self.clock:
                    string = i.switchon(self.clock)
                    if self.createlog:
                        logging.info(string)
                    self.schedule.addtime(round(i.endtime + .01, 2))
                elif i.active and not i.getactive(self.clock):
                    string = i.dropoff(self.clock)
                    if self.createlog:
                        logging.info(string)

            # Other buffs are procs and combos, track them here
            for i in self.buffs.values():
                if i.active and (not i.getactive(self.clock)):
                    if i.name == 'SS Ready':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You lost the proc ' + i.name)
                        self.buffs['Armys Ethos'].activate(self.clock)
                        self.buffs['Armys Ethos'].potency = self.rep
                        self.schedule.addtime(self.buffs['Armys Ethos'].activation)
                    if i.type == 'Song':
                        self.rep = 0
                    string = i.dropbuff(self.clock)
                    if self.createlog:
                        logging.info(string)

            if self.buffs['Raging Strikes'].getactive(self.clock):
                potmod.append(1.1)

            #if self.buffs['Battle Voice'].getactive(self.clock):
            #    direct = round(direct + self.buffs['Battle Voice'].getpotency(self.clock), 2)

            self.determinemodgcd()
            # Determine if we are in a buff window for logic
            if 'NIN' in self.party.keys() and self.pbuffs['Trick Attack'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            elif self.buffs['Potion'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            elif 'DRG' in self.party.keys() and 'BRD' in self.party.keys() and self.pbuffs['Battle Voice'].getactive(self.clock) and self.pbuffs['Battle Litany'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            else:
                buffwindow = False

            # Determine future stuff next such as Nextbuffwindow, and standard / Technical times
            foundnextbuffwindow = False
            nextbuffwindow = self.clock
            ## Lots of fun dancing logic used to figure out if I'm dancing soon or not and what dances are coming and when technical is coming
            # Could consolidate this to less code if ever needed, some redundancy here

            nextbuffwindow = 100000000000
            foundnextbuffwindow = False

            if 'NIN' in self.party.keys() and self.pbuffs['Trick Attack'].starttime - self.clock < 15:
                foundnextbuffwindow = True
                nextbuffwindow = self.pbuffs['Trick Attack'].starttime
            elif 'DRG' in self.party.keys() and 'BRD' in self.party.keys() and self.pbuffs['Battle Voice'].starttime - self.clock < 15:
                foundnextbuffwindow = True
                if self.pbuffs['Battle Voice'].starttime < nextbuffwindow:
                    nextbuffwindow = self.pbuffs['Battle Voice'].starttime
            ## Reset next buff window
            if nextbuffwindow == 100000000000:
                nextbuffwindow = 0
            # Build tables for pass through
            CDHStats = [critrate, critdam, direct, 1.25]
            DMGStats = [self.stats[0],self.stats[1],dex,self.stats[6],self.stats[7]]


            # Handle Auto
            if self.clock == nextauto:
                if not delay:
                    self.buildpotency(self.abilities['Auto Attack'].getpotency(self.clock, CDHStats, automod, DMGStats, True))
                nextauto = round(self.clock + self.autotime, 2)
                self.schedule.addtime(nextauto)

            # Handle Global Tick
            if self.clock == nexttick:
                for i in self.dots.values():
                    if i.getactive(self.clock):
                        self.buildpotency(i.getpotency(self.clock))
                        if self.checkproc(.4):
                            self.handlerep()
                nexttick = round(self.clock + 3, 2)
                self.schedule.addtime(nexttick)

            # Handle Delay Actions



            # Handle Opener if available
            # ---------------------------------------------------------- MAIN SIM---------------------------------------------------------------------------------------------
            if stillinopener:
                if self.action[posinopen].actionable(self.clock):
                    currentaction = self.action[posinopen]
                    if currentaction.name == 'Bloodletter':
                        if self.abilities['Bloodletter'].available:
                            self.buildpotency(self.abilities['Bloodletter'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                    elif currentaction.name == 'Empyreal Arrow':
                        if self.abilities['Empyreal Arrow'].available:
                            self.buildpotency(self.abilities['Empyreal Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            self.handlerep()
                    elif currentaction.name == 'Caustic Bite':
                        self.buildpotency(self.abilities['Caustic Bite'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Caustic Bite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.schedule.addtime(self.dots['Caustic Bite'].activation)
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif currentaction.name == 'Stormbite':
                        self.buildpotency(self.abilities['Stormbite'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Stormbite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.schedule.addtime(self.dots['Stormbite'].activation)
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif currentaction.name == 'Iron Jaws':
                        self.buildpotency(self.abilities['Iron Jaws'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Stormbite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.dots['Caustic Bite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.schedule.addtime(self.dots['Stormbite'].activation)
                        self.schedule.addtime(self.dots['Caustic Bite'].activation)
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif currentaction.name == 'Refulgent Arrow':
                        self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        if self.buffs['Barrage'].getactive(self.clock):
                            #gcd = gcd + 2
                            self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,True))
                            self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,True))
                            string = self.buffs['Barrage'].dropbuff(self.clock)
                            gcd = gcd + 1
                            if self.createlog:
                                logging.info(string)
                        string = self.buffs['SS Ready'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                    elif currentaction.name == 'Barrage':
                        if self.createlog:
                            logging.info(str(self.clock)+" : You use Barrage")
                        self.abilities['Barrage'].putonCD(self.clock)
                        self.buffs['SS Ready'].activate(self.clock)
                        self.schedule.addtime(self.buffs['SS Ready'].activation)
                        self.buffs['Barrage'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Barrage'].activation)
                    elif currentaction.name == 'Potion':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use a Potion!')
                        self.abilities['Potion'].putonCD(self.clock)
                        self.buffs['Potion'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Potion'].activation)
                    elif currentaction.name == 'Raging Strikes':
                        if self.abilities['Raging Strikes'].available(self.clock):
                            self.abilities['Raging Strikes'].putonCD(self.clock)
                            self.buffs['Raging Strikes'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Raging Strikes'].activation)
                    elif currentaction.name == 'Battle Voice':
                        if self.createlog:
                            logging.info(str(self.clock)+" : You use Battle Voice")
                        if self.abilities['Battle Voice'].available(self.clock):
                            self.abilities['Battle Voice'].putonCD(self.clock)
                            self.buffs['Battle Voice'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Battle Voice'].activation)
                    elif currentaction.name == 'Minuet':
                        if self.abilities['Minuet'].available(self.clock):
                            self.buildpotency(self.abilities['Minuet'].getpotency(self.clock, CDHStats, automod, DMGStats, True))
                            self.abilities['Minuet'].putonCD(self.clock)
                            self.buffs['Minuet'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Minuet'].activation)
                            if self.createlog:
                                logging.info(str(self.clock)+ " : You use Wanderer's Minuet")
                    elif currentaction.name == 'AutoGCD':
                        # Auto GCD in the self.action
                        # If RA is procced use it
                        # If Not use Burst
                        gcd = gcd + 1
                        if self.buffs['SS Ready'].getactive(self.clock):
                            self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            if self.buffs['Barrage'].getactive(self.clock):
                                #gcd = gcd + 2
                                self.buildpotency(
                                    self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                 True))
                                self.buildpotency(
                                    self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                 True))
                                string = self.buffs['Barrage'].dropbuff(self.clock)
                                if self.createlog:
                                    logging.info(string)
                            self.buffs['SS Ready'].dropbuff(self.clock)
                        else:
                            self.buildpotency(self.abilities['Burst Shot'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            if self.checkproc(.35):
                                self.buffs['SS Ready'].activate(self.clock)
                                self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif currentaction.name == 'AutoGCDIJ':
                        # Auto GCD in the self.action
                        # If RA is procced use it
                        # If Not use Burst
                        gcd = gcd + 1
                        if self.buffs['SS Ready'].getactive(self.clock):
                            self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            if self.buffs['Barrage'].getactive(self.clock):
                                #gcd = gcd + 2
                                self.buildpotency(
                                    self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                 True))
                                self.buildpotency(
                                    self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                 True))
                                string = self.buffs['Barrage'].dropbuff(self.clock)
                                if self.createlog:
                                    logging.info(string)
                            self.buffs['SS Ready'].dropbuff(self.clock)
                        elif not self.abilities['Barrage'].available(self.clock) and not self.dots['Caustic Bite'].endtime == self.dots['Stormbite'].endtime:
                            self.buildpotency(self.abilities['Iron Jaws'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            self.dots['Stormbite'].activate(self.clock, CDHStats, potmod, DMGStats)
                            self.dots['Caustic Bite'].activate(self.clock, CDHStats, potmod, DMGStats)
                            self.schedule.addtime(self.dots['Stormbite'].activation)
                            self.schedule.addtime(self.dots['Caustic Bite'].activation)
                            if self.checkproc(.35):
                                self.buffs['SS Ready'].activate(self.clock)
                                self.schedule.addtime(self.buffs['SS Ready'].activation)
                        else:
                            self.buildpotency(self.abilities['Burst Shot'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            if self.checkproc(.35):
                                self.buffs['SS Ready'].activate(self.clock)
                                self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif currentaction.name == 'AutoOGCD':
                        # AutoOGCD in the self.action
                        # For now passing until I see a need
                        if not self.buffs['SS Ready'].getactive(self.clock) and self.abilities['Barrage'].available(self.clock):
                            if self.createlog:
                                logging.info(str(self.clock) + " : You use Barrage")
                            self.abilities['Barrage'].putonCD(self.clock)
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                            self.buffs['Barrage'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Barrage'].activation)
                        elif self.buffs['Minuet'].getactive(self.clock) and self.rep > 2 and self.abilities['Pitch Perfect'].available(self.clock):
                                self.buildpotency(self.abilities['Pitch Perfect'].pitchpotency(self.clock, CDHStats, potmod,DMGStats, True, self.rep))
                                self.rep = 0
                        elif self.abilities['Bloodletter'].available(self.clock):
                                self.buildpotency(self.abilities['Bloodletter'].getpotency(self.clock, CDHStats, potmod, DMGStats,True))
                    elif currentaction.name == 'AutoPP':
                        # Will just PP at 3 stacks.
                        if self.buffs['Minuet'].getactive(self.clock) and self.rep > 2:
                            if self.abilities['Pitch Perfect'].available(self.clock):
                                self.buildpotency(self.abilities['Pitch Perfect'].pitchpotency(self.clock, CDHStats, potmod, DMGStats, True,self.rep))
                                self.rep = 0
                    elif currentaction.name == 'Hold':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : Waiting')

                    posinopen = posinopen + 1
                    if posinopen >= len(self.action):
                        if self.createlog:
                            logging.info('Finished with self.action, commencing Sim')
                        # Let's figure out when our last GCD was
                        foundlastGCD = False
                        foundlastaction = False
                        while (not foundlastGCD):
                            currentaction = self.action[posinopen - 1]
                            if currentaction.name == 'AutoGCD' or currentaction.name == 'AutoGCDIJ' or self.abilities[currentaction.name].abiltype == 'GCD':
                                if not foundlastaction:
                                    foundlastaction = True
                                    nextaction = round(self.clock + self.abilitydelay, 2)
                                foundlastGCD = True
                                nextgcd = round(self.clock + self.gcd, 2)
                            elif currentaction.name == 'AutoOGCD' or self.abilities[currentaction.name].abiltype == 'OGCD':
                                if not foundlastaction:
                                    foundlastaction = True
                                    nextaction = round(self.clock + self.abilitydelay, 2)
                            posinopen = posinopen - 1
                        stillinopener = False
            else:
                # GCD Priority List - Update this
                # # If Soul Voice is 95 or above > Use Apex Arrow
                # If Barrage is active > Use Refulgent
                # If Both dots are active and we pass the snap logic(See below) we use Iron Jaws
                # If both dots are active and If dots expire on or before next GCD > Iron Jaws
                # If Storm isn't up > Stormbite
                # If Caustic isn't up > Caustic bite
                # If refulgent expires within the next GCD > Refulgent
                # If Soul Voice is 95 or above > Use Apex Arrow
                # Use Refulgent If SS is up
                # Use Burst Shot

                if nextgcd == self.clock:
                    clip = False
                    if self.soulvoice > 100 and not (self.dots['Caustic Bite'].closetodrop(self.clock,self.gcd) or self.dots['Stormbite'].closetodrop(self.clock,self.gcd)):
                        self.buildpotency(self.abilities['Apex Arrow'].apexpotency(self.clock, CDHStats, potmod, DMGStats, True,self.soulvoice))
                        self.soulvoice = 0
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.buffs['Barrage'].getactive(self.clock) and self.buffs['SS Ready'].getactive(self.clock):
                        i = 0
                        gcd = gcd + 1
                        while i < 3:
                            #gcd = gcd + 1
                            self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            i = i + 1
                        string = self.buffs['Barrage'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        string = self.buffs['SS Ready'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.dots['Caustic Bite'].getactive(self.clock) and self.dots['Stormbite'].getactive(self.clock) and self.snaplogic(potmod):
                            self.buildpotency(self.abilities['Iron Jaws'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                            self.dots['Caustic Bite'].activate(self.clock, CDHStats, potmod, DMGStats)
                            self.dots['Stormbite'].activate(self.clock, CDHStats, potmod, DMGStats)
                            self.schedule.addtime(self.dots['Caustic Bite'].activation)
                            self.schedule.addtime(self.dots['Stormbite'].activation)
                            gcd = gcd + 1
                            nextgcd = round(self.clock + self.gcd, 2)
                            nextaction = round(self.clock + self.abilitydelay, 2)
                            if self.checkproc(.35):
                                self.buffs['SS Ready'].activate(self.clock)
                                self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif self.dots['Caustic Bite'].getactive(self.clock) and self.dots['Stormbite'].getactive(self.clock) and (self.dots['Caustic Bite'].closetodrop(self.clock,self.gcd) or self.dots['Stormbite'].closetodrop(self.clock,self.gcd)):
                        self.buildpotency(self.abilities['Iron Jaws'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Caustic Bite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.dots['Stormbite'].activate(self.clock,CDHStats,potmod,DMGStats)
                        self.schedule.addtime(self.dots['Caustic Bite'].activation)
                        self.schedule.addtime(self.dots['Stormbite'].activation)
                        gcd = gcd + 1
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                    elif not self.dots['Stormbite'].getactive(self.clock):
                        self.buildpotency(self.abilities['Stormbite'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Stormbite'].activate(self.clock, CDHStats, potmod, DMGStats)
                        self.schedule.addtime(self.dots['Stormbite'].activation)
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif not self.dots['Caustic Bite'].getactive(self.clock):
                        self.buildpotency(self.abilities['Caustic Bite'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        self.dots['Caustic Bite'].activate(self.clock, CDHStats, potmod, DMGStats)
                        self.schedule.addtime(self.dots['Caustic Bite'].activation)
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.buffs['SS Ready'].getactive(self.clock) and self.buffs['SS Ready'].closetodrop(self.clock, self.gcd):
                        self.buildpotency(self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        string = self.buffs['SS Ready'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        gcd = gcd + 1
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.soulvoice > 95:
                        self.buildpotency(self.abilities['Apex Arrow'].apexpotency(self.clock, CDHStats, potmod, DMGStats, True,self.soulvoice))
                        self.soulvoice = 0
                        gcd = gcd + 1
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.buffs['SS Ready'].getactive(self.clock):
                        self.buildpotency(
                            self.abilities['Refulgent Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        string = self.buffs['SS Ready'].dropbuff(self.clock)
                        gcd = gcd + 1
                        if self.createlog:
                            logging.info(string)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    else:
                        self.buildpotency(
                            self.abilities['Burst Shot'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        gcd = gcd + 1
                        if self.checkproc(.35):
                            self.buffs['SS Ready'].activate(self.clock)
                            self.schedule.addtime(self.buffs['SS Ready'].activation)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    #             # If anything changes, post an updated
                elif nextaction == self.clock:
                    # oGCD Priority list
                    # If we think its ok to clip in minuet (About to fall off with REP) use PP
                    # If we think its ok to clip in ballad (Dot tick soon and BL is up) use BL
                    # If we are in ballad, bloodletter is available and nextick is within 1.4s we use Bloodletter
                    # If we are in minuet and we have rep and Minuet falls with the next gcd - Use PP
                    #If we are in minuet and we have 3 rep use PP
                    # If minuet is available, we are not in ballad or if we are in ballad but it will fall before next tick - Use Minuet
                    # If ballad is available, we are not in minuet or if we are in minuet but it will fall before next tick - Use Ballad
                    # if paeon is available, If no songs are active, use Paeon if ballad or minuet are active but will fall off before next tick, use Paeon
                    # if Raging strikes is available and we are 1.5s away from a GCD and we are no in Paeon, use it
                    # if BV is available, use it
                    # if EA is available, use it
                    # if barrage is available and SS isn't ready, use it
                    # If bloodletter is available, use it
                    # if SW is available, use it
                    abilityused = False
                    if clip and self.buffs['Minuet'].getactive(self.clock) and self.abilities['Pitch Perfect'].available(self.clock) and self.rep > 0:
                        self.buildpotency(
                            self.abilities['Pitch Perfect'].pitchpotency(self.clock, CDHStats, potmod, DMGStats, True,
                                                                         self.rep))
                        self.rep = 0
                        clip = False
                        abilityused = True
                    elif clip and self.buffs['Ballad'].getactive(self.clock) and self.abilities['Bloodletter'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Bloodletter'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        clip = False
                        abilityused = True
                    elif not clip and self.buffs['Ballad'].getactive(self.clock) and self.abilities['Bloodletter'].available(self.clock) and nexttick - self.clock < 1.4:
                        self.buildpotency(self.abilities['Bloodletter'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        abilityused = True
                    elif self.buffs['Minuet'].getactive(self.clock) and self.rep > 2 and self.abilities['Pitch Perfect'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Pitch Perfect'].pitchpotency(self.clock, CDHStats, potmod, DMGStats, True,
                                                                         self.rep))
                        self.rep = 0
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        abilityused = True
                    elif self.buffs['Minuet'].getactive(self.clock) and self.rep > 0 and self.buffs['Minuet'].endtime < nextgcd and self.abilities['Pitch Perfect'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Pitch Perfect'].pitchpotency(self.clock, CDHStats, potmod, DMGStats, True,
                                                                         self.rep))
                        self.rep = 0
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        abilityused = True
                    elif not clip and self.songlogic('Minuet',nexttick,delaystart):
                        self.buildpotency(self.abilities['Minuet'].getpotency(self.clock, CDHStats, automod, DMGStats, True))
                        self.abilities['Minuet'].putonCD(self.clock)
                        self.buffs['Minuet'].activate(self.clock)
                        abilityused = True
                        self.schedule.addtime(self.buffs['Minuet'].activation)
                    elif not clip and self.songlogic('Ballad',nexttick,delaystart):
                        self.buildpotency(self.abilities['Ballad'].getpotency(self.clock, CDHStats, automod, DMGStats, True))
                        self.buffs['Ballad'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Ballad'].activation)
                        abilityused = True
                    elif not clip and self.songlogic('Paeon',nexttick,delaystart):
                        self.buildpotency(self.abilities['Paeon'].getpotency(self.clock, CDHStats, automod, DMGStats, True))
                        self.buffs['Paeon'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Paeon'].activation)
                        abilityused = True
                    elif not clip and self.abilities['Raging Strikes'].available(self.clock) and nextgcd - self.clock < 1.5 and not self.buffs['Paeon'].getactive(self.clock):
                        self.abilities['Raging Strikes'].putonCD(self.clock)
                        self.buffs['Raging Strikes'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Raging Strikes'].activation)
                        abilityused = True
                        if self.createlog:
                            logging.info(str(self.clock)+' : You use Raging Strikes')
                    elif not clip and self.abilities['Battle Voice'].available(self.clock):
                        self.abilities['Battle Voice'].putonCD(self.clock)
                        self.buffs['Battle Voice'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Battle Voice'].activation)
                        abilityused = True
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use Battle Voice')
                    elif self.ealogic(nexttick,False,nextgcd):
                        self.buildpotency(self.abilities['Empyreal Arrow'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        self.handlerep()
                        abilityused = True
                    elif not clip and self.abilities['Barrage'].available(self.clock) and not self.buffs['SS Ready'].getactive(self.clock) and not (self.dots['Caustic Bite'].closetodrop(self.clock,self.gcd) or self.dots['Stormbite'].closetodrop(self.clock,self.gcd)):
                        self.abilities['Barrage'].putonCD(self.clock)
                        self.buffs['Barrage'].activate(self.clock)
                        self.buffs['SS Ready'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Barrage'].activation)
                        abilityused = True
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use Barrage')

                    elif self.abilities['Bloodletter'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Bloodletter'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        abilityused = True
                    elif self.potion and self.abilities['Potion'].available(self.clock) and (nextgcd - nextaction) > 1.5 and (self.abilities['Raging Strikes'].getrecast(self.clock) < 10):
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use a potion!')
                        self.buffs['Potion'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Potion'].activation)
                        self.abilities['Potion'].putonCD(self.clock)
                        self.abilitydelay = 1.5
                        abilityused = True
                    elif not clip and self.abilities['Sidewinder'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Sidewinder'].getpotency(self.clock, CDHStats, potmod, DMGStats, True))
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        abilityused = True
                    if abilityused:  # Process new action time
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        if nextaction > nextgcd:
                            nextgcd = nextaction
                        elif nextaction + self.abilitydelay > nextgcd  and not clip:
                            if not self.cliplogic(nexttick):
                                nextaction = round(nextgcd, 2)  # I want to avoid clipping
                            else:
                                if self.createlog:
                                    logging.info(str(self.clock) + ': Attempting to Clip')
                                if self.buffs['Minuet'].getactive(self.clock) and not self.abilities['Pitch Perfect'].available(self.clock) and self.abilities['Pitch Perfect'].nextuse > nextaction and self.abilities['Pitch Perfect'].nextuse < self.buffs['Minuet'].endtime:
                                    nextaction = self.abilities['Pitch Perfect'].nextuse
                                clip = True
                        self.abilitydelay = .7
                    else: ### Future Schedule Logic
                        if not self.abilities['Bloodletter'].available(self.clock) and self.abilities['Bloodletter'].getrecast(self.clock) <= nextgcd - self.clock - self.abilitydelay:
                            nextaction = round(self.abilities['Bloodletter'].nextuse,2)
                        elif not self.abilities['Barrage'].available(self.clock) and self.abilities['Barrage'].getrecast(self.clock) <= nextgcd - self.clock - self.abilitydelay:
                            nextaction = round(self.abilities['Barrage'].nextuse,2)
                        elif not self.abilities['Battle Voice'].available(self.clock) and self.abilities['Battle Voice'].getrecast(self.clock) <= nextgcd - self.clock - self.abilitydelay and not (self.dots['Caustic Bite'].closetodrop(self.clock,self.gcd) or self.dots['Stormbite'].closetodrop(self.clock,self.gcd)):
                            nextaction = round(self.abilities['Battle Voice'].nextuse,2)
                        elif not self.abilities['Raging Strikes'].available(self.clock) and self.abilities['Raging Strikes'].getrecast(self.clock) <= nextgcd - self.clock - self.abilitydelay and not self.buffs['Paeon'].getactive(self.clock) and self.abilities['Raging Strikes'].nextuse - self.clock < 1.5:
                            nextaction = round(self.abilities['Raging Strikes'].nextuse,2)
                        elif not self.abilities['Empyreal Arrow'].available(self.clock) and self.abilities['Empyreal Arrow'].available(nextgcd) and self.ealogic(nexttick,True,nextgcd):
                            nextaction = round(self.abilities['Empyreal Arrow'].nextuse, 2)
                        else:
                            if nexttick < nextgcd:
                                nextaction = round(nexttick,2)
                            else:
                                nextaction = round(nextgcd, 2)
                        if nextaction < self.clock:
                            nextaction = round(self.clock + .01, 2)
                        if nextaction > nextgcd:
                            nextgcd = nextaction
                        elif nextaction + self.abilitydelay > nextgcd and not clip:
                            if not self.cliplogic(nexttick):
                                nextaction = round(nextgcd, 2)  # I want to avoid clipping
                            elif not nextaction >= nextgcd:
                                if self.buffs['Minuet'].getactive(self.clock) and not self.abilities['Pitch Perfect'].available(self.clock) and self.abilities['Pitch Perfect'].nextuse > nextaction and self.abilities['Pitch Perfect'].nextuse < self.buffs['Minuet'].endtime:
                                    nextaction = self.abilities['Pitch Perfect'].nextuse
                                clip = True

                        # Define the times we will want to act next
                        # 1. When FD1 is back up and we will not CLIP
                        # 2. If Flourish comes back within the next GCD and we want to use it
                        # 3. IF potion comes back within the next GCD and we want to use it


                # check to see if its within any GCD use at my current self.clock position
                # check to make sure its not happening in the next GCD
                # make sure I'm not dancing
                # make sure its a technical hold
                # check if the delay start time - its next use is greater than 22 before enforcing the hold
                # Make sure I have enough time to saber dance? How do I check that
            if self.gettimetable and self.clock == self.viewtime:
                if self.clock > 0:
                    self.timetable.append(self.potency/self.clock)
                else:
                    self.timetable.append(self.potency)
                self.viewtime = self.viewtime + 1
            if (oldpot != self.potency) or (oldsv != self.soulvoice) or (oldrep != self.rep):
                if self.createlog:
                    logging.info(str(self.clock) + ' : Potency: ' + str(round(self.potency, 1))+' '+ str(potmod) + ' || Soul Voice: ' + str(
                        self.soulvoice) + ' || Repertoire: ' + str(self.rep) + ' || Crit Rate: ' + str(
                        CDHStats[0]) + ' || DH Rate: ' + str(CDHStats[2]))
                oldpot = self.potency
                oldsv = self.soulvoice
                oldrep = self.rep
            # Advance self.clock
            if nextaction > nextgcd: #If I forced the clip, back it up
                nextgcd = round(nextaction + self.abilitydelay, 2)
            if nextgcd > 0 and not stillinopener:
                self.schedule.addtime(nextgcd)
            if nextaction > 0 and not stillinopener:
                self.schedule.addtime(nextaction)
            self.clock = self.schedule.nexttime()
        # print info after if logging
        if self.createlog:
            logging.info("------Results-----")
            logging.info("Time Ran : " + str(self.clock))
            logging.info("Potency : " + str(self.potency))
            logging.info("Potency per Second : " + str(self.potency / self.clock))
            #logging.info("Repetoire: " + str(self.feathers))
            logging.info("Soul Voice Remaining: " + str(self.soulvoice))
            logging.info("GCDs Used: " + str(self.clock/gcd))
            #logging.info("Feathers used: " + str(feathersused))
            #logging.info("Flourished Fans: " + str(flourishedfans))
            #logging.info("Devilments Used: " + str(useddevilments))
            #logging.info('Flourish Procs Dropped : ' + str(self.procdrop))
            #logging.info('Feathers Dropped : ' + str(self.feathersdropped))
            #logging.info('Esprit Cap : ' + str(self.espritcap))

        #print(gcd)
        return round(self.potency/self.length, 4)








