
class entitylist:
    pieceslist = []
    tmsc = {}
    player_teams = []
    gmsz = (0, 0)

class plugin:
    def update(self):
        pass

    def entity(self, x, y, team, tp):
        return x, y, team, tp


    def custom_generator(self):
        pass

# class name MUST be equal to the filename