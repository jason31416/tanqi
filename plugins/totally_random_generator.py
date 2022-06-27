import basicplugin
import random

# its just a sample plugin

class totally_random_generator(basicplugin.plugin):
    def custom_generator(self):
        el = basicplugin.entitylist()
        el.gmsz = (1000, 1000)
        for i in range(10):
            el.pieceslist.append(self.entity(random.randint(0, el.gmsz[0]), random.randint(0, el.gmsz[1]), random.choice(["red", "blue", "green", "yellow"]), "normal"))
        el.tmsc = {"red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 255, 0), "yellow": (255, 255, 0)}
        el.player_teams = ["red", "blue", "green", "yellow"]
        return el
