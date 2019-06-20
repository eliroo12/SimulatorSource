class job:

    def __init__(self, name, role, active, gcd, nextgcd, espritrate, partner):
        self.name = name
        self.role = role
        self.active = active
        self.gcd = gcd
        self.nextgcd = nextgcd
        self.firstgcd = nextgcd
        self.espritrate = espritrate
        self.partner = partner


    def switch(self):
        self.active = not self.active

    def reset(self):
        self.nextgcd = self.firstgcd

    def get_icon(self):
        return "graphics/"+self.name+'.png'