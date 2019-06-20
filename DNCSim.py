import simdictionary
from ability import ability
from buff import buff
from job import job
from sim import sim
import stats
import asyncio
import time
import statistics

import simdictionary as build

async def runsim(openers,fights,stattable,abilities,party,pbuffs,buffs):
    tasks = []
    tasks2 = []
    tasks3 =[]
    x= 0
    while x < 2:
        tasks.append(asyncio.create_task(sim(x,600,openers['Late Trick'],fights['Default'],stattable,abilities,party,pbuffs,buffs,True,False,False).sim()))
        tasks2.append(asyncio.create_task(
            sim(x, 600, openers['Late Trick'], fights['Default'], stattable, abilities, party, pbuffs, buffs, True,
                False, False).sim()))
        tasks3.append(asyncio.create_task(
            sim(x, 600, openers['Late Trick'], fights['Default'], stattable, abilities, party, pbuffs, buffs, True,
                False, False).sim()))
        x = x + 1
    a = await asyncio.gather(*tasks)
    b = await asyncio.gather(*tasks2)
    c = await asyncio.gather(*tasks3)

    return a + b + c

def main():

    dex = 3662
    WD = 114
    det = 1462
    ss = 1283
    crit = 1967
    dh = 1806
    wepdelay = 3.12
    critchance, critbonus = stats.determinecrit(crit)
    gcd = 2.41
    dhrate = stats.determinedh(dh)

    # stat table build out = WD,Wepdelay,Dex,Critrate,Critdamage,Directrate,Det,skillspeed,gcd
    stattable = [WD, wepdelay, dex, critchance, critbonus, dhrate, det, ss, gcd]
    jobs = build.genjobs()
    party = build.genparty(jobs)
    pbuffs = build.genpbuffs(party, False)
    buffs = build.genbuffs()
    abilities = build.genabil(wepdelay,gcd)
    settings = build.settings()
    openers = settings[0]
    fights = settings[1]
    runtime = 0
    potencytable = []
    x =[]
    s = time.perf_counter()
    while runtime < 50:
        stattable = [WD, wepdelay, dex, critchance, critbonus, dhrate, det, ss, gcd]
        x = x + asyncio.run(runsim(openers,fights,stattable,abilities,party,pbuffs,buffs))
        runtime = runtime + 1
    elapsed = time.perf_counter() - s
    print(len(x))
    print('Time to complete:'+str(elapsed))
        #potencytable.append(sim(1,600,openers['Late Trick'],fights['Default'],stattable,abilities,party,pbuffs,buffs,True,False,False).sim())
        #runtime = runtime + 1
    #print(statistics.mean(potencytable)/600)






main()

