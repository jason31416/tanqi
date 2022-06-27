import pygame
import yaml
import time
import random
import os
import basicplugin

cf = open("config.yml")

config = yaml.safe_load(cf)
pygame.init()

cf.close()

cf = open("pieces.yml")

piecest = yaml.safe_load(cf)
pygame.init()

cf.close()

print("loading all plugins...")

all_plgs = {}

for i in os.listdir("plugins"):
    if i.endswith(".py"):
        print("loading plugin: " + i)
        fl = open("plugins/" + i)
        exec(fl.read())
        all_plgs[i[:-3]] = eval(i[:-3]+"()")
        fl.close()

print("done!")

class ptpc:
    def __init__(self, sz, weight, spd):
        self.sz = sz
        self.weight = weight
        self.spd = spd

ptype = {}

gmsz = (config["game"]["width"], config["game"]["height"])

for i in piecest["all_pieces"]:
    ptype[i["name"]] = ptpc(i["size"], i["weight"], i["speed"])

sc = pygame.display.set_mode((config["display"]["width"], config["display"]["height"]))

ets = []

if config["game"]["setup"]["type"] != "custom":
    tmsc = {"red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 255, 0), "yellow": (255, 255, 0), "other": (0, 0, 0)}
    human_tms = ["red", "blue", "green", "yellow"][:config["game"]["setup"]["team_num"]]
    tms_p_left = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
else:
    plgrt: basicplugin.entitylist = all_plgs[config["game"]["setup"]["custom_plugin"]].custom_generator()
    tmsc = plgrt.tmsc
    gmsz = plgrt.gmsz
    human_tms = plgrt.player_teams
    tms_p_left = {}
    for i in human_tms:
        tms_p_left[i] = 0
    ets = plgrt.pieceslist

wsz = (config["display"]["width"], config["display"]["height"])

def dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

selected = None


stage = 0

vx, vy = 0, 0

class pieces:
    def __init__(self, x, y, tp: ptpc, tm):
        self.x = x
        self.y = y
        self.tp = tp
        self.team = tm
        self.spdx, self.spdy = 0, 0
        if self.team in human_tms:
            tms_p_left[self.team] += 1

    def draw(self):
        if 0 <= self.x - vx < wsz[0] and 0 <= self.y - vy < wsz[1]:
            pygame.draw.circle(sc, tmsc[self.team], (self.x-vx, self.y-vy), self.tp.sz)

    def onselect(self):
        global stage
        pygame.draw.circle(sc, (200, 200, 200), (self.x-vx, self.y-vy), self.tp.sz + 200)
        mousex, mousey = pygame.mouse.get_pos()
        if self.tp.sz + 200 > dist(self.x-vx, self.y-vy, mousex, mousey) > self.tp.sz + 20 and pygame.mouse.get_pressed()[0]:
            mx, my = mousex-(self.x-vx), mousey-(self.y-vy)
            self.spdx, self.spdy = round(mx*self.tp.spd/200, 2), round(my*self.tp.spd/200, 2)
            stage = 1


    def update(self):
        global selected
        mouse_pos = pygame.mouse.get_pos()
        if dist(self.x-vx, self.y-vy, mouse_pos[0], mouse_pos[1]) < self.tp.sz and pygame.mouse.get_pressed()[0] and human_tms[turn] == self.team and stage == 0:
            selected = self
        self.draw()
        self.spdx, self.spdy = round(self.spdx, 2), round(self.spdy, 2)
        if (abs(self.spdx) > 1 or abs(self.spdy) > 1) and stage == 1:
            self.x += self.spdx
            self.y += self.spdy
            scw = gmsz[0] - self.tp.sz
            sch = gmsz[1] - self.tp.sz
            if self.x > scw or self.x < 0 or self.y > sch or self.y < 0:
                all_entitys.remove(self)
                tms_p_left[self.team] -= 1
                return
            slowdown = self.tp.weight
            self.spdx /= slowdown
            self.spdy /= slowdown
            for i in all_entitys:
                if i != self:
                    # collide with other pieces
                    if (self.x - i.x) ** 2 + (self.y - i.y) ** 2 == (self.tp.sz + i.tp.sz) ** 2:
                        i.spdx += self.spdx/i.tp.weight
                        i.spdy += self.spdy/i.tp.weight
                        self.spdx = 0
                        self.spdy = 0
                    elif (self.x - i.x) ** 2 + (self.y - i.y) ** 2 < (self.tp.sz + i.tp.sz) ** 2:
                        i.spdx += self.spdx
                        i.spdy += self.spdy
                        self.spdx = 0
                        self.spdy = 0
                        if abs(i.spdx) < 1:
                            if i.spdx < 0:
                                i.spdx = -1
                            elif i.spdx > 0:
                                i.spdx = 1
                        if abs(i.spdy) < 1:
                            if i.spdy < 0:
                                i.spdy = -1
                            elif i.spdy > 0:
                                i.spdy = 1
                        while (self.x - i.x) ** 2 + (self.y - i.y) ** 2 < (self.tp.sz + i.tp.sz) ** 2:
                            i.x += i.spdx
                            i.y += i.spdy
                        i.spdx /= i.tp.weight
                        i.spdy /= i.tp.weight
            return True
        if stage != 1:
            self.spdy, self.spdx = 0, 0
        return False


def draw_text(t, sz, x, y, clr):
    font = pygame.font.SysFont("comicsans", sz)
    text = font.render(t, True, clr)
    sc.blit(text, (x, y))

# setup

all_entitys = []

def create_pieces(x, y, tp, tm):
    all_entitys.append(pieces(x, y, ptype[tp], tm))

def setup():
    if config["game"]["setup"]["type"] == "random":
        if config["game"]["setup"]["seed"] != 0:
            random.seed(config["game"]["setup"]["seed"])
        for i in range(config["game"]["setup"]["num"]):
            create_pieces(random.randint(100, gmsz[0]-100), random.randint(100, gmsz[1]-100), config["game"]["setup"]["default_type"], "red")
        for i in range(config["game"]["setup"]["num"]):
            create_pieces(random.randint(100, gmsz[0]-100), random.randint(100, gmsz[1]-100), config["game"]["setup"]["default_type"], "blue")
        if config["game"]["setup"]["team_num"] > 2:
            for i in range(config["game"]["setup"]["num"]):
                create_pieces(random.randint(100, gmsz[0]-100), random.randint(100, gmsz[1]-100), config["game"]["setup"]["default_type"], "green")
        if config["game"]["setup"]["team_num"] > 3:
            for i in range(config["game"]["setup"]["num"]):
                create_pieces(random.randint(100, gmsz[0]-100), random.randint(100, gmsz[1]-100), config["game"]["setup"]["default_type"], "yellow")
        for i in range(config["game"]["setup"]["obstacle_num"]):
            create_pieces(random.randint(100, gmsz[0]-100), random.randint(100, gmsz[0]-100), config["game"]["setup"]["obstacle_type"], "other")
    elif config["game"]["setup"]["type"] == "normal":
        if config["game"]["setup"]["seed"] != 0:
            random.seed(config["game"]["setup"]["seed"])
        for i in range(config["game"]["setup"]["num"]):
            create_pieces(random.randint(100, gmsz[0]-100), 100, config["game"]["setup"]["default_type"], "red")
        for i in range(config["game"]["setup"]["num"]):
            create_pieces(random.randint(100, gmsz[0]-100), gmsz[1]-100, config["game"]["setup"]["default_type"], "blue")
        if config["game"]["setup"]["team_num"] > 2:
            for i in range(config["game"]["setup"]["num"]):
                create_pieces(gmsz[1]-100, random.randint(100, gmsz[0]-100), config["game"]["setup"]["default_type"], "green")
        if config["game"]["setup"]["team_num"] > 3:
            for i in range(config["game"]["setup"]["num"]):
                create_pieces(100, random.randint(100, gmsz[0]-100), config["game"]["setup"]["default_type"], "yellow")
        for i in range(config["game"]["setup"]["obstacle_num"]):
            create_pieces(random.randint(200, gmsz[0]-200), random.randint(200, gmsz[1]-200), config["game"]["setup"]["obstacle_type"], "other")
    elif config["game"]["setup"]["type"] == "custom":
        for i in ets:
            create_pieces(i[0], i[1], i[3], i[2])

setup()

running = True
fps = 60
tick = 0
turn = 0
winner = ""

while running:
    ntime = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
    sc.fill((0, 0, 0))

    pygame.draw.rect(sc, (255, 255, 255), (-vx, -vy, gmsz[0], gmsz[1]))

    if selected and stage == 0:
        selected.onselect()

    bb = False

    for i in all_entitys:
        a = i.update()
        bb = bb or a

    keys = pygame.key.get_pressed()
    spdm = 5
    if keys[pygame.K_SPACE]:
        spdm *= 4
    if keys[pygame.K_w]:
        vy -= spdm
    if keys[pygame.K_s]:
        vy += spdm
    if keys[pygame.K_a]:
        vx -= spdm
    if keys[pygame.K_d]:
        vx += spdm
    if vx < -100:
        vx = -100
    if vy < -100:
        vy = -100
    if vx > gmsz[0]:
        vx = gmsz[0]
    if vy > gmsz[1]:
        vy = gmsz[1]

    lst = ""

    for i in tms_p_left.keys():
        if tms_p_left[i] != 0:
            if lst == "":
                lst = i
            else:
                lst = ""
                break

    if lst != "":
        # team[lst] wins
        running = False
        winner = lst

    if not bb and stage == 1:
        turn = (turn + 1) % len(human_tms)
        while tms_p_left[human_tms[turn]] == 0:
            turn = (turn + 1) % len(human_tms)
        stage = 0
        selected = None
        nowsel = (0, 0)

    draw_text("Now its " + human_tms[turn] + "'s turn", 24, 10, 10, tmsc[human_tms[turn]])

    for i in all_plgs.keys():
        all_plgs[i].update()

    while time.time() - ntime < 1 / fps:
        pass
    pygame.display.update()
    tick += 1


sc.fill((255, 255, 255))
draw_text("Team" + winner + "wins!", 96, gmsz[0]/2-128, gmsz[1]/2-48, tmsc[winner])
pygame.display.update()
runninga = True
while runninga:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runninga = False