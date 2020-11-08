#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyleft (ↄ) 2020 jkirchartz <me@jkirchartz.com>
#
# Distributed under terms of the NPL (Necessary Public License) license.

"""

"""

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Cycle, Stars, Print
from asciimatics.renderers import ImageFile
from PIL import ImageDraw, Image, ImageOps
from opensimplex import OpenSimplex
from math import sin, pi as PI
from time import time
import numpy as np
import random

class Biome:
    which = 0 # random.randint(0,1)
    numlist= [0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9]
    palette = "default"
    ## COLORS
    WATER=[0,0,255,255]
    LAND=[0,255,0,255]
    BEACH=[255,400,175,255]
    FOREST=[50,255,50,255]
    JUNGLE=[80,255,80,255]
    SAVANNAH=[150,100,20,255]
    DESERT=[255,170,150,255]
    SNOW=[255,255,255,255]

    def __init__(self):
        self.which = random.randint(0,3) # make sure to keep this in-line with the number of generate options
        self.numlist= sorted([x/100 for x in random.sample(range(0, 100), 7)])
        paletteRand=random.randint(0,2)
        if (paletteRand == 1):
            self.palette = "grayscale - dark"
            self.WATER=[255,255,255,255]
            self.LAND=[223,223,223,255]
            self.BEACH=[191,191,191,255]
            self.FOREST=[159,159,159,255]
            self.JUNGLE=[127,127,127,255]
            self.SAVANNAH=[95,95,95,255]
            self.DESERT=[63,63,63,255]
            self.SNOW=[31,31,31,255]
        elif (paletteRand == 2):
            self.palette = "grayscale - light"
            self.WATER=[255,255,255,255]
            self.LAND=[239,239,239,255]
            self.BEACH=[223,223,223,255]
            self.FOREST=[207,207,207,255]
            self.JUNGLE=[191,191,191,255]
            self.SAVANNAH=[175,175,175,255]
            self.DESERT=[159,159,159,255]
            self.SNOW=[143,143,143,255]

    def style(self):
        return format("%s | %s | %s" % (self.which, self.numlist, self.palette))

    def generate(self, e, m):
        if self.which == 0:
            if (e < self.numlist[4]):
                return self.WATER
            else:
                if (m < self.numlist[4]):
                    return self.LAND
                else:
                    return self.DESERT
        elif self.which == 1:
            if (e < self.numlist[0]):
                return self.WATER
            elif (e < self.numlist[1]):
                return self.BEACH
            elif (e < self.numlist[2]):
                return self.FOREST
            elif (e < self.numlist[3]):
                return self.JUNGLE
            elif (e < self.numlist[4]):
                return self.SAVANNAH
            elif (e < self.numlist[6]):
                return self.DESERT
            else:
                return self.SNOW
        elif self.which == 2:
            if (e < self.numlist[1]):
                return self.SNOW
            elif (e < self.numlist[3]):
                if (m < self.numlist[4]):
                    return self.BEACH
                else:
                    return self.DESERT
            elif (e < self.numlist[5]):
                if (m < self.numlist[4]):
                    return self.JUNGLE
                else:
                    return self.FOREST
            else:
                return self.WATER
        elif self.which == 3:
            if (e < self.numlist[0]):
                return self.WATER
            elif (e < self.numlist[1]):
                return self.BEACH
            elif (e < self.numlist[3]):
                if (m < self.numlist[4]):
                    return self.FOREST
                else:
                    return self.JUNGLE
            elif (e < self.numlist[6]):
                if (m < self.numlist[3]):
                    return self.DESERT
                elif (m > self.numlist[5]):
                    return self.SAVANNAH
                else:
                    return self.SNOW
            else:
                return self.LAND
        if self.which == 4:
            if (e < self.numlist[4]):
                return self.WATER
            else:
                if (m < self.numlist[4]):
                    return self.SNOW
                else:
                    return self.FOREST

def makeMap(height, width):
    # ideas from https://www.redblobgames.com/maps/terrain-from-noise/
    gen = OpenSimplex(random.randint(0,99999999))
    gen2 = OpenSimplex(int(time()))
    def noise(nx, ny):
        # Rescale from -1.0:+1.0 to 0.0:1.0
        return gen.noise2d(nx, ny) / 2.0 + 0.5
    def noise2(nx, ny):
        # Rescale from -1.0:+1.0 to 0.0:1.0
        return gen2.noise2d(nx, ny) / 2.0 + 0.5

    poles = random.random() / 2
    equator = (random.random() / 2) + 0.5
    value = []
    bio = Biome()
    island=random.randint(0,2)
    print("# island? %s | style? %s" % (island, bio.style()));

    for y in range(height):
        value.append([0] * width)
        for x in range(width):
            nx = x/width - 0.5
            ny = y/height - 0.5
            e = noise(nx, ny)
            m = noise2(nx, ny)
            if island == 1:
                e = 10*e*e + poles + (equator-poles) * sin(PI * (y / height))
            elif island == 2:
                d = abs(nx) + abs(ny)
                e = (1 + e - d) / 2
            else:
                e = e # do nothing
            value[y][x] = bio.generate(e , m)

    return np.array(value, dtype=np.uint8)

def planet():
    surface=Image.fromarray(makeMap(400,400), mode="RGBA")
    pl=Image.new("RGBA", (400, 400), "#000000")
    draw=ImageDraw.Draw(pl);
    draw.ellipse((0, 0, 400, 400), fill="#FFFFFF")
    pl=pl.convert("L")
    output=ImageOps.fit(surface, pl.size, centering=(0.5, 0.5))
    output.putalpha(pl)
    output=output.convert("RGBA")
    output.save("./tmp/planet.png") # asciimatics seems to only take image files, not blobs

def art():
    # generate a planet graphic
    planet()
    screen = Screen.open()
    # generate a starfield & convert graphic to ascii art
    effects=[
            Stars(screen, (screen.width + screen.height) // 2),
            Print(screen, ImageFile('./planet.png', 20, colours=8), 0)
            ]
    screen.set_scenes([Scene(effects, 0)])
    # screen.draw_next_frame(repeat=False)
    # write ascii from screen object to textfile
    doc = ""
    for x in range(0, screen.dimensions[0] - 1):
        doc += "\n"
        for y in range(0, screen.dimensions[1] - 1):
            print(chr(screen.get_from(x, y)[0])) # returns a tuple, 0 = ascii code
    f = open("./tmp/planet.txt", "a")
    f.write(doc)
    f.close()

# Screen.wrapper(art)
art()

