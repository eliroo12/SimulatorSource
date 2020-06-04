import math

# Returns Crit Chance and Crit Bonus
def determinecrit(crit):

    return math.floor(200*(crit-380)/3300+50)/10, math.floor(200*(crit-380)/3300+1400)/1000

def determinedh(dh):
    return math.floor(550*(dh-380)/3300)/10

def determinegcd(ss):
    GCDm = math.floor((1000 - math.floor(130*(ss-380)/3300))*2500/1000)
    A = math.floor(math.floor(math.floor(math.floor((100-0)*(100-0)/100)*(100-0)/100))-0)
    B = (100 - 0) / 100
    GCDc = math.floor(math.floor(math.floor(math.ceil(A*B)*GCDm/100)*100/1000)*100/100)

    return GCDc / 100

def determinedet(deter):

    return round(((math.floor(130*(deter-340)/3300+1000)/1000)-1)*100,2)