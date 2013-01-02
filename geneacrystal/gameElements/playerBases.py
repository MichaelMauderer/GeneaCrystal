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
from geneacrystal import gameElements, physic, util
import pymunk
from libavg import avg
from geneacrystal.gameElements import items, GameElementBase
import math
from geneacrystal.nodes import StaticOverlayNode


class PlayerBase(GameElementBase):
        
    def __init__(self, crystalGenerator, hitPoints=None, timeoutDuration=None,
                 showExitButton=True, infoManager=None, *args, **kwargs):
        self._crystalGenerator = crystalGenerator
        self._maxHitPoints = hitPoints
        self._hitPoints = self._maxHitPoints
        
        GameElementBase.__init__(self, *args, **kwargs)
        
        self._timeoutCallback = None
        self._timeoutTimer = None  
        self.timeoutDuration = timeoutDuration

        self.destructionCallback = None
                
        self._spawnPos = self._getSpawnPos()
        
        self._infoManager = infoManager        
        self._scoreDisplay = None
        self._exitButton = None
        if self.owner is not None:
            self.owner.setCannon(self)
            if infoManager is not None:
                button, box = self._makeInfoElements()
                self._placeInfoElements(button, box)
            self._scoreDisplay = self._makeScoreCounter()
            if self._scoreDisplay is not None:
                self._alignScore(self._scoreDisplay)
            self.owner.setOnScoreChangeCallback(self._setScore)
            
        if showExitButton:
            self._makeExitButton()
                
        self.startCrystalSpawn()
        
    def _setScore(self, value):
        if self._scoreDisplay is not None:
            self._scoreDisplay.text = str(value)
            self._alignScore(self._scoreDisplay)
            
    def _alignScore(self, scoreNode ):
        self._scorePosition = (-self.size[0]*0.18+self.size[0]*0.01,
                               -self.size[1]*0.18-self.size[1]*0.01)
        util.centerNodeOnPosition(scoreNode, self._scorePosition)
        scoreNode.angle = math.pi/4
        
    @property
    def timeOutCB(self):
        return self._timeoutCallback

    @timeOutCB.setter
    def timeOutCB(self, value):
        self._timeoutCallback = value
        self._activateTimeOut()

    def _activateTimeOut(self):
        if self._timeoutTimer is not None:
            avg.Player.get().clearInterval(self._timeoutTimer)
        if self._timeoutCallback is not None and self.timeoutDuration is not None:
            self._timeoutTimer = avg.Player.get().setTimeout(self.timeoutDuration,
                                                             self._timeoutCallback)

    def _resetTimeout(self):
        self._activateTimeOut()
        
    def _getSpawnPos(self):
        raise NotImplementedError
  
    def _placeInfoElements(self):
        raise NotImplementedError
    
    def _getCreateCrystalIfEmpty(self):
        if self.getItemOnLauncher() is not None:
            return
        self._resetTimeout()
        
        color, crystalClass = self._crystalGenerator.getNextItemOrCrystalConstructor()
        if color is None:
            crystal = crystalClass(space = self._space,
                                 parent=self._root.getParent(),
                                 position = self._spawnPos,
                                 owner=self.owner,
                                 helpSystem=self._helpSystem
                                 )
        else:
            crystal = crystalClass(color=color,
                                  space = self._space,
                                 parent=self._root.getParent(),
                                 position = self._spawnPos,
                                 owner=self.owner,
                                 helpSystem=self._helpSystem
                                 )
        crystal.rotationSpeed = 2
        crystal.rotatioNenabled = True
        
    def getItemOnLauncher(self):
        shape = self.getShapesOnLauncher()
        if shape is None or not isinstance(shape.body.gameElement, items.Item):
            return None
        else:
            crystal = shape.body.gameElement
            return crystal    
        
    def getShapesOnLauncher(self):
        intersectionShapes = self._space.shape_query(self._sensorShape)
        intersectionShapes = filter(lambda shape: isinstance(shape.body,physic.BaseBody),
                                    intersectionShapes)
        intersectionCircles = filter(lambda shape: isinstance(shape.body.gameElement,
                                                              items.Item),
                                     intersectionShapes)

        if len(intersectionCircles) == 0:
            return None
        else:
            return intersectionCircles[0]
        
    def _initPhysic(self, position, angle):        
        self._body = physic.BaseBody(self, None,None)
        self._body.position = position
        self._body.angle = angle
        points = [(0,0), (self.size[0],0), self.size, (0,self.size[1])]
        points = map(lambda p: util.vectorSub(p, util.vectorMult(self.size, 0.5)),
                     points)
        shape = pymunk.Poly(self._body, points)
        shape.collision_type = physic.CannonCollisionType
        shape.elasticity = 1
        self._addShape(shape)
        
        sensorPoints = map(lambda p: util.vectorMult(p, 0.9), points)
        self._sensorShape = pymunk.Poly(self._body, sensorPoints)
        self._sensorShape.sensor = True
        self._addShape(self._sensorShape)
        
        self._addLaunchAreaDivider()
        
    def _setBackground(self):
        pass
    
    def _initLibavg(self, root):
        self._setBackground()
        if self._hitPoints is not None:
            self._makeLifebars()
        
    def onCrystalCollision(self, other,  dX, dY):
        return dX > self.size[0]/2 or dY > self.size[1]/2
            
    def delete(self):
        if not self.alive:
            return
        self.stopCrystalSpawn()
        
        if self.destructionCallback is not None:
                self.destructionCallback()
                self.destructionCallback = None
        
        if self.owner is not None:
            self.owner.setCannon(None)
            self.owner.scoreChangeCallbacks = []
        
        crystal = self.getItemOnLauncher()
        if crystal is not None:
            crystal.delete()
        
        if self._exitButton is not None:
            self._exitButton.unlink(True)
            self._exitButton = None
            
        if self._scoreDisplay is not None:
            self._scoreDisplay.unlink(True)
            self._scoreDisplay = None
                     
        if self._timeoutTimer is not None:
            avg.Player.get().clearInterval(self._timeoutTimer)
        self._timeoutCallback = None
      
        gameElements.GameElementBase.delete(self)
            
    def applyDamage(self, value):
   
        if self._hitPoints is None or not self.alive:
            return
        
        self._hitPoints -= value
        
        if self._hitPoints <=0:
            self.delete()
            return
        
        greenSizeY = self._lifeBarLength * self._hitPoints/self._maxHitPoints
        
        redSizeY = self._lifeBarLength - greenSizeY
        redPosY = self._lifeBarLength - redSizeY
        
        self._lifebarGreen.size = self._lifebarGreen.size[0], greenSizeY
        
        self._lifebarRed.pos = self._lifebarRed.pos[0], redPosY
        self._lifebarRed.size = self._lifebarRed.size[0], redSizeY
 
    def _makeLifebars(self):
        lifebarDiv = avg.DivNode(parent=self._root)
        lifebarDiv.angle = -math.pi/4
        lifebarDiv.pos = -self.size[1]*0.10,-self.size[1]*0.44
        
        self._lifeBarLength = math.sqrt(self.size[0]**2+self.size[1]**2)*0.5
        
        self._lifebarGreen = avg.RectNode(pos=(0,0),
                                              parent=lifebarDiv,
                                              fillcolor="00FF00",
                                              color="000000",
                                              fillopacity=0.5,
                                              size=(self.size[0]/20, self._lifeBarLength),
                                              )

        self._lifebarRed = avg.RectNode(pos =(0,self._lifeBarLength),
                                            parent=lifebarDiv,
                                            fillcolor="FF0000",
                                            color="000000",
                                            fillopacity=0.5,
                                            size=(self.size[0]/20, 0),
                                              )
        
    def hide(self):
        GameElementBase.hide(self)
        crystal = self.getItemOnLauncher()
        if crystal is not None:
            crystal.delete()
        self.stopCrystalSpawn()
            
    def show(self):
        GameElementBase.show(self)
        crystal = self.getItemOnLauncher()
        if crystal is not None:
            crystal.delete()
        self.startCrystalSpawn()
            
    def onStructureCollision(self, other):
        self.delete()
        
    def stopCrystalSpawn(self):
        avg.Player.get().clearInterval(self._spawnTimer)
        
    def startCrystalSpawn(self):
        player = avg.Player.get()
        self._spawnTimer = player.setInterval(500, self._getCreateCrystalIfEmpty)
        
    def _makeInfoElements(self):
        minSize = min(self._parent.size)*0.85
        
        infoButtonSize = self.size[0]/3,self.size[1]/3
        infoButton = self._infoManager.getInfoButton(parent=self._root, size=infoButtonSize)
         
        util.centerNodeOnPosition(infoButton, (0,0))
        
        infoBox = self._infoManager.getInfoBox(parent=self._root, size =(minSize/3, minSize/4) )
        util.centerNodeOnPosition(infoBox, (0,0))

        return infoButton, infoBox
    
    def _makeExitButton(self):
        pos = self.size[0]*0.1, -self.size[1] *0
        self._exitButton = StaticOverlayNode(self.delete, parent=self._root,
                                             size=util.vectorMult(self.size, 0.25),
                                             pos=pos)

    def _makeScoreCounter(self):
        pass
        
        
class DiagonalPlayerBase3Room(PlayerBase):
    
    infoKey = "breakable_base"
    
    def _getSpawnPos(self):
        spawnPos = util.vectorMult((self.size[0], -self.size[1]), 0.5)
        spawnPos = util.vectorSub(spawnPos, (util.CRYSTAL_SIZE,-util.CRYSTAL_SIZE)) 
        spawnPos = self._root.getAbsPos(spawnPos)
        return spawnPos
    
    def _placeInfoElements(self, button, box):
        button.angle = math.pi/4
        box.angle = math.pi/4
        
        angle =   -math.pi/4
        baseDisplacement = math.sqrt(2*(self.size[0]**2)) /2.0
        infoButtonElementAdjustemnt = util.getVectotInDirection(angle ,
                                                            -baseDisplacement + math.sqrt(2*(button.size[1]**2))/2)
        infoBoxElementAdjustemnt = util.getVectotInDirection(angle,
                                                            baseDisplacement + box.size[1]/2)
     
        util.centerNodeOnPosition(button, infoButtonElementAdjustemnt)
        util.centerNodeOnPosition(box, infoBoxElementAdjustemnt)
        
    def _setBackground(self):
        self._theme.BaseDiagonal3Room(parent=self._root, size=self.size)
        
    def _addLaunchAreaDivider(self):
        a = -self.size[0]*0.15, -self.size[1]/2
        b=self.size[0]/2, self.size[1]*0.15
        divider = pymunk.Segment(self._body, b, a, 1)
        divider.elasticity = 1   
        self._addShape(divider)
        
    def _makeExitButton(self):
        pos = self.size[0]*0.065, self.size[1] *0.065
        self._exitButton = StaticOverlayNode(self.delete, parent=self._root,
                                             size=(50,50), pos=pos, angle=math.pi/4)

    def _makeScoreCounter(self):
        scoreCounter = avg.WordsNode( color="FFFFFF", fontsize=25,
                                      parent = self._root, text = "0",
                                      sensitive=False,
                                      #alignment="center",
                                     )
        return scoreCounter


class DiagonalPlayerBase2Room(DiagonalPlayerBase3Room):
    
    infoKey = "simple_base"
    
    def _placeInfoElements(self, button, box):

        button.angle = math.pi/4
        box.angle = math.pi/4
        
        angle =   -math.pi/4
        baseDisplacement = math.sqrt(2*(self.size[0]**2)) /2.0
        
        infoBoxElementAdjustemnt = util.getVectotInDirection(angle,
                                                            baseDisplacement + box.size[1]/2)
     
        util.centerNodeOnPosition(button, (self.size[0]*0.17, self.size[1]*0.2))
        
        util.centerNodeOnPosition(box, infoBoxElementAdjustemnt)
        
    def _setBackground(self):
        self._theme.BaseDiagonal2Room(parent=self._root, size=self.size)
  
    def _makeExitButton(self):
        pos = -self.size[0]*0.29, -self.size[1] *0.29
        self._exitButton = StaticOverlayNode(self.delete, parent=self._root,
                                              size=util.vectorMult(self.size, 0.25),
                                               pos=pos,
                                              angle=math.pi/4)
        
    def _makeScoreCounter(self):
        return None
    
    
class AlignedPlayerBase(PlayerBase):
    
    infoKey = "score_base"
    
    def _getSpawnPos(self):
        spawnPos = 0, -self.size[1]/2
        spawnPos = util.vectorAdd(spawnPos, (0,util.CRYSTAL_SIZE)) 
        spawnPos = self._root.getAbsPos(spawnPos)
        return spawnPos

    def _placeInfoElements(self, button, box):
        angle =  math.pi/2
        baseDisplacement = math.sqrt(2*(self.size[0]**2)) /2.0
        infoBoxElementAdjustemnt = util.getVectotInDirection(angle,
                                                            -baseDisplacement - box.size[1]/2)
     
        buttonPos =  (-self.size[0]*0.23, self.size[1]*0.27)
        button.size = util.vectorMult(self.size, 0.20) 
        util.centerNodeOnPosition(button, buttonPos)
        util.centerNodeOnPosition(box, infoBoxElementAdjustemnt)

        util.centerNodeOnPosition(box, infoBoxElementAdjustemnt)

    def _setBackground(self):
        self._theme.BaseAligned(parent=self._root, size=self.size)
        
    def _makeScoreCounter(self):
        scoreCounter = avg.WordsNode( color="FFFFFF", fontsize=20,
                                      parent = self._root, text = "0",
                                      sensitive=False,
                                     )
        return scoreCounter
        
    def _alignScore(self, scoreNode):
        scorePos = (self.size[0]*0, -self.size[1]*0.015)
        util.centerNodeOnPosition(scoreNode, scorePos)
        
    def _addLaunchAreaDivider(self):
        a = -self.size[0]/2, -self.size[1]*0.1
        b=self.size[0]/2, -self.size[1]*0.1
        divider = pymunk.Segment(self._body, b, a, 0)
        divider.elasticity = 1
        self._addShape(divider)
              
    def _makeExitButton(self):
        pos = self.size[0]*0.125, self.size[1] *0.165
        self._exitButton = StaticOverlayNode(self.delete, parent=self._root,
                                             size=util.vectorMult(self.size, 0.2),
                                             pos=pos)

