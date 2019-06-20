class action:

    def __init__(self, id, name, actiontime):
        self.id = id
        self.name = name
        self.actiontime = actiontime

    def actionable(self, time):
        return time == self.actiontime