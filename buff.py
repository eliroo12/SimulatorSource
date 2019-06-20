import math

class buff:

    def __init__(self, name, duration, starttime, potency, cooldown,type):

        self.name = name
        self.duration = duration
        self.starttime = starttime
        self.active = False
        self.potency = round(potency, 2)
        self.falloff = False
        self.cooldown = cooldown
        self.available = True
        self.endtime = 0
        self.default = starttime
        self.ready = False
        self.activation = -1
        self.activationdelay = .5
        self.type = type
    # Returns if buff is active
    def getactive(self, time):
        if self.active and (time > self.endtime):
            return False
        elif self.active:
            return True
    # turns buff off and sets the buffs endtime and when the next time is up for use. Also sets the delay on when to switch on
    def activate(self, time):
        if self.active:
            return
        else:
            self.ready = True
            self.activation = round(time + self.activationdelay, 2)

    # Makes the buff active
    def switchon(self,time):
        self.endtime = round(time + self.duration, 2)
        self.starttime = round(time + self.cooldown-self.activationdelay, 2)
        self.active = True
        self.ready = False
        return str(time) + ": Buff / Debuff Up : " + self.name

    #check to see if the buff is dropping in a GCD, used for procs
    def closetodrop(self, time, gcd):
        if self.active and (time > self.endtime):
            return False
        elif (time + gcd - .01) > self.endtime:
            return True
        else:
            return False

    #dropbuff if used or done
    def dropbuff(self, clock):
        if self.active:
            self.active = False
            return str(clock)+ ' : '+self.name+' has fallen off.'
        else:
            return ''


    #get the potency of the buff
    def getpotency(self, clock):
        if not self.active:
            return 0
        elif self.falloff:
            remainingtime = self.endtime - clock
            return 1+(round(2 * math.ceil(remainingtime/4), 2)/100)
        else:
            return round(self.potency, 2)

    #get the duration of the buff
    def returnduration(self,clock):
        if not self.active:
            return 0
        else:
            return self.endtime - clock

    #reset buff starttimes and other values
    def reset(self):
        self.starttime = self.default
        self.activation = -1
        self.active = False
        self.available = False
        self.ready = False

    def setnew(self,time):
        self.default = time
        self.starttime = time
    # literally just exists for Divination

    def specialactivate(self, time, check):
        if check:
            self.potency = 1.06
        else:
            self.potency = 1.03
        self.ready = True
        self.activation = time + self.activationdelay
        return str(time) + ": Buff / Debuff Up : " + self.name