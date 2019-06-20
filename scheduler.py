class scheduler:

    def __init__(self, set):

        self.times = set

    def addtime(self, time):
        if not time == 0:
            self.times.add(round(time,2))

    def nexttime(self):
        time = min(self.times)
        self.times.remove(time)
        return time
