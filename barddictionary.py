from ability import ability
from buff import buff
from card import card
from job import job
from dot import dot

def genabil(wepdelay, GCDrecast):

    autoattack = ability('Auto Attack', 'Auto', 'ST', wepdelay, 100, 0, 0)
    burst = ability('Burst Shot','GCD','ST',GCDrecast,230,0,0)
    ra = ability('Refulgent Arrow', 'GCD', 'ST', GCDrecast, 360, 0, 0)
    ij = ability('Iron Jaws', 'GCD', 'ST', GCDrecast, 100, 0, 0)
    cb = ability('Caustic Bite', 'GCD', 'ST', GCDrecast, 150, 0, 0)
    sb = ability('Stormbite', 'GCD', 'ST', GCDrecast, 100, 0, 0)
    apex = ability('Apex Arrow', 'GCD', 'ST', GCDrecast, 230, 0, 0)

    bl = ability('Bloodletter', 'oGCD', 'ST', 15, 150, 0, 0)
    pp = ability('Pitch Perfect', 'GCD', 'ST', 3, 100, 0, 0)
    sw = ability('Sidewinder', 'GCD', 'ST', 60, 260, 0, 0)
    ea = ability('Empyreal Arrow', 'oGCD', 'ST', 15, 230, 0, 0)

    wm = ability('Minuet', 'oGCD', 'ST', 80, 100, 0, 0)
    mb = ability('Ballad', 'oGCD', 'ST', 80, 100, 0, 0)
    ap = ability('Paeon', 'oGCD', 'ST', 80, 100, 0, 0)

    rs = ability('Raging Strikes', 'oGCD', 'ST', 80, 230, 0, 0)
    ba = ability('Barrage', 'oGCD', 'ST', 80, 230, 0, 0)
    bv = ability('Battle Voice', 'oGCD', 'ST', 180, 230, 0, 0)


    potion = ability('Potion', 'OGCD', 'ST', 270, 0, 0, 0)

    table = [autoattack,burst,ra,ij,cb,sb,apex,bl,pp,sw,ea,wm,mb,ap,rs,ba,bv,potion]

    dict = {}
    for i in table:
        dict[i.name]=i

    return dict

def gendots():
    cb = dot('Caustic Bite', 50, 30)
    sb = dot('Stormbite', 60, 30)

    table = [cb,sb]

    dict = {}
    for i in table:
        dict[i.name] = i

    return dict

def genast():

    redraw = ability('Redraw', 'OGCD', 'ST', 30, 0, 0, 0)
    redraw.charged = True
    redraw.charges = 3
    redraw.maxcooldown = 3 * 30

    draw = ability('Draw', 'OGCD', 'ST', 30, 0, 0, 0)
    sleeve = ability('Sleeve Draw', 'OGCD', 'ST', 180, 0, 0, 0)
    div = ability('Divination', 'OGCD', 'AoE', 180, 0, 0, 0)

    abilities = [redraw,draw,sleeve,div]
    abildict = {}
    for i in abilities:
        abildict[i.name] = i

    balance = card('Balance', 'Solar', False)
    bole = card('Bole', 'Solar', True)
    arrow = card('Arrow', 'Lunar', False)
    ewer = card('Ewer', 'Lunar', True)
    spear = card('Spear', 'Celestial', False)
    spire = card('Spire', 'Celestial', True)

    deck = [balance, bole, arrow, ewer, spear, spire ]

    goodcard = buff('Bole', 15, 0, 1.06, 0, 'pot')
    badcard = buff('Balance', 15, 0, 1.03, 0, 'pot')
    notmycard = buff('Not My Card', 15, 0, 1.00, 0, 'None')
    bigcard = buff('Lady', 15, 0, 1.08, 0, 'pot')
    divination = buff('Divination', 15, 0, 1.06, 180, 'pot')
    sleevebuff = buff('Sleeve Draw', 15, 0, 0, 0, 'None')

    buffs= [goodcard, badcard, notmycard, bigcard, divination, sleevebuff]
    buffdict = {}
    for i in buffs:
        buffdict[i.name] = i

    return [abildict, buffdict, deck]

def genjobs():
    nin = job('NIN', 'DPS', True, 2.4, .7, .15, True)
    drg = job('DRG', 'DPS', True, 2.4, .7, .15, False)
    mnk = job('MNK', 'DPS', False, 2.4, .7, .15, False)
    sam = job('SAM', 'DPS', False, 2.4, .7, .15, False)

    dnc = job('DNC', 'DPS', False, 2.4, 0, .15, False)
    mch = job('MCH', 'DPS', False, 2.4, 0, .15, False)

    rdm = job('RDM', 'DPS', True, 2.4, 0, .15, False)
    smn = job('SMN', 'DPS', False, 2.4, 0, .15, False)
    blm = job('BLM', 'DPS', False, 2.4, 0, .15, False)

    sch = job('SCH', 'HEAL', True, 2.4, 0, .15, False)
    ast = job('AST', 'HEAL', True, 2.4, 0, .15, False)
    whm = job('WHM', 'HEAL', False, 2.4, 0, .15, False)

    gnb = job('GNB', 'TANK', True, 2.4, 0, .15, False)
    war = job('WAR', 'TANK', True, 2.4, 0, .15, False)
    drk = job('DRK', 'TANK', False, 2.4, 0, .15, False)
    pld = job('PLD', 'TANK', False, 2.4, 0, .15, False)


    table = [nin,drg,mnk,sam,dnc,mch,rdm,smn,blm,sch,ast,whm,gnb,war,drk,pld]

    dict ={}
    for i in table:
        dict[i.name] = i

    return dict

def genparty(jobs):

    party = []
    for i in jobs.values():
        if i.active:
            party.append(i)

    dict = {}
    for i in party:
        dict[i.name] = i

    return dict

def genpbuffs(party, tetherbuff,dncpart):

    goodcard = buff('Bole', 15, 0, 1.06, 0,'pot')
    badcard = buff('Balance', 15, 0, 1.03, 0, 'pot')
    notmycard = buff('Not my Card', 15, 0, 1.00, 0, 'pot')
    bigcard = buff('Lady', 15, 0, 1.08, 0, 'pot')
    divination = buff('Divination', 15, 0, 1.06, 180,'pot')
    trick = buff('Trick Attack', 10, 9.82, 1.1, 60,'pot')
    trick.activationdelay = .8
    tether = buff("Dragon Sight", 20, 1.4, 1.05, 120,'pot')
    devotion = buff("Devotion", 15, 15.0, 1.05, 180,'pot')
    brotherhood = buff("Brotherhood", 14, 10.5, 1.05, 90,'pot')
    embolden = buff("Embolden", 20, 10, 1.1, 120,'pot')
    embolden.falloff = True

    technical = buff('Technical Finish', 15, 10.4, 1.05, 120,'pot')
    sabercrit = buff('Saber Dance CRIT',15,7.8,30,120,'ch')
    saberdh = buff('Saber Dance DH',15,7.8,30,120,'dh')
    litany = buff("Battle Litany", 20, 3.1, 10, 180,'ch')
    chain = buff("Chain Stratagem", 15, 3.1, 10, 120,'ch')
    chain.activationdelay = .8
    buffs = []
    for i in party.keys():
        if i == 'NIN':
            buffs.append(trick)
        if i == 'DRG':
            buffs.append(litany)
            if tetherbuff:
                buffs.append(tether)
        if i == 'MNK':
            buffs.append(brotherhood)
        if i == 'RDM':
            buffs.append(embolden)
        if i == 'SMN':
            buffs.append(devotion)
        if i == 'DNC':
            buffs.append(technical)
            if dncpart:
                buffs.append(sabercrit)
                buffs.append(saberdh)
        if i == 'SCH':
            buffs.append(chain)



    dict = {}
    for i in buffs:
        dict[i.name] = i

    return dict

def genbuffs():


    wm = buff('Minuet',30,0,0,90,'Song')
    mb = buff('Ballad',30,0,0,90,'Song')
    ap = buff('Paeon',30,0,0,90,'Song')
    ss = buff('SS Ready',10,0,0,0,'Proc')
    bv = buff('Battle Voice',20,0,20,180,'dh')
    rs = buff('Raging Strikes',20,0,0,80,'pot')
    muse =buff('Armys Muse',10,0,12,0,'Special')
    ethos = buff('Armys Ethos',30,0,0,0,'Special')
    barrage = buff('Barrage',10,0,0,80,'None')

    potionbuff = buff('Potion', 30, 0, .1, 0,'None')



    table =[wm,mb,ap,ss,bv,rs,muse,ethos,barrage,potionbuff]

    dict = {}
    for i in table:
        dict[i.name] = i
    return dict

def settings():
    openers = {}
    fight = {}
    with open('settings.txt', 'r') as f:
        for line in f:
            type = line.split(':')
            if type[0].lower() == 'opener':
                try:
                    type2 = type[1].split(';')
                    key = type2[0]
                    openlist = type2[1].split(',')
                    opentable = []
                    for i in openlist:
                        opentable.append(i.rstrip('\n'))
                    openers[key] = opentable
                except:
                    pass
            elif type[0].lower() == 'fight':
                try:
                    type2 = type[1].split(';')
                    key = type2[0]
                    holdlist = type2[1].split(',')
                    fighttable = []
                    for i in holdlist:
                        holdtime = []
                        parsetimes = i.split('-')
                        holdtime.append(int(parsetimes[0]))
                        holdtime.append(int(parsetimes[1]))
                        holdtime.append(bool(parsetimes[2].rstrip('/n')))
                        fighttable.append(holdtime)
                    fight[key] = fighttable
                except:
                    pass
    openstrings = []
    fightstrings = []
    for i in openers.keys():
        openstrings.append(i)
    for i in fight.keys():
        fightstrings.append(i)
    tempopeners = {}
    tempopeners['Standard'] = ['PotionPre','Stormbite','Bloodletter','Raging Strikes','Caustic Bite','Minuet','Empyreal Arrow','AutoPP 1','AutoGCD','Battle Voice','AutoPP 1', 'AutoGCD','AutoPP 2','Iron Jaws']
    return [tempopeners,['Standard'],fight,fightstrings]

def setpmod(abilities, val):

    for i in abilities.values():
        i.partymod = val

