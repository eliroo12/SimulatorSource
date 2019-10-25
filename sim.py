from buff import buff
from ability import ability
from action import action
from scheduler import scheduler
from astmodule import astmodule
from job import job
from card import card
import logging
import random
import asyncio
import copy


class sim:
    # stat table build out = WD,Wepdelay,Dex,Critrate,Critdamage,Directrate,Det,skillspeed,gcd
    # int,     int,  table, table, table,   dict,   dict,    dict,   bool, bool,   bool
    def __init__(self, number, length, open, fight, stats, abilities, party, pbuffs, buffs, potion, astpriority, log):

        logging.basicConfig(filename='DNC_Sim_Log' + str(number), filemode='w', format='%(message)s',
                            level=logging.INFO)
        self.length = length
        self.opener = open
        self.fight = fight
        self.stats = copy.deepcopy(stats)
        self.party = copy.deepcopy(party)
        self.abilities = copy.deepcopy(abilities)
        self.buffs = copy.deepcopy(buffs)
        self.pbuffs = copy.deepcopy(pbuffs)
        self.createlog = log
        self.potion = potion
        self.gcd = stats[8]
        self.defaultstats = stats
        self.cdhstats = [stats[3], stats[4], stats[5], 1.25]
        self.damagestats = [stats[0], stats[1], stats[2], stats[6], stats[7]]
        self.abilitydelay = .7

        self.esprit = 0
        self.rate = .3
        self.feathers = 0
        self.potency = 0

        self.feathersdropped = 0
        self.espritcap = 0
        self.procdrop = 0
        self.combodrops = 0

        self.clock = 0
        self.astime = -1

        self.timetable = []
        self.viewtime = 5
        self.gettimetable = True

        self.prepullpot = False
        self.prepulltime = 0
        self.forceTdrift = False
        self.forceSdrift = False

        if 'AST' in self.party.keys():
            self.ast = astmodule(number, astpriority, self.fight, False)
            goodcard = buff('Bole', 15, 0, 1.06, 0, 'pot')
            bigcard = buff('Lady', 15, 0, 1.08, 0, 'pot')
            divination = buff('Divination', 15, 0, 1.06, 180, 'pot')
            self.astbuff = [goodcard, bigcard, divination]
            self.astbuffs = {}
            for i in self.astbuff:
                self.astbuffs[i.name] = i
            self.astime = 0

    def buildopentable(self):

        actiontable = []
        clock = 0
        nextgcd = 0
        nextaction = 0

        for i in self.opener:
            clock = round(clock, 2)
            if i.split()[0] == 'Hold':
                actiontable.append(action(19, 'Hold', clock))
                clock = clock + float(i.split()[1])
            elif i.split()[0] == 'Pretech':
                self.abilities['Technical Step'].putonCD(round(0 - 5.5, 2))
            elif i.split()[0] == 'Prepot':
                self.prepullpot = True
                self.prepulltime = round(0 - float(i.split()[1]), 2)
            elif i.split()[0] == 'TechDrift':
                self.forceTdrift = True
            elif i.split()[0] == 'StandDrift':
                self.forceSdrift = True
            elif i.split()[0] == 'Technical':
                if nextgcd > clock:
                    clock = round(nextgcd, 2)
                if nextaction > clock:
                    clock = round(nextaction, 2)
                if i.split()[1] == 'Step':
                    actiontable.append(action(1, 'Technical Step', clock))
                    clock = round(clock + 1.5, 2)
                    counter = 0
                    while counter < 4:
                        counter = counter + 1
                        actiontable.append(action(4, 'Step', clock))
                        clock = round(clock + 1, 2)
                    actiontable.append(action(0, 'Technical Finish', clock))
                    nextgcd = round(clock + 1.5, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
                elif i.split()[1] == 'Finish':
                    actiontable.append(action(0, 'Technical Finish', clock))
                    nextgcd = round(clock + 1.5, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Standard':
                if nextgcd > clock:
                    clock = round(nextgcd, 2)
                if nextaction > clock:
                    clock = round(nextaction, 2)
                if i.split()[1] == 'Step':
                    actiontable.append(action(3, 'Standard Step', clock))
                    clock = round(clock + 1.5, 2)
                    counter = 0
                    while counter < 2:
                        counter = counter + 1
                        actiontable.append(action(4, 'Step', clock))
                        clock = round(clock + 1.0, 2)
                    actiontable.append(action(2, 'Standard Finish', clock))
                    nextgcd = round(clock + 1.5, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
                elif i.split()[1] == 'Finish':
                    actiontable.append(action(2, 'Standard Finish', clock))
                    nextgcd = round(clock + 1.5, 2)
                    nextaction = round(clock + self.abilitydelay, 2)
                    clock = round(clock + self.abilitydelay, 2)
            elif i.split()[0] == 'Potion':
                actiontable.append(action(19, 'Potion', clock))
                nextaction = round(clock + 1.5, 2)
                clock = round(clock + 1.5, 2)
            elif i.split()[0] == 'AutoGCD':
                if nextgcd > clock:
                    clock = round(nextgcd, 2)
                if nextaction > clock:
                    clock = round(nextaction, 2)
                actiontable.append(action(19, 'AutoGCD', clock))
                nextgcd = round(clock + self.gcd, 2)
                nextaction = round(clock + self.abilitydelay, 2)
                clock = round(clock + self.abilitydelay, 2)
            elif i.split()[0] == 'ReverseProc':  # Special selection for opener to drop combo for proc if obtained
                if nextgcd > clock:
                    clock = round(nextgcd, 2)
                if nextaction > clock:
                    clock = round(nextaction, 2)
                actiontable.append(action(19, 'ReverseProc', clock))
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

    def getfeathers(self):
        if self.feathers >= 4:
            self.feathersdropped = self.feathersdropped + 1
            if self.createlog:
                logging.info(str(self.clock) + ' : You cannot get anymore Feathers')
        elif (random.randint(1, 10001) > 10000 * .5):
            self.feathers = self.feathers + 1

    def buildesprit(self, rate):
        rand = random.randint(1, 10001)
        if (rand < 10000 * rate):
            if self.esprit >= 100:
                self.espritcap = self.espritcap + 1
                if self.createlog:
                    logging.info(str(self.clock) + ': You cannot build more Esprit')
            else:
                self.esprit = self.esprit + 10

    def checkproc(self):
        return (random.randint(1, 10001) > 10000 * .50)

    def countprocs(self):

        procounter = 0
        if self.buffs['Flourishing Bladeshower'].getactive(self.clock):
            procounter = procounter + 1
        if self.buffs['Flourishing Windmill'].getactive(self.clock):
            procounter = procounter + 1
        if self.buffs['Flourishing Cascade'].getactive(self.clock):
            procounter = procounter + 1
        if self.buffs['Flourishing Fountain'].getactive(self.clock):
            procounter = procounter + 1

        return procounter

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

    def buildpotency(self, pot):
        if self.createlog:
            logging.info(pot[1])
        self.potency = self.potency + pot[0]

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

        buffwindow = True
        buffwindowend = 0
        stillinopener = True
        posinopen = 0
        lastbuffwindow = 0

        # Next GCD / Action and Server Tick Trackers
        nextgcd = 0
        nextaction = 0
        nexttick = 0

        # Dancing vars
        standarddancing = False
        technicaldancing = False
        stepsneeded = 0

        # Values to determine Saber / Technical positioning
        saberfirst = False
        technicalfirst = False

        # Standard / Technical holds per GCD tier for sim logic
        technicalhold = False
        standardhold = False
        technicalholdlist = [2.50, 2.49, 2.48, 2.44, 2.43, 2.38]
        standardholdlist = [2.5, 2.49, 2.48, 2.47]

        for i in technicalholdlist:
            if i == self.gcd:
                technicalhold = True

        for i in standardholdlist:
            if i == self.gcd:
                standardhold = True

        if self.forceSdrift:
            standardhold = False
        if self.forceTdrift:
            technicalhold = False

        # Auto Information
        nextauto = 1
        self.schedule.addtime(1)
        # Values to keep track and help print updates

        oldpot = 0
        oldfeathers = 0
        oldesprit = 0
        gcd = 0
        feathersused = 0
        flourishedfans = 0
        saberdancess = 0

        self.abilities['Fan Dance I'].nextuse = 1
        self.abilities['Fan Dance III'].nextuse = 1

        if self.prepullpot:
            self.abilities['Potion'].putonCD(self.prepulltime)
            self.buffs['Potion'].activate(self.prepulltime)
            if self.buffs['Potion'].activation < 0:
                string = self.buffs['Potion'].switchon(self.buffs['Potion'].activation)
                self.schedule.addtime(self.buffs['Potion'].endtime + .01)
                if self.createlog:
                    logging.info(string)
            else:
                self.schedule.addtime(self.buffs['Potion'].activation)

        #### Sim Start ###
        delaystart = round(self.fight[delayedpos][0], 2)
        delayend = round(self.fight[delayedpos][1], 2)
        buffdelay = self.fight[delayedpos][2]
        self.schedule.addtime(delaystart)
        self.schedule.addtime(delayend)
        while self.clock < self.length:
            ## Check if we have entered a delay in the fight
            if self.clock == delaystart:
                nextgcd = round(delayend, 2)
                nextaction = round(delayend, 2)
                nextauto = round(delayend, 2)
                for i in self.party.values():
                    i.nextauto = round(delayend, 2)
                delayeddance = round(delayend - 14, 2)
                self.schedule.addtime(nextgcd)
                self.schedule.addtime(nextaction)
                self.schedule.addtime(delayeddance)
                if self.createlog:
                    logging.info(str(self.clock) + ' : Boss has jumped')
                delay = True
                stillinopener = False  # To avoid complications)
                if self.abilities['Technical Step'].nextuse < delayend:
                    self.abilities['Technical Step'].nextuse = round(delayend + 1.5 + self.gcd * 2, 2)
                if self.abilities['Devilment'].nextuse < delayend:
                    self.abilities['Devilment'].nextuse = round(delayend + self.gcd, 2)

            elif self.clock == delayend:
                if self.buffs['Improvisation'].getactive(self.clock):
                    string = self.buffs['Improvisation'].dropbuff(self.clock)
                    if self.createlog:
                        logging.info(string)
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
            potmod = [1.20, 1.05]
            automod = [1.05]
            dex = self.stats[2]
            critrate = self.stats[3]
            critdam = self.stats[4]
            direct = self.stats[5]
            det = self.stats[6]
            sks = self.stats[7]

            devilhold = False

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
                        self.schedule.addtime(round(i.endtime + .01, 2))
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
                        if i.starttime + (i.duration - 2) > delaystart or (
                                delay and i.starttime < delayend) and i.starttime <= delayend + i.default:
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
                        self.schedule.addtime(round(i.endtime + .01, 2))
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
                            direct = round(direct + i.getpotency(self.clock), 2)
                    elif i.available and not i.getactive(self.clock) and i.active:
                        string = i.dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)

            for i in self.buffs.values():
                if i.ready and i.activation == self.clock:
                    string = i.switchon(self.clock)
                    if self.createlog:
                        logging.info(string)
                    self.schedule.addtime(round(i.endtime + .01, 2))
                    self.schedule.addtime(i.starttime)

            if self.buffs['Technical Finish'].getactive(self.clock):
                potmod.append(1.05)
                automod.append(1.05)
            elif self.buffs['Technical Finish'].active:
                string = self.buffs['Technical Finish'].dropbuff(self.clock)
                if self.createlog:
                    logging.info(string)

            if self.buffs['Devilment'].getactive(self.clock):
                critrate = round(critrate + self.buffs['Devilment'].getpotency(self.clock), 2)
                direct = round(direct + self.buffs['Devilment'].getpotency(self.clock), 2)
            elif self.buffs['Devilment'].active:
                string = self.buffs['Devilment'].dropbuff(self.clock)
                if self.createlog:
                    logging.info(string)

            # Other buffs are procs and combos, track them here
            for i in self.buffs.values():
                if i.active and (not i.getactive(self.clock)):
                    if not i.name == 'Combo':
                        if self.createlog:
                            self.procdrop = self.procdrop + 1
                            logging.info(str(self.clock) + ' : You lost the proc ' + i.name)
                    else:
                        self.combodrops = self.combodrops + 1
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You lost a combo')
                    string = i.dropbuff(self.clock)
                    if self.createlog:
                        logging.info(string)

            # Determine if we are in a buff window for logic
            if 'NIN' in self.party.keys() and self.pbuffs['Trick Attack'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            elif self.buffs['Devilment'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            elif self.buffs['Potion'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            elif 'DRG' in self.party.keys() and 'BRD' in self.party.keys() and self.pbuffs['Battle Voice'].getactive(
                    self.clock) and self.pbuffs['Battle Litany'].getactive(self.clock):
                buffwindow = True
                lastbuffwindow = self.clock
            else:
                buffwindow = False

            # Determine future stuff next such as Nextbuffwindow, and standard / Technical times
            foundnextbuffwindow = False
            nextbuffwindow = self.clock
            nextdance = self.clock
            nextdancetype = 'None'
            dancenumber = 0
            standardtimer = 0
            technicaltimer = 0
            actualnextdance = 0  # Because I don't want to change the code, Next dance is sometimes a lie!!!

            standardrecast = round(self.abilities['Standard Step'].getrecast(self.clock), 2)
            technicalrecast = round(self.abilities['Technical Step'].getrecast(self.clock), 2)
            if standardrecast - 15 <= 0:
                nextdancetype = 'Standard'
                nextdance = round(self.clock + standardrecast, 2)
                dancenumber = dancenumber + 1
                standardtimer = round(self.clock + standardrecast, 2)
            if technicalrecast - 15 <= 0:
                nextdancetype = 'Technical'
                nextdance = round(self.clock + technicalrecast, 2)
                dancenumber = dancenumber + 1
                technicaltimer = round(self.clock + standardrecast, 2)
            ## Lots of fun dancing logic used to figure out if I'm dancing soon or not and what dances are coming and when technical is coming
            # Could consolidate this to less code if ever needed, some redundancy here
            if dancenumber > 0:
                if technicaltimer == 0:
                    actualnextdance = standardtimer
                elif standardtimer == 0:
                    actualnextdance = technicaltimer
                elif technicaltimer > standardtimer:
                    actualnextdance = standardtimer
                else:
                    actualnextdance = standardtimer

            nextbuffwindow = 100000000000
            foundnextbuffwindow = False

            if 'NIN' in self.party.keys() and self.pbuffs['Trick Attack'].starttime - self.clock < 15:
                foundnextbuffwindow = True
                nextbuffwindow = self.pbuffs['Trick Attack'].starttime
            elif self.abilities['Devilment'].nextuse - self.clock < 15:
                foundnextbuffwindow = True
                if self.abilities['Devilment'].nextuse < nextbuffwindow:
                    nextbuffwindow = self.abilities['Devilment'].nextuse
            elif 'DRG' in self.party.keys() and 'BRD' in self.party.keys() and self.pbuffs[
                'Battle Voice'].starttime - self.clock < 15:
                foundnextbuffwindow = True
                if self.pbuffs['Battle Voice'].starttime < nextbuffwindow:
                    nextbuffwindow = self.pbuffs['Battle Voice'].starttime
            ## Reset next buff window
            if nextbuffwindow == 100000000000:
                nextbuffwindow = 0
            # Build tables for pass through
            CDHStats = [critrate, critdam, direct, 1.25]
            DMGStats = [self.stats[0], self.stats[1], dex, self.stats[6], self.stats[7]]

            # Handle Esprit
            # Handle party GCDs and Esprit
            for i in self.party.values():
                if i.nextgcd == self.clock:
                    i.nextgcd = round(self.clock + i.gcd, 2)
                    self.schedule.addtime(i.nextgcd)
                    if self.buffs['Technical Finish'].getactive(self.clock):
                        self.buildesprit(i.espritrate)
                    elif i.partner:
                        self.buildesprit(i.espritrate)
            # Handle Auto
            if self.clock == nextauto:
                if not delay:
                    self.buildpotency(self.abilities['Auto Attack'].getpotency(self.clock, CDHStats, automod, DMGStats,
                                                                               self.buffs['Combo'].getactive(
                                                                                   self.clock)))
                nextauto = round(self.clock + self.abilities['Auto Attack'].cooldown, 2)
                self.schedule.addtime(nextauto)
            # Handle Global Tick
            if self.clock == nexttick:
                if self.buffs['Improvisation'].getactive(self.clock):
                    self.esprit = self.esprit + len(self.party) * 3
                    if self.esprit > 100:
                        self.esprit = 100
                        self.buffs['Improvisation'].dropbuff(self.clock)
                nexttick = round(self.clock + 3, 2)
                self.schedule.addtime(nexttick)

            # Handle Delay Actions

            if delay:

                if (delayeddance - self.clock > 10 or (
                        self.abilities['Standard Step'].nextuse > delayend and self.abilities[
                    'Technical Step'].nextuse > delayend)) and self.abilities['Improvisation'].available(
                    self.clock) and not self.buffs['Improvisation'].getactive(
                    self.clock) and not technicaldancing and not standarddancing and self.esprit < 60:
                    if self.createlog:
                        logging.info(str(self.clock) + ' : You begin Improvisation')
                    self.abilities['Improvisation'].putonCD(self.clock)
                    self.buffs['Improvisation'].activate(self.clock)
                    self.schedule.addtime(self.buffs['Improvisation'].activation)
                elif self.abilities['Standard Step'].available(
                        self.clock) and self.clock >= delayeddance and not technicaldancing and not standarddancing:
                    if self.createlog:
                        logging.info(str(self.clock) + ' : You begin Standard Step')
                    nextgcd = round(self.clock + 1.5, 2)
                    self.abilities['Standard Step'].putonCD(self.clock)
                    standarddancing = True
                    stepsneeded = 2

            elif not delay and self.buffs['Improvisation'].getactive(self.clock):
                string = self.buffs['Improvisation'].dropbuff(self.clock)
                if self.createlog:
                    logging.info(string)

            # Let's push the next GCD to technical or standard if its within range
            # Handle Opener if available
            # ---------------------------------------------------------- MAIN SIM---------------------------------------------------------------------------------------------
            if stillinopener:
                if self.action[posinopen].actionable(self.clock):
                    currentaction = self.action[posinopen]
                    if self.action[posinopen].name == 'Technical Finish':
                        self.buildpotency(
                            self.abilities['Technical Finish'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                        self.buffs['Technical Finish'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Technical Finish'].activation)
                        nextgcd = round(self.clock + 1.5, 2)
                        if not saberfirst:
                            technicalfirst = True
                    elif self.action[posinopen].name == 'Standard Finish':
                        self.buildpotency(
                            self.abilities['Standard Finish'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                        nextgcd = round(self.clock + 1.5, 2)
                        if self.abilities['Standard Step'].available(self.clock):
                            self.abilities['Standard Step'].putonCD(round(0 - 14.7, 2))
                    elif self.action[posinopen].name == 'Devilment':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use Devilment!')
                        if not technicalfirst:
                            saberfirst = True
                        self.buffs['Devilment'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Devilment'].activation)
                        self.abilities['Devilment'].putonCD(self.clock)
                    elif self.action[posinopen].name == 'Flourish':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use Flourish!')
                        self.buffs['Flourishing Cascade'].activate(self.clock)
                        self.buffs['Flourishing Windmill'].activate(self.clock)
                        self.buffs['Flourishing Fountain'].activate(self.clock)
                        self.buffs['Flourishing Bladeshower'].activate(self.clock)
                        self.buffs['Flourishing Fan'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)
                        self.abilities['Flourish'].putonCD(self.clock)
                    elif currentaction.name == 'Potion':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use a Potion!')
                        self.abilities['Potion'].putonCD(self.clock)
                        self.buffs['Potion'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Potion'].activation)
                    elif currentaction.name == 'ReverseProc' and self.buffs['Flourishing Cascade'].getactive(
                            self.clock):
                        self.buildpotency(
                            self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                        gcd = gcd + 1
                        string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.getfeathers()
                        self.buildesprit(self.clock, self.rate)
                        nextgcd = round(self.clock + self.gcd, 2)
                    elif currentaction.name == 'AutoGCD' or currentaction.name == 'ReverseProc':
                        # Auto GCD in the self.action
                        # If technical is active and Esprit > 80 - Use Saber Dance
                        # If we are to lose any procs do them in the following order Fountfall > Cascade > self.abilities['Bloodshower'] > windmill
                        # If we are in a buffwindo and esprit is great than or equal to 50 then use Saber Dance
                        # If we are in a combo and self.buffs['Flourishing Fountain'] is not active and our combo will drop - Use Fountain
                        # Use Flourishes in this order : Fountainfall >  Reverse Cascade > Blood > Rising
                        # If esprit is 90 or above use Saber Dance
                        # If combo use Fountain
                        # Else use Cascade
                        proccount = self.countprocs()
                        procgcd = proccount * self.gcd
                        nextgcd = round(self.clock + self.gcd, 2)
                        if self.buffs['Technical Finish'].getactive(
                                self.clock) and self.esprit > 80:  # If we Technical is out and we have 90+ Esprit, Go now
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                            gcd = gcd + 1
                        elif self.buffs['Flourishing Fountain'].getactive(
                                self.clock):  # Check to see if Flourish Fountain is close to dropping
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Cascade'].getactive(
                                self.clock):  # Check if Reverse Cascade is close to dropping
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Bladeshower'].getactive(
                                self.clock):  # Check if Bloodshower is close to fall
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Windmill'].getactive(
                                self.clock):  # Check if Windmill is close to fall
                            self.buildpotency(
                                self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Technical Finish'].getactive(
                                self.clock) and self.esprit >= 50:  # I want to use self.abilities['Saber Dance'] in the buff window
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                        elif self.buffs['Combo'].getactive(self.clock) and not self.buffs[
                            'Flourishing Fountain'].getactive(self.clock) and self.buffs['Combo'].closetodrop(
                                self.clock,
                                self.gcd):  # First We check to see if we are in combo and don't have Flourished Fountain
                            self.buildpotency(
                                self.abilities['Fountain'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                      self.buffs['Combo'].getactive(self.clock)))
                            self.buffs['Combo'].dropbuff(self.clock)
                            usedfountain = True
                            gcd = gcd + 1
                            if self.checkproc():
                                self.buffs['Flourishing Fountain'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                        elif self.buffs['Flourishing Fountain'].getactive(
                                self.clock):  # Check to see if Flourish Fountain is up
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Cascade'].getactive(self.clock):  # Check if Reverse Cascade is up
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Bladeshower'].getactive(self.clock):  # Check if Bloodshower is up
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                        elif self.buffs['Flourishing Windmill'].getactive(self.clock):  # Check if Windmill is up
                            self.buildpotency(
                                self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.esprit > 80:
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                        elif self.buffs['Combo'].getactive(
                                self.clock):  # If we are in combo we are doing self.abilities['Fountain'] here
                            self.buildpotency(
                                self.abilities['Fountain'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                      self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            usedfountain = True
                            self.buffs['Combo'].dropbuff(self.clock)
                            if self.checkproc():
                                self.buffs['Flourishing Fountain'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                        else:  # If all else fails we go into Cascade combo
                            self.buildpotency(
                                self.abilities['Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.buffs['Combo'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Combo'].activation)
                            if self.checkproc():
                                self.buffs['Flourishing Cascade'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)
                        self.buildesprit(self.rate)  # Check if we get Esprit from this GCD
                    elif currentaction.name == 'AutoOGCD':
                        # AutoOGCD in the self.action
                        # If self.abilities['Flourish'] is up, we have no procs - Use it
                        # If self.abilities['Flourish'] fan is up use FD3
                        # if we are in the buffwindow and have feathers and can use FD1 use FD1
                        # If we have 4 feathers and FD1 is up use FD1
                        # push the oGCD further if we have more feathers. at a 2.4 gcd we can get two in
                        if self.abilities['Flourish'].available(self.clock) and self.countprocs() == 0 and not \
                        self.buffs['Flourishing Fan'].getactive(
                                self.clock):
                            if self.createlog:
                                logging.info(str(self.clock) + ' : You use Flourish!')
                            self.buffs['Flourishing Cascade'].activate(self.clock)
                            self.buffs['Flourishing Windmill'].activate(self.clock)
                            self.buffs['Flourishing Fountain'].activate(self.clock)
                            self.buffs['Flourishing Bladeshower'].activate(self.clock)
                            self.buffs['Flourishing Fan'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)
                            self.abilities['Flourish'].putonCD(self.clock)
                        elif self.buffs['Flourishing Fan'].getactive(self.clock) and self.abilities[
                            'Fan Dance III'].available(self.clock):
                            self.buildpotency(
                                self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                           self.buffs['Combo'].getactive(self.clock)))
                            flourishedfans = flourishedfans + 1
                            string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif buffwindow and self.feathers > 0 and self.abilities['Fan Dance I'].available(self.clock):
                            self.buildpotency(
                                self.abilities['Fan Dance I'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            self.feathers = self.feathers - 1
                            feathersused = feathersused + 1
                            if self.checkproc():
                                self.buffs['Flourishing Fan'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fan'].activation)
                        elif self.feathers > 3 and self.abilities['Fan Dance I'].available(self.clock):
                            self.buildpotency(
                                self.abilities['Fan Dance I'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            feathersused = feathersused + 1
                            self.feathers = self.feathers - 1
                            if self.checkproc():
                                self.buffs['Flourishing Fan'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fan'].activation)
                        elif self.abilities['Fan Dance I'].nextuse + .7 <= nextgcd and self.feathers > 0:
                            currentaction.actiontime = round(self.abilities['Fan Dance I'].nextuse, 2)
                            self.schedule.addtime(self.abilities['Fan Dance I'].nextuse)
                            posinopen = posinopen - 1
                    elif currentaction.name == 'Hold':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : Waiting')
                    elif currentaction.name == 'Technical Step':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You begin Technical Step')
                        if not saberfirst:
                            technicalfirst = True
                        self.abilities[currentaction.name].putonCD(self.clock)
                    elif currentaction.name == 'Standard Step':
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You begin Standard Step')
                        self.abilities['Standard Step'].putonCD(self.clock)
                    elif currentaction.name == 'Fountain':
                        self.buildpotency(self.abilities['Fountain'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                self.buffs['Combo'].getactive(
                                                                                    self.clock)))
                        gcd = gcd + 1
                        usedfountain = True
                        self.buffs['Combo'].dropbuff(self.clock)
                        if self.checkproc():
                            self.buffs['Flourishing Fountain'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                        self.buildesprit(self.rate)
                    elif currentaction.name == 'Cascade':
                        self.buildpotency(self.abilities['Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                               self.buffs['Combo'].getactive(
                                                                                   self.clock)))
                        gcd = gcd + 1
                        self.buffs['Combo'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Combo'].activation)
                        if self.checkproc():
                            self.buffs['Flourishing Cascade'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)
                        self.buildesprit(self.rate)
                    elif currentaction.name == 'Fan Dance I':
                        if self.feathers > 0:
                            self.buildpotency(
                                self.abilities['Fan Dance I'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            feathersused = feathersused + 1
                            self.feathers = self.feathers - 1
                        if self.checkproc():
                            self.buffs['Flourishing Fountain'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                    elif currentaction.name == 'Fan Dance III':
                        if self.buffs['Flourishing Fan'].getactive(self.clock):
                            self.buildpotency(
                                self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                           self.buffs['Combo'].getactive(self.clock)))
                            flourishedfans = flourishedfans + 1
                            string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                    elif currentaction.name == 'Fountainfall':
                        self.buildpotency(
                            self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                      self.buffs['Combo'].getactive(self.clock)))
                        gcd = gcd + 1
                        string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.buildesprit(self.rate)
                        self.getfeathers()
                        nextgcd = round(self.clock + self.gcd, 2)
                    elif currentaction.name == 'Reverse Cascade':
                        self.buildpotency(
                            self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                        gcd = gcd + 1
                        string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.buildesprit(self.rate)
                        self.getfeathers()
                        nextgcd = round(self.clock + self.gcd, 2)
                    elif currentaction.name == 'Bloodshower':
                        self.buildpotency(
                            self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                        gcd = gcd + 1
                        string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.buildesprit(self.rate)
                        self.getfeathers()
                        nextgcd = round(self.clock + self.gcd, 2)
                    elif currentaction.name == 'Rising Windmill':
                        self.buildpotency(
                            self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                        gcd = gcd + 1
                        string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        self.buildesprit(self.rate)
                        self.getfeathers()
                        nextgcd = round(self.clock + self.gcd, 2)
                    elif currentaction.name == 'Step':
                        nextgcd = round(self.clock + 1, 2)
                    elif currentaction.name == 'Standard Step':
                        nextgcd = round(self.clock + 1.5, 2)
                    elif currentaction.name == 'Technical Step':
                        nextgcd = round(self.clock + 1.5, 2)
                    posinopen = posinopen + 1
                    if posinopen >= len(self.action):
                        if self.createlog:
                            logging.info('Finished with self.action, commencing Sim')
                        # Let's figure out when our last GCD was
                        foundlastGCD = False
                        foundlastaction = False
                        while (not foundlastGCD):
                            currentaction = self.action[posinopen - 1]
                            if currentaction.name.split()[0] == 'Technical' or currentaction.name.split()[
                                0] == 'Standard':
                                if not foundlastaction:
                                    foundlastaction = True
                                    nextaction = round(self.clock + self.abilitydelay, 2)
                                if currentaction.name.split()[1] == 'Finish':
                                    foundlastGCD = True
                                    nextgcd = round(self.clock + 1.5, 2)
                            elif currentaction.name == 'AutoGCD' or self.abilities[
                                currentaction.name].abiltype == 'GCD':
                                if not foundlastaction:
                                    foundlastaction = True
                                    nextaction = round(self.clock + self.abilitydelay, 2)
                                foundlastGCD = True
                                nextgcd = round(self.clock + self.gcd, 2)
                            elif currentaction.name == 'AutoOGCD' or self.abilities[
                                currentaction.name].abiltype == 'OGCD':
                                if not foundlastaction:
                                    foundlastaction = True
                                    nextaction = round(self.clock + self.abilitydelay, 2)
                            posinopen = posinopen - 1
                        stillinopener = False
            else:
                # GCD Priority List -
                # First we check if we are dancing and finish the dance
                # We check the status on technical, If we used Saber first in our opener we also check to see if Devilment is up. We also check to make there is no boss jump/delay in the 22 seconds Then we use Technical
                # If Technical is up and we have 80 or more Esprit - Use Saber
                # Check if Standard Step is up and there is no boss jump/delay in 5 seconds - If so use it
                # If we have 50 Esprit. improv is up and the boss is jumping within the next GCD we want to dump Esprit into Saber Dance
                # If we don't have a ninja in our group and we aren't using Technical step in 30s and we have no procs but flourish will be of CD within the next GCD and we have enough esprit - Use Saber
                # next we check if 1 or more dances are coming and one is next GCD and if we have Flourishing Fountain - Use Flourish Fountain
                # next we check if 1 or more dances are coming and one is next GCD and if we have Flourishing Cascade - Use Flourish Cascade
                # If we have Flourishing Fountain and we will lose a the proc next GCD - Use Fountainfall
                # If we have Flourishing Cascade and we will lose a the proc next - Use Reverse Cascade
                # next we check if we are in combo and the combo is about to drop and we don't have Flourish Fountain - Use Fountain
                # If Flourisng Cascade is up and we will lose any Flourish  proc if we don't use one - Use Reverse Cascade
                # If Flourishing Bladeshower is up and we will lose any Flourish proc if we don't use one - Use Bloodshower
                # If we are in a buffwindow and esprit equal or greater than 50 - Use Saber Dance
                # If Flourishing up and we will lose any Flourish proc if we don't use one - Use Rising Windmill
                # Use Saber if Esprit is at 80 or above
                # If we are in a buffwindow and Flourishing Fountain is up - Use Fountainfall
                # If we are in a buffwindow and Flourising Cascade is up - Use Reverse Cascade
                # If we are in a buff window and Flourishing Bladeshower is up - Use Blood Shower
                # If we are in a buff window and Flourishing Windmill is up - Use Rising Windmill
                # If Flourishing Windmill is up - Use Risingmill
                # if Flourishing Blade Shower - Use Bloodshower
                # if Flourishing Cascade - Use Reverse Cascade
                # if Flourishing Fountain - Use Fountainfall
                # If we are in a combo use Fountain
                #  Else Use Cascade

                if nextgcd == self.clock:
                    if standarddancing or technicaldancing:
                        if stepsneeded > 0:
                            if self.createlog:
                                logging.info(str(self.clock) + ' : You use a Step')
                            stepsneeded = stepsneeded - 1
                            nextgcd = round(self.clock + 1, 2)
                        elif not delay:
                            if technicaldancing:
                                self.buildpotency(
                                    self.abilities['Technical Finish'].getpotency(self.clock, CDHStats, potmod,
                                                                                  DMGStats,
                                                                                  self.buffs['Combo'].getactive(
                                                                                      self.clock)))
                                technicaldancing = False
                                self.buffs['Technical Finish'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Technical Finish'].activation)
                            else:
                                self.buildpotency(
                                    self.abilities['Standard Finish'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                                 self.buffs['Combo'].getactive(
                                                                                     self.clock)))
                                standarddancing = False
                            nextgcd = round(self.clock + 1.5, 2)
                            nextaction = round(self.clock + self.abilitydelay, 2)
                        else:
                            if delayend - self.clock > 1.5:
                                nextgcd = round(delayend, 2)
                                nextaction = round(delayend, 2)
                            else:
                                nextgcd = round(self.clock + 1.5, 2)
                                nextaction = round(self.clock + 1.5, 2)
                    elif self.abilities['Technical Step'].available(self.clock) and (
                            (saberfirst and self.buffs['Devilment'].getactive(
                                self.clock)) or technicalfirst) and delaystart - self.clock > 22:
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You begin Technical Step')
                        nextgcd = round(self.clock + 1.5, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        self.abilities['Technical Step'].putonCD(self.clock)
                        technicaldancing = True
                        stepsneeded = 4
                    elif self.buffs['Technical Finish'].getactive(self.clock) and self.esprit >= 80:
                        self.buildpotency(
                            self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                        saberdancess = saberdancess + 1
                        gcd = gcd + 1
                        self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                        self.buildesprit(self.rate)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                    elif self.abilities['Standard Step'].available(
                            self.clock) and self.abilities[
                        'Technical Step'].nextuse > self.clock + 6.5 and delaystart - self.clock > 5:
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You begin Standard Step')
                        nextgcd = round(self.clock + 1.5, 2)
                        self.abilities['Standard Step'].putonCD(self.clock)
                        standarddancing = True
                        stepsneeded = 2
                    else:
                        proccount = self.countprocs()
                        procgcd = proccount * self.gcd
                        self.buildesprit(self.rate)
                        nextgcd = round(self.clock + self.gcd, 2)
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        if self.esprit > 40 and delayend - delaystart > 20 and delaystart < self.clock + self.gcd and \
                                self.abilities['Improvisation'].available(
                                        self.clock):
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                            self.buildesprit(self.rate)
                        elif self.esprit > 49 and not 'NIN' in self.party.keys() and self.abilities[
                            'Flourish'].available(nextgcd) and self.countprocs() == 0 and self.abilities[
                            'Technical Step'].getrecast(self.clock) > 30:
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                            self.buildesprit(self.rate)
                        elif (dancenumber >= 1 and self.buffs['Flourishing Fountain'].getactive(
                                self.clock) and actualnextdance <= nextgcd) or (
                                self.buffs['Flourishing Fountain'].getactive(
                                    self.clock) and nextdancetype == 'Technical' and actualnextdance <= nextgcd and
                                self.buffs['Flourishing Fountain'].returnduration(
                                    self.clock) < self.gcd + 7):
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif (dancenumber >= 1 and self.buffs['Flourishing Cascade'].getactive(
                                self.clock) and actualnextdance <= nextgcd) or (
                                self.buffs['Flourishing Cascade'].getactive(
                                    self.clock) and nextdancetype == 'Technical' and actualnextdance <= nextgcd and
                                self.buffs['Flourishing Cascade'].returnduration(
                                    self.clock) < self.gcd + 7):
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Fountain'].getactive(self.clock) and self.buffs[
                            'Flourishing Fountain'].closetodrop(self.clock,
                                                                self.gcd):  # Check to see if Flourish Fountain is close to dropping
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Bladeshower'].getactive(self.clock) and self.buffs[
                            'Flourishing Bladeshower'].closetodrop(self.clock,
                                                               self.gcd):  # Check if Reverse Cascade is close to dropping
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Cascade'].getactive(self.clock) and self.buffs[
                            'Flourishing Fountain'].getactive(
                                self.clock) and dancenumber > 0 and foundnextbuffwindow:
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Combo'].getactive(self.clock) and not self.buffs[
                            'Flourishing Fountain'].getactive(self.clock) and self.buffs['Combo'].closetodrop(
                                self.clock,
                                self.gcd):  # First We check to see if we are in combo and don't have Flourished Fountain
                            self.buildpotency(
                                self.abilities['Fountain'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                      self.buffs['Combo'].getactive(self.clock)))
                            usedfountain = True
                            string = self.buffs['Combo'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            gcd = gcd + 1
                            if self.checkproc():
                                self.buffs['Flourishing Fountain'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                        elif self.buffs['Flourishing Bladeshower'].getactive(self.clock) and self.buffs[
                            'Flourishing Bladeshower'].closetodrop(self.clock,
                                                                   procgcd):  # Check if Bloodshower is close to fall
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Cascade'].getactive(self.clock) and self.buffs[
                            'Flourishing Cascade'].closetodrop(self.clock,
                                                               procgcd):  # Check if Bloodshower is close to fall
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Windmill'].getactive(self.clock) and self.buffs[
                            'Flourishing Windmill'].closetodrop(self.clock,
                                                                procgcd):  # Check if Windmill is close to fall
                            self.buildpotency(
                                self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif buffwindow and self.esprit >= 50:  # I want to use self.abilities['Saber Dance'] in the buff window
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                            self.buildesprit(self.rate)
                        elif self.esprit > 80:
                            self.buildpotency(
                                self.abilities['Saber Dance'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            saberdancess = saberdancess + 1
                            gcd = gcd + 1
                            self.esprit = self.esprit - self.abilities['Saber Dance'].cost
                            self.buildesprit(self.rate)

                        elif buffwindow and self.buffs['Flourishing Fountain'].getactive(
                                self.clock):  # Check to see if Flourish Fountain is up
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif buffwindow and self.buffs['Flourishing Bladeshower'].getactive(
                                self.clock):  # Check if Bloodshower is up
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif buffwindow and self.buffs['Flourishing Cascade'].getactive(
                                self.clock):  # Check if Reverse Cascade is up
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif buffwindow and self.buffs['Flourishing Windmill'].getactive(
                                self.clock):  # Check if Windmill is up
                            self.buildpotency(
                                self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Windmill'].getactive(self.clock):  # Check if Windmill is up
                            self.buildpotency(
                                self.abilities['Rising Windmill'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Windmill'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Bladeshower'].getactive(self.clock):  # Check if Bloodshower is up
                            self.buildpotency(
                                self.abilities['Bloodshower'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                         self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.getfeathers()
                            string = self.buffs['Flourishing Bladeshower'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                        elif self.buffs['Flourishing Cascade'].getactive(self.clock):  # Check if Reverse Cascade is up
                            self.buildpotency(
                                self.abilities['Reverse Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                             self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Cascade'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Flourishing Fountain'].getactive(
                                self.clock):  # Check to see if Flourish Fountain is up
                            self.buildpotency(
                                self.abilities['Fountainfall'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                          self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            string = self.buffs['Flourishing Fountain'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            self.getfeathers()
                        elif self.buffs['Combo'].getactive(
                                self.clock):  # If we are in combo we are doing self.abilities['Fountain'] here
                            self.buildpotency(
                                self.abilities['Fountain'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                      self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            usedfountain = True
                            string = self.buffs['Combo'].dropbuff(self.clock)
                            if self.createlog:
                                logging.info(string)
                            if self.checkproc():
                                self.buffs['Flourishing Fountain'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Fountain'].activation)
                        else:  # If all else fails we go into Cascade combo
                            self.buildpotency(
                                self.abilities['Cascade'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                            gcd = gcd + 1
                            self.buffs['Combo'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Combo'].activation)
                            if self.checkproc():
                                self.buffs['Flourishing Cascade'].activate(self.clock)
                                self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)

                    if technicalhold and self.abilities['Technical Step'].nextuse < round(nextgcd + self.gcd,
                                                                                          2) and not (self.abilities[
                                                                                                          'Technical Step'].nextuse == nextgcd) and not standarddancing and delaystart - \
                            self.abilities['Technical Step'].nextuse > 22:  #
                        if not nextgcd > round(self.abilities['Technical Step'].nextuse, 2):
                            nextgcd = round(self.abilities['Technical Step'].nextuse, 2)

                    elif standardhold and self.abilities['Standard Step'].nextuse < round(nextgcd + self.gcd, 2) and (
                            self.abilities['Technical Step'].nextuse - nextgcd) > (
                            6.5 + self.gcd) and not technicaldancing and not round(
                            self.abilities['Standard Step'].nextuse, 2) == nextgcd and delaystart - self.abilities[
                        'Standard Step'].nextuse > 5.2:
                        if not nextgcd > round(self.abilities['Standard Step'].nextuse, 2):
                            nextgcd = round(self.abilities['Standard Step'].nextuse, 2)
                    #             # If anything changes, post an updated
                elif nextaction == self.clock:
                    # oGCD Priority list
                    # Ignore oGCDs if dancing
                    # If Devilment is ready, and technical is the next GCD or we opened with Technical first and we are in the second oGCD slot - Use Saber
                    # If Saber is ready and technical is the next GCD or we opened with Technical first and our next GCD is greater than 1.5 away, close the ogcd slot to ensure saber gets second slot
                    # if Devilment is ready, our opener used Saber First and self.abilities['Technical Step'] is the next gcd and nextgcd is 1.7 away, wait. To ensure second oGCD slot
                    # if self.abilities['Flourish'] is available, we have 0 self.abilities['Flourish'] procs, and technical dance isn't less than 4* our Current GCD seconds away and we aren't dancing twice in the next 15, and we aren't in a buff window with 50 or more Esprit - use self.abilities['Flourish']
                    # if our potion is ready and the next Devilment is less than 15 seconds away - use potion
                    # if we have a flourished fan and are double dancing in the next 15 seconds or self.abilities['Flourish'] is up, use Fan Dance III
                    # if we have a flourished fan and the fan is close to dropping, use Fan Dance III
                    # If we have a flourished fan and the next buff window is more than 13.5 seconds away, use Fan Dance III
                    # if we have a flourished fan and we have 4 feathers, use Fan Dance III
                    # If we are in a buffwindow and have a flourished fan, use Fan Dance III
                    # If we are in a buffwindow and have feathers use Fan Dance I
                    # IF we have 4 feathers and some other self.abilities['Flourish'] proc - Use Fan Dance I
                    abilityused = False
                    if technicaldancing or standarddancing:
                        abilityused = False
                    elif self.abilities['Devilment'].available(self.clock) and not saberfirst:
                        if self.createlog:
                            logging.info(str(self.clock) + " : You use Devilment!")
                        self.buffs['Devilment'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Devilment'].activation)
                        self.abilities['Devilment'].putonCD(self.clock)
                        abilityused = True
                        devilhold = False
                    elif self.abilities['Devilment'].available(self.clock) and round(nextgcd - self.abilitydelay,
                                                                                     2) <= self.clock and \
                            self.abilities['Technical Step'].nextuse <= nextgcd:
                        if self.createlog:
                            logging.info(str(self.clock) + " : You use Devilment!")
                        self.buffs['Devilment'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Devilment'].activation)
                        self.abilities['Devilment'].putonCD(self.clock)
                        abilityused = True
                        devilhold = False
                        nextaction = round(self.abilities['Technical Step'].nextuse, 2)
                    elif saberfirst and self.abilities['Devilment'].available(round(nextgcd - self.abilitydelay, 2)) and \
                            self.abilities[
                                'Technical Step'].nextuse <= nextgcd:  # Wait for Second oGCD window for Devilment
                        abilityused = False
                        devilhold = True
                        nextaction = round(nextgcd - self.abilitydelay, 2)
                    elif self.abilities['Devilment'].available(
                            round(self.clock + self.abilitydelay, 2)) and technicalhold and self.abilities[
                        'Technical Step'] == nextgcd:
                        nextaction = round(nextgcd - 1, 2)
                    elif self.abilities['Flourish'].available(self.clock) and (self.countprocs() == 0) and not (
                            self.buffs['Flourishing Fan'].getactive(self.clock)) and not (
                            nextdancetype == 'Technical' and round(nextgcd + (self.gcd * 4),
                                                                   2) > nextdance) and dancenumber < 2 and not (
                            buffwindow and self.esprit >= 50):
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use Flourish!')
                        self.buffs['Flourishing Cascade'].activate(self.clock)
                        self.buffs['Flourishing Bladeshower'].activate(self.clock)
                        self.buffs['Flourishing Windmill'].activate(self.clock)
                        self.buffs['Flourishing Fountain'].activate(self.clock)
                        self.buffs['Flourishing Fan'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Flourishing Cascade'].activation)
                        self.abilities['Flourish'].putonCD(self.clock)
                        abilityused = True
                    elif self.potion and self.abilities['Potion'].available(self.clock) and (
                            nextgcd - nextaction) > 1.5 and (
                            self.abilities['Devilment'].getrecast(self.clock) < 15):
                        if self.createlog:
                            logging.info(str(self.clock) + ' : You use a potion!')
                        self.buffs['Potion'].activate(self.clock)
                        self.schedule.addtime(self.buffs['Potion'].activation)
                        self.abilities['Potion'].putonCD(self.clock)
                        nextaction = round(self.clock + .7, 2)
                        abilityused = True
                    elif self.buffs['Flourishing Fan'].getactive(self.clock) and self.abilities[
                        'Fan Dance III'].available(self.clock) and (
                            dancenumber > 0 or self.abilities['Flourish'].available(
                        self.clock)):  # Use it right away so we don't risk losing proc
                        self.buildpotency(
                            self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                       self.buffs['Combo'].getactive(self.clock)))
                        flourishedfans = flourishedfans + 1
                        string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        abilityused = True
                    elif self.buffs['Flourishing Fan'].getactive(self.clock) and self.abilities[
                        'Fan Dance III'].available(self.clock) and self.buffs['Flourishing Fan'].closetodrop(
                            self.clock, self.gcd):  # Use it if it drops in a GCD
                        self.buildpotency(
                            self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                       self.buffs['Combo'].getactive(self.clock)))
                        flourishedfans = flourishedfans + 1
                        string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        abilityused = True
                    elif self.buffs['Flourishing Fan'].getactive(self.clock) and self.abilities[
                        'Fan Dance III'].available(
                            self.clock) and nextbuffwindow > 13.5:  # Use it if there isn't a buff window coming
                        self.buildpotency(
                            self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                       self.buffs['Combo'].getactive(self.clock)))
                        flourishedfans = flourishedfans + 1
                        string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        abilityused = True
                    elif self.buffs['Flourishing Fan'].getactive(
                            self.clock) and self.feathers > 3:  # Use it if we have 4 feathers
                        self.buildpotency(
                            self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                       self.buffs['Combo'].getactive(self.clock)))
                        flourishedfans = flourishedfans + 1
                        string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        abilityused = True
                    elif buffwindow and self.buffs['Flourishing Fan'].getactive(self.clock):
                        self.buildpotency(
                            self.abilities['Fan Dance III'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                       self.buffs['Combo'].getactive(self.clock)))
                        flourishedfans = flourishedfans + 1
                        string = self.buffs['Flourishing Fan'].dropbuff(self.clock)
                        if self.createlog:
                            logging.info(string)
                        abilityused = True
                    elif buffwindow and self.feathers > 0 and self.abilities['Fan Dance I'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Fan Dance I'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                        feathersused = feathersused + 1
                        self.feathers = self.feathers - 1
                        abilityused = True
                        if self.checkproc():
                            self.buffs['Flourishing Fan'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Fan'].activation)
                    elif self.feathers > 3 and not (self.buffs['Flourishing Fan'].getactive(self.clock)) and \
                            self.abilities['Fan Dance I'].available(self.clock):
                        self.buildpotency(
                            self.abilities['Fan Dance I'].getpotency(self.clock, CDHStats, potmod, DMGStats,
                                                                     self.buffs['Combo'].getactive(self.clock)))
                        feathersused = feathersused + 1
                        self.feathers = self.feathers - 1
                        abilityused = True
                        if self.checkproc():
                            self.buffs['Flourishing Fan'].activate(self.clock)
                            self.schedule.addtime(self.buffs['Flourishing Fan'].activation)
                    if abilityused:  # Process new action time
                        nextaction = round(self.clock + self.abilitydelay, 2)
                        if nextaction + self.abilitydelay > nextgcd and not self.abilities['Devilment'].available(
                                nextgcd):
                            nextaction = round(nextgcd, 2)  # I want to avoid clipping
                    elif not devilhold:
                        if not (technicaldancing or standarddancing) and saberfirst and technicalhold and \
                                self.abilities['Devilment'].nextuse < nextgcd:
                            nextaction = round(self.abilities['Devilment'].nextuse, 2)
                        elif not (technicaldancing or standarddancing) and self.abilities[
                            'Flourish'].nextuse < nextgcd - self.abilitydelay and (self.countprocs() == 0) and not (
                        self.buffs['Flourishing Fan'].getactive(self.clock)) and not (
                                nextdancetype == 'Technical' and round(nextgcd + (self.gcd * 4),
                                                                       2) > nextdance) and dancenumber < 2 and not (
                                buffwindow and self.esprit >= 50):
                            nextaction = round(self.abilities['Flourish'].nextuse, 2)
                        elif not (technicaldancing or standarddancing) and self.abilities[
                            'Potion'].nextuse < nextgcd - 1.5 and self.abilities['Devilment'].getrecast(
                                self.clock) < 15:
                            nextaction = round(self.abilities['Potion'].nextuse, 2)
                        elif not (technicaldancing or standarddancing) and buffwindow and self.feathers > 0 and \
                                self.abilities['Fan Dance I'].nextuse <= round(nextgcd - self.abilitydelay, 2) and not (
                                self.buffs['Flourishing Fan'].getactive(self.clock) or self.buffs[
                            'Flourishing Fan'].activation > self.clock):
                            nextaction = round(self.abilities['Fan Dance I'].nextuse, 2)
                        else:
                            nextaction = round(nextgcd, 2)
                        if nextaction + self.abilitydelay > nextgcd and not self.abilities['Devilment'].available(
                                nextgcd):
                            nextaction = round(nextgcd, 2)  # I want to avoid clipping
                        # Define the times we will want to act next
                        # 1. When FD1 is back up and we will not CLIP
                        # 2. If Flourish comes back within the next GCD and we want to use it
                        # 3. IF potion comes back within the next GCD and we want to use it

                # check to see if its within any GCD use at my current self.clock position
                # check to make sure its not happening in the next GCD
                # make sure I'm not dancing
                # make sure its a technical hold
                # check if the delay start time - its next use is greater than 22 before enforcing the hold
                # Make sure I have enough time to Devilment? How do I check that
            if self.gettimetable and self.clock == self.viewtime:
                if self.clock > 0:
                    self.timetable.append(self.potency / self.clock)
                else:
                    self.timetable.append(self.potency)
                self.viewtime = self.viewtime + 1
            if (oldpot != self.potency) or (oldesprit != self.esprit) or (oldfeathers != self.feathers):
                if self.createlog:
                    logging.info(str(self.clock) + ' : Potency: ' + str(round(self.potency, 1)) + ' ' + str(
                        potmod) + ' || Feathers: ' + str(
                        self.feathers) + ' || Esprit: ' + str(self.esprit) + ' || Crit Rate: ' + str(
                        CDHStats[0]) + ' || DH Rate: ' + str(CDHStats[2]))
                oldpot = self.potency
                oldesprit = self.esprit
                oldfeathers = self.feathers
            # Advance self.clock
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
            logging.info("Feathers Remaining: " + str(self.feathers))
            logging.info("Esprit Remaining: " + str(self.esprit))
            logging.info("GCDs Used: " + str(gcd))
            logging.info("Feathers used: " + str(feathersused))
            logging.info("Flourished Fans: " + str(flourishedfans))
            logging.info("Saber Dances Used: " + str(saberdancess))
            logging.info('Combos Dropped: ' + str(self.combodrops))
            logging.info('Flourish Procs Dropped : ' + str(self.procdrop))
            logging.info('Feathers Dropped : ' + str(self.feathersdropped))
            logging.info('Esprit Cap : ' + str(self.espritcap))

        # print(gcd)
        totalesprit = saberdancess * 50 + self.esprit
        return round(self.potency / self.length, 4)








