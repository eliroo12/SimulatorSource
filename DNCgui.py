import PySimpleGUI as sg
from sim import sim
import stats
import simdictionary as build
import numpy
from buff import buff
from ability import ability
from job import job
import statistics
import matplotlib
import asyncio
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import tkinter as Tk
import matplotlib.pyplot as plt





def draw_figure(canvas, figure, loc=(0, 0)):
    """ Draw a matplotlib figure onto a Tk canvas
    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    """
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = Tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
    canvas.create_image(loc[0] + figure_w / 2, loc[1] + figure_h / 2, image=photo)
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    return photo

async def runsim(runjobs,runtime,currentid,open,fight,stattable,abilities,party,pbuffs,buffs,potion,ast,log):
    tasks = []
    tasks2 = []
    tasks3 = []
    a = []
    b = []
    c = []
    one = False
    two = False
    three = False
    x = 0
    while x < runjobs:
        one = True
        tasks.append(asyncio.create_task(sim(1, runtime, open, fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log).sim()))
        x = x + 1
        if x < runjobs:
            two = True
            tasks2.append(asyncio.create_task(sim(1, runtime, open,fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log).sim()))
        x = x + 1
        if x < runjobs:
            three = True
            tasks3.append(asyncio.create_task(sim(1, runtime,  open, fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log).sim()))
        x = x + 1
    if one:
        a = await asyncio.gather(*tasks)
    if two:
        b = await asyncio.gather(*tasks2)
    if three:
        c = await asyncio.gather(*tasks3)

    return a + b + c

async def run1sim(runjobs,runtime,currentid,open,fight,stattable,abilities,party,pbuffs,buffs,potion,ast,log):
    tasks = []
    tasks2 = []
    tasks3 = []
    a = []
    b = []
    c = []
    atime = []
    btime =[]
    ctime =[]
    abilitydict = {}
    returntable = []
    one = False
    two = False
    three = False
    x = 0
    while x < runjobs:
        one = True
        sim1 = sim(1, runtime, open, fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log)
        tasks.append(asyncio.create_task(sim1.sim()))
        x = x + 1
        if x < runjobs:
            two = True
            sim2 = sim(1, runtime, open, fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log)
            tasks2.append(asyncio.create_task(sim2.sim()))
        x = x + 1
        if x < runjobs:
            three = True
            sim3 = sim(1, runtime, open, fight, stattable, abilities, party, pbuffs, buffs, potion,ast, log)
            tasks3.append(asyncio.create_task(sim3.sim()))
        x = x + 1
    if one:
        a = await asyncio.gather(*tasks)
        atime = sim1.timetable
        ability = sim1.abilities
        returntable.append(atime)
        for i in ability.keys():
            if i in abilitydict.keys():
                abilitydict[i] = abilitydict[i] + ability[i].totalpotency
            else:
                abilitydict[i] = ability[i].totalpotency
    if two:
        b = await asyncio.gather(*tasks2)
        btime = sim2.timetable
        ability = sim2.abilities
        returntable.append(btime)
        for i in ability.keys():
            if i in abilitydict.keys():
                abilitydict[i] = abilitydict[i] + ability[i].totalpotency
            else:
                abilitydict[i] = ability[i].totalpotency
    if three:
        c = await asyncio.gather(*tasks3)
        ability = sim3.abilities
        for i in ability.keys():
            if i in abilitydict.keys():
                abilitydict[i] = abilitydict[i] + ability[i].totalpotency
            else:
                abilitydict[i] = ability[i].totalpotency
        ctime = sim3.timetable
        returntable.append(ctime)


    return a + b + c, returntable,abilitydict


def main():
    ###### Gather default data #######
    tether = False
    astpriority = False
    settings = build.settings()
    openers = settings[0]
    fights = settings[2]
    openlist = settings[1]
    fightlist = settings[3]
    jobs = build.genjobs()
    party = build.genparty(jobs)
    pbuffs = build.genpbuffs(party,tether)
    buffs = build.genbuffs()
    dex = 3662
    WD = 114
    det = 1462
    ss = 1283
    crit = 1967+1360
    dh = 1806+560
    wepdelay = 3.12
    gcd = stats.determinegcd(ss)
    abilities = build.genabil(wepdelay,gcd)

    layout = [[sg.Text("DNC Simulator"),sg.Text('',size=(20,1)),sg.Image('graphics/DRK.png',size=(8,1))],
			  [sg.Text("Sim One Stats"), sg.Text(''),sg.Text('',size=(22,1)),sg.Text('Sim Two Stats')],
			  [sg.Text("Weapon Damage",size=(14,1)), sg.Input(default_text=WD,size=(8,1),key='wd1',do_not_clear=True), sg.Text('',size=(12,1)),sg.Text("Weapon Damage",size=(14,1)), sg.Input(default_text='',size=(8,1),key='wd2',do_not_clear=True)],
			  [sg.Text("Weapon Delay",size=(14,1)), sg.Input(default_text=wepdelay,size=(8,1),key='del1',do_not_clear=True),sg.Text('',size=(12,1)),sg.Text("Weapon Delay",size=(14,1)), sg.Input(default_text=wepdelay,size=(8,1),key='del2',do_not_clear=True)],
			  [sg.Text("Dexterity",size=(14,1)), sg.Input(default_text=dex,size=(8,1),key='dex1',do_not_clear=True),sg.Text('',size=(12,1)),sg.Text("Dexterity",size=(14,1)), sg.Input(size=(8,1),key='dex2',do_not_clear=True)],
			  [sg.Text("Critical Hit Rate",size=(14,1)), sg.Input(default_text=crit,size=(8,1),key='crit1',do_not_clear=True),sg.Text('',size=(12,1),key='crate1'),sg.Text("Critical Hit Rate",size=(14,1)), sg.Input(default_text='3347',size=(8,1),key='crit2',do_not_clear=True),sg.Text('',key='crate2',size=(12,1))],
			  [sg.Text("Direct Hit",size=(14,1)), sg.Input(default_text=dh,size=(8,1),key='dh1',do_not_clear=True),sg.Text('',size=(12,1),key='direct1'),sg.Text("Direct Hit",size=(14,1)), sg.Input(default_text='2046',size=(8,1),key='dh2',do_not_clear=True),sg.Text('',key='direct2',size=(10,1))],
			  [sg.Text("Determination",size=(14,1)), sg.Input(default_text=det,size=(8,1),key='det1',do_not_clear=True),sg.Text('',size=(12,1),key='deter1'),sg.Text("Determination",size=(14,1)), sg.Input(default_text='1462',size=(8,1),key='det2',do_not_clear=True),sg.Text('',key='deter2',size=(10,1))],
			  [sg.Text("Skill Speed",size=(14,1)), sg.Input(default_text=ss,size=(8,1),key='sks1',do_not_clear=True),sg.Text('',size=(12,1),key='skill1'),sg.Text("Skill Speed",size=(14,1)), sg.Input(default_text='1283',size=(8,1),key='sks2',do_not_clear=True),sg.Text('',key='skill2',size=(10,1))],
			  [sg.Text("Opener", size=(14,1)), sg.InputCombo(openlist, key='open1'), sg.Text('',size=(7,1)), sg.Text("Opener", size=(14,1)), sg.InputCombo(openlist, key='open2')],
			  [sg.Text("Fight", size=(14,1),tooltip='Determine fight breaks, if any'), sg.InputCombo(fightlist,key='fights'), sg.Text('',size=(10,1)),sg.Checkbox('Create Logs', size=(10,1),key='logs')],
			  [sg.Text("Length of Fight",tooltip='How long is the fight', size=(16,1)),sg.Input(default_text='300',size=(8,1),key='length'), sg.Text('',size=(9,1)),sg.Checkbox('Party Modifier', size=(10,1),key='partymod')],
			  [sg.Text("Run How many Times",tooltip='The Higher number, the longer and more accurate the sim is', size=(16,1)),sg.Input(default_text='200',size=(7,1),key='runtime'), sg.Text('',size=(10,1)),sg.Checkbox('Use Potion',tooltip='Will Still use if specified in opener', size=(8,1),key='potion')],
			  [sg.Button('Run Sim',key='sim'),sg.Text('',size=(20,1)),sg.Button('Set Party',key='party'),sg.Button('Set Buff Times',key='buffs')]]
    sim1 =['wd1','del1','dex1','crit1','dh1','det1','sks1']
    sim2 =['wd2','del2','dex2','crit2','dh2','det2','sks2']
    window = sg.Window("DNC Simulator",icon='graphics\\DRK.png').Layout(layout)

    win2_active = False
    win3_active = False
    win4_active = False

    while True:
        button, values = window.Read(timeout=100)

        if button is None:
            break
        #Update window elements
        try:
            string = str(stats.determinecrit(int(values['crit1']))[0])+'% '+str(stats.determinecrit(int(values['crit1']))[1])+'% '
            window.FindElement('crate1').Update(string)
        except:
            window.FindElement('crate1').Update('')
        try:
            window.FindElement('direct1').Update(str(stats.determinedh(int(values['dh1'])))+'%')
        except:
            window.FindElement('direct1').Update('')
        try:
            window.FindElement('deter1').Update(str(stats.determinedet(int(values['det1'])))+'%')
        except:
            window.FindElement('deter1').Update('')
        try:
            window.FindElement('skill1').Update(stats.determinegcd(int(values['sks1'])))
        except:
            window.FindElement('skill1').Update('')
        try:
            string2 = str(stats.determinecrit(int(values['crit2']))[0]) + '% ' + str(stats.determinecrit(int(values['crit2']))[1]) + '% '
            window.FindElement('crate2').Update(string2)
        except:
            window.FindElement('crate2').Update('')
        try:
            window.FindElement('direct2').Update(str(stats.determinedh(int(values['dh2'])))+'%')
        except:
            window.FindElement('direct2').Update('')
        try:
            window.FindElement('deter2').Update(str(stats.determinedet(int(values['det2'])))+'%')
        except:
            window.FindElement('deter2').Update('')
        try:
            window.FindElement('skill2').Update(stats.determinegcd(int(values['sks2'])))
        except:
            window.FindElement('skill2').Update('')

        #Process window generation when we want to change party UI
        if not win2_active and button == 'party':
            window.Hide()
            win2_active = True
            layout2 = [[sg.Text('Job', size=(8,1)),sg.Text('Member',size=(8,1)),sg.Text('Partner',size=(8,1)), sg.Text('Buff Priority',size=(8,1))],]
            for i in jobs.values():
                row = []
                row.append(sg.Text(i.name, size=(8,1)))
                row.append(sg.Checkbox('',size=(8,1), default=i.active, key=i.name))
                row.append(sg.Radio('',size=(8,1),default=i.partner,group_id='partner', key=i.name+'part'))
                if i.name == 'AST':
                    row.append(sg.Checkbox('AST Priority',size=(8,1),default=astpriority,key='astprio'))
                elif i.name == 'DRG':
                    row.append(sg.Checkbox('DRG Tether', size=(8, 1), default=tether, key='tether'))
                layout2.append(row)
            layout2.append([sg.Button('Done')])
            win2 = sg.Window('Party Screen').Layout(layout2)

        #Process information when Sim its clicked
        if not win3_active and button == 'sim':
            simoneaction = True
            simtwoaction = True
            simonetable = []
            simtwotable = []
            fight = fights[values['fights']]
            logging = values['logs']
            build.setpmod(abilities,values['partymod'])
            potion = values['potion']
            for i in sim1:
                if values[i] == '':
                    simoneaction = False
                elif i == 'crit1':
                    rate, dam = stats.determinecrit(int(values[i]))
                    simonetable.append(rate)
                    simonetable.append(dam)
                elif i == 'dh1':
                    simonetable.append(stats.determinedh(int(values[i])))
                elif i == 'sks1':
                    simonetable.append(int(values[i]))
                    simonetable.append(stats.determinegcd(int(values[i])))
                else:
                    simonetable.append(float(values[i]))
            if not simoneaction:
                sg.PopupOK('Please enter in Values for Sim One')
            else:
                for i in sim2:
                    if values[i] == '':
                        simtwoaction = False
                    elif i == 'crit2':
                        rate, dam = stats.determinecrit(int(values[i]))
                        simtwotable.append(rate)
                        simtwotable.append(dam)
                    elif i == 'dh2':
                        simtwotable.append(stats.determinedh(int(values[i])))
                    elif i == 'sks2':
                        simtwotable.append(int(values[i]))
                        simtwotable.append(stats.determinegcd(int(values[i])))
                    else:
                        simtwotable.append(float(values[i]))
                if simtwoaction:
                    runtimes = int(values['runtime'])
                    runlength = int(values['length'])

                    opener1 = openers[values['open1']]
                    opener2 = openers[values['open2']]
                    potency1 = []
                    potency2 = []
                    layoutprog = [[sg.Text('Running Sim', key='progtext')],
                                  [sg.ProgressBar(runtimes, orientation='h', size=(20, 20), key='progbar')],
                                  [sg.Button('Cancel')]]
                    progwin = sg.Window('Running Sim One', layoutprog)
                    bar = progwin.FindElement('progbar')
                    i = runtimes
                    while i > 0:
                        progevent, progvals = progwin.Read(timeout=100)
                        if progevent == 'Cancel' or progevent is None:
                            break
                        jobruns = 0
                        if i > 5:
                            jobruns = 6
                        else:
                            jobruns = i
                        results = asyncio.run(runsim(jobruns,runlength,i,opener1,fight,simonetable,abilities,party,pbuffs,buffs,potion,astpriority,logging))
                        potency1 = potency1 + results
                        i = i - jobruns
                        bar.UpdateBar(runtimes - i)
                    progwin.TKroot.title('Running Sim Two')
                    i = runtimes
                    while i > 0:
                        progevent, progvals = progwin.Read(timeout=100)
                        if progevent == 'Cancel' or progevent is None:
                            break
                        jobruns = 0
                        if i > 5:
                            jobruns = 6
                        else:
                            jobruns = i
                        results = asyncio.run(
                            runsim(jobruns, runlength, i, opener2, fight, simtwotable, abilities, party, pbuffs,
                                   buffs, potion, astpriority, logging))
                        potency2 = potency2 + results
                        i = i - jobruns
                        bar.UpdateBar(runtimes - i)
                    progwin.Close()
                    sg.PopupAnimated('graphics/loading.gif','Finalizing your results',time_between_frames =1)

                    maxval = max(potency1)
                    minval = min(potency1)
                    if runtimes > 1:
                        aveval = statistics.mean(potency1)
                        deviation = round(statistics.stdev(potency1),3)
                    else:
                        aveval = potency1[0]
                        deviation = potency1[0]

                    maxval2 = max(potency2)
                    minval2 = min(potency2)
                    if runtimes > 1:
                        aveval2 = statistics.mean(potency2)
                        deviation2 = round(statistics.stdev(potency2),3)
                    else:
                        aveval2 = potency2[0]
                        deviation = potency2[0]

                    if aveval > aveval2:
                        color1 ='#3CB371'
                        color2 ='#B22222'
                    else:
                        color2 = '#3CB371'
                        color1 = '#B22222'

                    results_layout = [[sg.Text('Sim One'), sg.Text('', size=(16, 1)),
                                       sg.Text(str(round(aveval, 3)), size=(8, 1), font=('Helvetica', 20),text_color=color1),sg.Text('',size=(2,1)), sg.Text('Sim Two',size=(22,1)), sg.Text(str(round(aveval2, 3)), size=(8, 1), font=('Helvetica', 20),text_color=color2)],
                                      [sg.Text('Weapon Damage: ', size=(14, 1)),
                                       sg.Text(str(int(simonetable[0])), size=(8, 1)), sg.Text('Max', size=(8, 1)),
                                       sg.Text(maxval,size=(10,1)),sg.Text('Weapon Damage: ', size=(14, 1)),
                                       sg.Text(str(int(simtwotable[0])), size=(8, 1)), sg.Text('Max', size=(8, 1)),
                                       sg.Text(maxval2)],
                                      [sg.Text('Weapon Delay: ', size=(14, 1)),
                                       sg.Text(str(simonetable[1]), size=(8, 1)), sg.Text('Min', size=(8, 1)),
                                       sg.Text(minval,size=(10,1)),sg.Text('Weapon Delay: ', size=(14, 1)),
                                       sg.Text(str(simtwotable[1]), size=(8, 1)), sg.Text('Min', size=(8, 1)),
                                       sg.Text(minval2)],
                                      [sg.Text('Dexterity: ', size=(14, 1)),
                                       sg.Text(str(int(simonetable[2])), size=(8, 1)),
                                       sg.Text('Deviation', size=(8, 1)), sg.Text(deviation,size=(10,1)),sg.Text('Dexterity: ', size=(14, 1)),
                                       sg.Text(str(int(simtwotable[2])), size=(8, 1)),
                                       sg.Text('Deviation', size=(8, 1)), sg.Text(deviation2)],
                                      [sg.Text('Critical Hit Rate: ', size=(14, 1)),
                                       sg.Text(str(int(values['crit1'])),size=(8,1)),sg.Text('',size=(20,1)),sg.Text('Critical Hit Rate: ', size=(14, 1)),
                                       sg.Text(str(int(values['crit2'])))],
                                      [sg.Text('Direct Hit: ', size=(14, 1)), sg.Text(str(int(values["dh1"])),size=(8,1)),sg.Text('',size=(20,1)),sg.Text('Direct Hit: ', size=(14, 1)), sg.Text(str(int(values['dh2'])))],
                                      [sg.Text('Determination: ', size=(14, 1)), sg.Text(str(int(simonetable[6])),size=(8,1)),sg.Text('',size=(20,1)),sg.Text('Determination: ', size=(14, 1)), sg.Text(str(int(simtwotable[6])))],
                                      [sg.Text('Skillspeed: ', size=(14, 1)), sg.Text(str(int(simonetable[7])),size=(8,1)),sg.Text('',size=(20,1)),sg.Text('Skillspeed: ', size=(14, 1)), sg.Text(str(int(simtwotable[7])))],
                                      [sg.Text('Opener: ', size=(14,1)),sg.Text(values["open1"],size=(30,1)),sg.Text('Opener: ',size=(14,1)),sg.Text(values["open2"])],
                                      #[sg.Canvas(size=(figure_w, figure_h), key='canvas'),sg.Canvas(size=(figure_w, figure_h), key='canvas2')],
                                      #[sg.Text(sim.returnpartystring())],
                                      [sg.Button('Close')]]
                    if logging:
                        results_layout[9].append(sg.Button('View Logs',key='logview'))
                    resultwindow = sg.Window("Sim Results", force_toplevel=True).Layout(results_layout).Finalize()
                    window.Hide()
                    sg.PopupAnimated(image_source=None)
                    win3_active = True


                else:
                    runtimes = int(values['runtime'])
                    runlength = int(values['length'])
                    opener1 = openers[values['open1']]
                    fight = fights[values['fights']]
                    logging = values['logs']
                    build.setpmod(abilities, values['partymod'])
                    potion = values['potion']
                    potency1 = []
                    abilitydict = {}
                    viewtimes = [[]]
                    firstime = False
                    layoutprog = [[sg.Text('Running Sim',key='progtext')], [sg.ProgressBar(runtimes, orientation = 'h', size =(20,20),key='progbar')], [sg.Button('Cancel')]]
                    progwin = sg.Window('Running Sim',layoutprog)
                    bar = progwin.FindElement('progbar')
                    i = runtimes
                    while i > 0:
                        progevent, progvals = progwin.Read(timeout=100)
                        if progevent == 'Cancel' or progevent is None:
                            break
                        jobruns = 0
                        if i > 5:
                            jobruns = 6
                        else:
                            jobruns = i
                        results, times, ability= asyncio.run(run1sim(jobruns, runlength, (runtimes-i), opener1, fight, simonetable, abilities, party, pbuffs,buffs, potion, astpriority, logging))
                        potency1 = potency1 + results
                        for u in times:
                            viewtimes.append(u)
                        for u in ability.keys():
                            if ability[u] > 0:
                                if u in abilitydict.keys():
                                    abilitydict[u] = abilitydict[u] + ability[u]
                                else:
                                    abilitydict[u] = ability[u]

                        i = i - jobruns
                        bar.UpdateBar(runtimes - i)
                    progwin.Close()
                    sg.PopupAnimated('graphics/loading.gif','Finalizing your results',time_between_frames =1)
                    maxval = max(potency1)
                    minval = min(potency1)
                    allpotency = 0
                    for i in abilitydict.keys():
                        allpotency = allpotency + abilitydict[i]

                    for i in abilitydict.keys():
                        abilitydict[i] = round((abilitydict[i] / allpotency) * 100, 2)

                    sort = sorted(abilitydict, key=abilitydict.__getitem__, reverse=True)
                    viewtimes.remove([])
                    viewtable = numpy.mean(viewtimes, axis=0)
                    if runtimes > 1:
                        aveval = round(statistics.mean(potency1),3)
                        deviation = round(statistics.stdev(potency1),3)
                    else:
                        aveval = round(potency1[0],3)
                        deviation = round(potency1[0],3)
                    if runtimes > 1 :

                        plt.plot(list(range(5,runlength)),viewtable)
                        plt.xlabel('Time')
                        plt.xlabel('DPS')
                        #plt.hist(potency1,
                        #         color='blue',
                        #         edgecolor='black',
                        #         bins=int((maxval - minval)/(runtimes/(runtimes*.15))))
                        fig = plt.gcf()
                        figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
                    else:
                        figure_w = 8
                        figure_h = 1
                    results_layout =[[sg.Text('Stats Used'),sg.Text('',size=(16,1)),sg.Text(str(round(aveval,3)),size=(8,1),font=('Helvetica',20))],
                                     [sg.Text('Weapon Damage: ',size=(14,1)), sg.Text(str(int(simonetable[0])),size=(8,1)),sg.Text('Max',size=(8,1)),sg.Text(maxval)],
                                     [sg.Text('Weapon Delay: ',size=(14,1)), sg.Text(str(simonetable[1]),size=(8,1)),sg.Text('Min',size=(8,1)),sg.Text(minval)],
                                     [sg.Text('Dexterity: ',size=(14,1)), sg.Text(str(int(simonetable[2])),size=(8,1)),sg.Text('Deviation',size=(8,1)),sg.Text(deviation)],
                                     [sg.Text('Critical Hit Rate: ',size=(14,1)), sg.Text(str(int((values['crit1']))))],
                                     [sg.Text('Direct Hit: ',size=(14,1)), sg.Text(str(int(values['dh1'])))],
                                     [sg.Text('Determination: ',size=(14,1)), sg.Text(str(int(simonetable[6])))],
                                     [sg.Text('Skillspeed: ',size=(14,1)), sg.Text(str(int(simonetable[7])))],
                                     [sg.Text('Opener: ', size=(14, 1)), sg.Text(values["open1"], size=(30, 1))],
                                     [sg.Canvas(size=(figure_w, figure_h), key='canvas')]]
                    row = []
                    x = 0
                    for i in sort:
                        if x == 4:
                            row.append(sg.Text(i + ' ' + str(abilitydict[i]) + '%', size=(18, 1)))
                            results_layout.append(row)
                            x = 0
                        elif x == 0:
                            row = [sg.Text(i + ' ' + str(abilitydict[i]) + '%', size=(18, 1))]
                            x = x + 1
                        else:
                            row.append(sg.Text(i + ' ' + str(abilitydict[i]) + '%', size=(18, 1)))
                            x = x + 1
                    if x > 0:
                        results_layout.append(row)
                    finalrow = [sg.Button('Close')]
                    if logging:
                        finalrow.append(sg.Button('View Logs', key='logview'))
                    results_layout.append(finalrow)
                    resultwindow = sg.Window("Sim Results", force_toplevel=True).Layout(results_layout).Finalize()
                    window.Hide()
                    if runtimes > 1:
                        fig_photo = draw_figure(resultwindow.FindElement('canvas').TKCanvas, fig)
                    sg.PopupAnimated(image_source=None)
                    win3_active = True





            #except:
             #   sg.PopupOK('Please Enter Valid Numbers')

        if not win4_active and button == 'buffs':
            bufflayout = [[sg.Text('Buff Start Times')]]
            for i in pbuffs.values():
                if not (i.name == 'Not My Card' or i.name == 'Bole' or i.name == 'Balance' or i.name== 'Divination'):
                    addtolayout = []
                    addtolayout.append(sg.Text(i.name,size=(12,1)))
                    addtolayout.append(sg.Input(default_text=i.starttime,key=i.name,size=(8,1)))
                    bufflayout.append(addtolayout)
            bufflayout.append([sg.Button('Done',key='donebuff')])
            buffwindow = sg.Window('Set Buff Timers').Layout(bufflayout)
            window.Hide()
            win4_active = True





        if win2_active:
            button2, values2 = win2.Read(timeout=100)
            if button2 is None:
                win2_active = False
                win2.Close()
                window.UnHide()
                window.BringToFront()
            elif button2 is 'Done':
                partyset = []
                #jobs = ['NIN','DRG','MNK','SAM','BRD','MCH','RDM','SMN','BLM','WHM','SCH','AST','GNB','WAR','DRK','PLD']
                membernumber = 0
                for i in jobs.values():
                    i.active = values2[i.name]
                    if values2[i.name]:
                        membernumber = membernumber + 1
                if membernumber > 7:
                    sg.PopupOK('You have to many members')
                else:
                    party = build.genparty(jobs)
                    foundpart = False
                    partner = 'None'
                    for i in party.values():
                        if values2[i.name+'part']:
                            foundpart = True
                            i.partner = True

                    if not foundpart:
                        sg.PopupOK('You need to select a valid partner')
                    else:
                        tether = values2['tether']
                        astpriority= values2['astprio']
                        pbuffs = build.genpbuffs(party,tether)
                        win2_active = False
                        win2.Close()
                        window.UnHide()
                        window.BringToFront()


        if win3_active:

            resevents, resvalus = resultwindow.Read(timeout=100)

            if resevents is None or resevents == 'Close':
                win3_active = False
                resultwindow.Close()
                window.UnHide()
                window.BringToFront()
            elif resevents is 'logview':
                logfile = open('Dnc_Sim_Log1','r')
                sg.PopupScrolled(logfile.read(),size=(80,None))

        if win4_active:
            buffevents, buffvalues = buffwindow.Read()

            if buffevents is None:
                win4_active = False
                buffwindow.Close()
                window.UnHide()
                window.BringToFront()
            elif buffevents =='donebuff':
                try:
                    for i in pbuffs.values():
                        i.starttime = float(buffvalues[i.name])
                        i.default = float(buffvalues[i.name])
                    win4_active = False
                    buffwindow.Close()
                    window.UnHide()
                except:
                    sg.PopupOK("Please enter valid times")



if __name__ == '__main__':
	main()

