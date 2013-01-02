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
from geneacrystal import util
import random
import math
import libavg
from libavg import avg


class Player(object):
              
    def __init__(self, pos, angle=0, area=None, hasScore = True, color="FFFFFF"):        
        self.pos = pos
        self.angle = angle
        if hasScore:
            self._score = 0
        else:
            self._score = None
        self._cannon = None
        self._structures= []
        self._area=area
        self.scoreChangeCallbacks = []
        self._sideLines = []  
        self.color = color
        
    def setCannon(self, cannon):
        self._cannon = cannon
    
    def addStructure(self, structure):
        self._structures.append(structure)
    
    def removeStructure(self, structure):
        self._structures.remove(structure)
        
    def cannonEvent(self, event):
        self._cannonOnEvent(event)
    
    def structureEvent(self, event):
        for structure in self._structures:
            structure.onEvent(event)
            
    def setOnScoreChangeCallback(self, cb):
        self.scoreChangeCallbacks.append(cb)
        
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        self._score = value
        for cb in self.scoreChangeCallbacks:
            cb(value)
            
    def isForPlayer(self, event):
        if hasattr(event, "handorientation") :
            if self._area is not None:
                if self._area.originatesFromArea(event):
                    return True
        return False
    
    def __repr__(self, *args, **kwargs):
        return "Player({player.pos},{player.quadrant})".format(player=self)
        

class StaticQuadrantPlayer(Player):
    
    def __init__(self, pos, angle, quadrant, **kwargs):
        self.quadrant = quadrant
        Player.__init__(self, pos, angle, area=self._getAreaForQuadrant(quadrant), **kwargs)      
    
   
    def _getAreaForQuadrant(self, quadrant):
        
        if quadrant[0] == -1:
            left = 0
            right = util.WINDOW_SIZE[0]/2
        else: 
            left = util.WINDOW_SIZE[0]/2
            right = util.WINDOW_SIZE[0]
            
        if quadrant[1] == -1:
            top = 0
            bottom = util.WINDOW_SIZE[1]/2
        else:
            top = util.WINDOW_SIZE[1]/2
            bottom = util.WINDOW_SIZE[1]
        return QuadPlayerArea((left,top),(right,bottom), quadrant)
            
    def __repr__(self, *args, **kwargs):
        return "StaticQuadrantPlaye({player.pos}, {player.angle},{player.quadrant})".format(player=self)
     

class StaticSlicePlayer(Player):
    
    def __init__(self, pos, angle, index, maxIndex, **kwargs):
        self.index = index
        self.maxIndex = maxIndex
        Player.__init__(self, pos, angle, **kwargs)
        self._area = self._getArea()
              
    
    def _getArea(self):
        sliceWidth = util.WINDOW_SIZE[0] / self.maxIndex
        mySliceLeftBorder = sliceWidth*self.index
        mySliceRightBorder = sliceWidth*(self.index+1)
        if __debug__:
            print mySliceLeftBorder, self.pos[0] , mySliceRightBorder
        assert(mySliceLeftBorder < self.pos[0] <mySliceRightBorder)
        
        return SlicePlayerArea(mySliceLeftBorder, mySliceRightBorder, self.index)
        
    def __repr__(self, *args, **kwargs):
        return "StaticSlicePlayer({player.pos}, {player.angle},{player.index}, {player.maxIndex})".format(player=self)
   

class PlayerArea(object):
    
    def isInArea(self, event):
        pass

    
class SlicePlayerArea(PlayerArea):
    def __init__(self, left, right, index):
        self.left =left
        self.right = right
        self.idex = index
    
    def originatesFromArea(self, event):
        eventX, eventY = event.pos
        
        baseAngle = event.handorientation + math.pi
        beta = baseAngle - 3*math.pi/2 #angle  perpendicular to y-Axis (lower left quadrant)
        alpha = math.pi/2
        gamma = 180 - beta - alpha
        dX =  (util.WINDOW_SIZE[1]- event.pos[1]) * math.sin(beta)/math.sin(alpha) #law of sines
        
        pointOfOrigin =(eventX + dX, util.WINDOW_SIZE[1])
        pointOfOriginX = pointOfOrigin[0]
        
        if __debug__:
            root = avg.Player.get().getRootNode()
            avg.CircleNode(parent=root, pos=pointOfOrigin, r=10,fillcolor="FF0000", fillopacity=1)
            print "POO", pointOfOrigin, "BA", (baseAngle/(2*math.pi))*360, "BETA", beta
        
        return self.left < pointOfOriginX < self.right
        
        
class QuadPlayerArea(PlayerArea):
    
    
    def __init__(self, upperLeftCorner, lowerRightCorner, quadrant):
        self._quadrant = quadrant
        self._upperLeftCornerX, self._upperLeftCornerY  = upperLeftCorner
        self._lowerRightCornerX , self._lowerRightCornerY = lowerRightCorner
        
    def originatesFromArea(self, event):
    
        handAngle = math.fmod(event.handorientation + math.pi , 2*math.pi)

        if self._quadrant[0] == -1 and self._quadrant[1] == -1:
            return 0<= handAngle <= math.pi/2
        elif self._quadrant[0] == 1 and self._quadrant[1] == -1:
            return math.pi/2<= handAngle <= math.pi
        elif self._quadrant[0] == -1 and self._quadrant[1] == 1:
            return 3*(math.pi/2)<= handAngle <= 2*math.pi    
        elif self._quadrant[0] == 1 and self._quadrant[1] == 1:
            return math.pi<= handAngle <= 3*(math.pi/2)
                
        return False
        
    def isInArea(self, event):
        x,y =  event.pos
        isInX = self._upperLeftCornerX <= x <= self._lowerRightCornerX
        if isInX:
            isInY = self._upperLeftCornerY <= y <= self._lowerRightCornerY
            return isInY
        return False
    
    def __repr__(self, *args, **kwargs):
        return  "QuadPlayerArea(({0},{1}),({2},{3}))".format(self._upperLeftCornerX,
                                                             self._upperLeftCornerY,
                                                             self._lowerRightCornerX,
                                                             self._lowerRightCornerY,
                                                             )
