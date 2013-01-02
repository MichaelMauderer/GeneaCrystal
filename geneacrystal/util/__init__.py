# GeneaCrystal Copyright (C) 2012-2013
#    Christian Jaeckel, <christian.doe@gmail.com>
#    Frederic Kerber, <fkerber@gmail.com>
#    Pascal Lessel, <maverickthe6@gmail.com>
#    Michael Mauderer, <mail@michaelmauderer.de>
#
# GeneaCrystal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GeneaCrystal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GeneaCrystal. If not, see <http://www.gnu.org/licenses/>.
import math
import csv
import libavg as avg
import os

WINDOW_SIZE = 1280, 800

REACTION_THRESHOLD = 3

MAX_SHIELD_DISTANCE = 200

CRYSTAL_SIZE = 40
CRYSTAL_RADIUS = CRYSTAL_SIZE/2

CRYSTAL_MASS = 1

DATA_PATH = "media/"

IMAGE_PATH = os.path.join(DATA_PATH, "graphics/")
XML_PATH =  os.path.join(DATA_PATH, "xml/")

HIGHSCORE_PATH = os.path.expanduser("~/")

CANNON_ACTIVATION_TIMEOUT = 15000

CAP_INACTIVITY_TIMEOUT = 50000

MAX_HIGHSCORE_LENGTH = 10

def transformVector(v):
    x,y = v
    return x,y

def vectorAdd(v1, v2):
    x1,y1 = v1
    x2,y2 = v2
    return x1+x2,y1+y2

def vectorSub(v1, v2):
    x1,y1 = v1
    x2,y2 = v2
    return x1-x2,y1-y2

def vectorMult(v, m):
    x,y = v
    return x*m, y*m

def vectorLength(v):
    x,y = v
    return math.sqrt(x**2 +y**2)

def pointDistance(p1, p2):
    v = vectorSub(p1, p2)
    return vectorLength(v)

def getVectotInDirection(angle, length=1):
    return math.cos(angle)*length , math.sin(angle)*length

def getDirOfVector(v):
    x,y = v
    alpha = math.acos(y/math.sqrt(x**2 + y**2))
    beta =  math.acos(x/math.sqrt(x**2 + y**2))
    return -alpha if beta < math.pi/2 else alpha 

def vectorNormalize(v):
    x,y = v
    l = vectorLength(v)
    if l == 0:
        return 0,0
    else:
        return x/l,y/l

def vectorGetDirWithLength(p1,p2,length=1):
    v = vectorSub(p1, p2)
    v = vectorNormalize(v)
    v = vectorMult(v, length)
    return v

def getDirInRad(v):
    x,y = v
    return math.acos(x/vectorLength(v))

def centerNodeOnPosition(node, position):
    position = vectorAdd(position, vectorMult(node.size, -0.5))
    node.pos = position

def getDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def degToRad(deg):
    return 2*math.pi * (deg/360.0)

def radToDeg(rad):
    return rad * 360.0 / (2 * math.pi)

def getLogger(name):
    logger = avg.Logger.get()
    def log(msg):
        logger.trace(avg.Logger.APP, "%s: %s" % (name, msg))
    return log
        
