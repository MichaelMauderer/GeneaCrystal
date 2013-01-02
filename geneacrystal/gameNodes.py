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
from geneacrystal.nodes import  HighscoreEntryNode, TouchPointNode, ShieldNode
from libavg import avg
import geneacrystal.util as util
import pymunk
from geneacrystal.physic import DebugCrystalGameSpace, CrystalGameSpace, BorderCollisionType,\
    TeleportBorderCollisionType
import itertools
import math
from geneacrystal.crystalManager import CrystalManager
from geneacrystal.gameElements.structures import CenterNodeStructure, \
    AggressiveCenterNodeStructure, CeilingStructure
from geneacrystal.player import StaticQuadrantPlayer, StaticSlicePlayer
from geneacrystal.helpSystem import HelpSystem, InfoManager
from geneacrystal import themes
from geneacrystal.gameElements import  playerBases


class ComeAndPlayGameNode(avg.DivNode):

    def __init__(self, settings, items, endCB, theme=themes.DefaultTheme,
                 infos=dict(), *args, **kwargs):
        """
        Creates a new object. 
        @param parent: the parent gameElement to append to.
        """
        avg.DivNode.__init__(self, *args, **kwargs)
        
        if __debug__:
            self.space = DebugCrystalGameSpace()
        else:
            self.space = CrystalGameSpace()
        self.__touchNodeMapping = {}
        self.__shieldNodeMapping = {}
        self._playerCannons = []
        self._endCB = endCB
        self._theme = theme   
        self._generator = CrystalManager(items, settings.get("crystals", 3))#CrystalManager(items)
        self.timers = []
        self.playerColors = ["999900", "990000", "009900", "000099"]
        self._highscore = "0"
        self._touchPointRadius = min(self.size)/40
        self._structureStartRotationSpeed = settings.get("rotation_speed", 0)*0.01
        
        if settings.get("growing_speed", 23) != 0:
            self._structureFramesToGrowth = 60*60/settings.get("growing_speed", 23) 
            self._growIncrementPerPlayer = self._structureFramesToGrowth/2
        else:
            self._structureFramesToGrowth = float("inf")
            self._growIncrementPerPlayer = 0
        self._structureStartSize = 15 #
        self._stuctureShootFrequency = 10000/settings.get("shooting_speed", 1) if settings.get("shooting_speed", 1) != 0 else float("inf")
        self._helpSystem = HelpSystem(infos)   
   
        player = avg.Player.get()
        tickTimer = player.setOnFrameHandler(lambda:self.space.step(1 / 150.0))
        self.timers.append(tickTimer)
        
        player.getTestHelper().fakeKeyEvent(avg.KEYDOWN, 17, 116, "t", 116, 0)
        
        self._setBackground()
        self._interactionDiv = avg.DivNode(parent=self, size=self.size)
        self._interactionDiv.setEventHandler(avg.CURSORDOWN, avg.TOUCH, self.__touchDown)
        self.setEventHandler(avg.CURSORUP, avg.TOUCH, self.__touchUp)
      
        self._initBorders()
        self._players = self._initPlayers(self)
        self.structures = []
        self._initGameElements(self._interactionDiv)
      
    def _setBackground(self):
        self._theme.GameBackGround(size=util.WINDOW_SIZE, parent=self)
        
    def _initBorders(self):
        corners = [(0, 0),
                   (0, util.WINDOW_SIZE[1]),
                   util.WINDOW_SIZE,
                   (util.WINDOW_SIZE[0], 0)]
        borders = [] 
        
        for a, b in zip(corners, itertools.chain(corners[1:], corners[:1])):
                a, b = a, b
                borderBody = pymunk.Body()
                shape = pymunk.Segment(borderBody, a, b, 10)
                shape.elasticity = 1
                shape.collision_type = BorderCollisionType
                self.space.add(shape)
                borders.append(borderBody)

    def _winCB(self, gameWon = False, showKeyboards=True):
        
        shadowNode = avg.DivNode(size = util.WINDOW_SIZE, parent = self.getParent())
        imageLeft = self._theme.getNode("LeftDoor")(size = util.WINDOW_SIZE,
                                                    pos=(-util.WINDOW_SIZE[0]/2, 0),
                                                    parent=shadowNode)
        imageRight = self._theme.getNode("RightDoor")(size = util.WINDOW_SIZE,
                                                      pos=(util.WINDOW_SIZE[0]/2, 0),
                                                      parent=shadowNode)
        
        def slideOutDoors():
            avg.LinearAnim(imageLeft, "pos", 1000, imageLeft.pos,
                           (-util.WINDOW_SIZE[0]/2, 0)).start()
            avg.LinearAnim(imageRight, "pos", 1000, imageRight.pos,
                           (util.WINDOW_SIZE[0]/2, 0), False, None,
                           lambda : shadowNode.unlink(True)).start()

        def doorsClosedCB():
            if not gameWon or not showKeyboards:
                avg.Player.get().setTimeout(750, slideOutDoors)
                if self._endCB is not None:
                    self._endCB(False, shadowNode)
                    self._endCB = None
            else:

                def finishedEntryCB(name):
                    self._namesToEnter -= 1
                    if self._namesToEnter == 0 and self._endCB is not None:  
                        self._endCB(False, shadowNode)
                        self._endCB = None
                        avg.Player.get().setTimeout(500, slideOutDoors)
                        
                self._makeKeyboards(finishedEntryCB, shadowNode)
 
        avg.LinearAnim(imageLeft, "pos", 1000, imageLeft.pos, (0,0)).start()
        avg.LinearAnim(imageRight, "pos", 1000, imageRight.pos, (0,0), False, None, doorsClosedCB).start()

    def _makeKeyboards(self, finishedCB, parent):
        self._namesToEnter = len(self._players)
        playerScores = []
        for player in self._players:
            playerScores.append(player.score)
        
        for player in self._players:
                
            hsen = HighscoreEntryNode(self._highscore, player.score, playerScores, finishedCB, parent=parent, size=(util.WINDOW_SIZE[0]//3,util.WINDOW_SIZE[0]//9))
            if player.angle < util.degToRad(45) or player.angle > util.degToRad(225):
                playerPos = player.pos[0], player.pos[1]- 165
            else:
                playerPos = player.pos[0], player.pos[1] + 15
            if player.angle < util.degToRad(135):
                playerPos = playerPos[0]-125, playerPos[1]
            else:
                playerPos = playerPos[0]-325, playerPos[1]
            hsen.angle = player.angle + math.pi/4
            hsen.pos=playerPos[0], playerPos[1]
    
    def _initGameElements(self, parent):  
        gameElement = CenterNodeStructure(radius=50,
                                          space=self.space,
                                          rotationSpeed=self._structureStartRotationSpeed,
                                          framesToGrowth= self._structureFramesToGrowth,
                                          startCrystals=self._structureStartSize,
                                          position=util.vectorMult(util.WINDOW_SIZE, 0.5),
                                          parent=parent,
                                          helpSystem=self._helpSystem,
                                          crystalManager=self._generator,
                                          )
       
        gameElement.depletedCallback = lambda: self._winCB(showKeyboards=False)
        gameElement.gameOverCallback = lambda: self._winCB(showKeyboards=False)
        self.structures.append(gameElement)
      
    def _initPlayers(self, parent):  
        players = []
        for x in (1,-1):
            for y in (1,-1):
                
                angle = ((x+1)/2)*math.pi + (abs(y+x)/2)*math.pi/2 
                xPos = util.WINDOW_SIZE[0]/2 + x*(util.WINDOW_SIZE[0]/2- util.WINDOW_SIZE[1]/8 )  
                yPos = util.WINDOW_SIZE[1]/2 + y*(util.WINDOW_SIZE[1]/2 - util.WINDOW_SIZE[1]/8)
                
                player = StaticQuadrantPlayer((xPos, yPos), angle, (x,y),color=self.playerColors.pop(), hasScore=False)
                infoManager = InfoManager(self._helpSystem, self._theme, owner=player)
                base = playerBases.DiagonalPlayerBase2Room( self._generator,
                                                       space=self.space, 
                                                       angle=player.angle,
                                                       parent=parent,
                                                       size=self._getCannonSize(),
                                                       position=player.pos,
                                                       owner=player,
                                                       helpSystem=self._helpSystem,
                                                       infoManager = infoManager    
          
                                                       )
                self._setBaseTimeoutForRejoin(base, util.CAP_INACTIVITY_TIMEOUT)
                base.destructionCallback = lambda: self._winCB(showKeyboards=False)
    
                players.append(player)
                player.base = base
        return players
          
    def _setBaseTimeoutForRejoin(self, base, duration): 
        
        def restoreBase():
            base.show()
            for structure in self.structures:
                structure.framesToGrowth -= self._growIncrementPerPlayer
              
        def baseTimeout():
            base.hide()
            circle = self._theme.JoinButton(parent=self)
            util.centerNodeOnPosition(circle, base.position)
            circle.angle = base.angle + math.pi/4
            circle.setEventHandler(avg.CURSORDOWN, avg.TOUCH, lambda event : restoreBase())
            for structure in self.structures:
                structure.framesToGrowth += self._growIncrementPerPlayer
              
        base.timeoutDuration = duration   
        base.timeOutCB = baseTimeout

    def _getCannonSize(self):
        sizeX = min(self.size.x, self.size.y) / 4
        return sizeX, sizeX 
            
    def toggleRotations(self):
        for structure in self.structures:
            structure.rotationEnabled = not structure.rotationEnabled
               
    def _getPlayerForEvent(self, event):
        for player in self._players:
            if player.isForPlayer(event):
                return player
        return None
            
    def __touchDown(self, event):
            
        for cannon in self._playerCannons:
            used = cannon.isTouchInCannonArea(event.pos)
            if used:
                return
        
        player = self._getPlayerForEvent(event)
        node = TouchPointNode(self.space, r=self._touchPointRadius, pos=event.pos, fillopacity=1, owner=player)
        node.eventId = event.cursorid
        
        for node2 in self.__touchNodeMapping.values():
            if (util.getDistance(node.pos, node2.pos) < util.MAX_SHIELD_DISTANCE):
                del self.__touchNodeMapping[node2.eventId]
                self.space.delayRemoveComplete(node2._body)
                self.space.delayRemoveComplete(node._body)
           
                mapping = (node2.eventId, node.eventId)
                if node.eventId < node2.eventId:
                    mapping = (node.eventId, node2.eventId)
                    shield = ShieldNode(self.space,
                                        pos1=node.pos,
                                        pos2=node2.pos,
                                        strokewidth=20,
                                        color="FF0000")
                else:
                    shield = ShieldNode(self.space,
                                        pos1=node2.pos,
                                        pos2=node.pos,
                                        strokewidth=20,
                                        color="FF0000")

    
                self.__shieldNodeMapping[mapping] = shield
                self.appendChild(shield)
                return
 
        self.__touchNodeMapping[event.cursorid] = node
        self.appendChild(node)
       
    def __touchUp(self, event):
        
        player = self._getPlayerForEvent(event)
          
        if event.cursorid in self.__touchNodeMapping:
            node = self.__touchNodeMapping[event.cursorid]
            del self.__touchNodeMapping[event.cursorid]
            self.space.delayRemoveComplete(node._body)
        else:
            for key in self.__shieldNodeMapping.keys():
                id1, id2 = key
                if id1 == event.cursorid or id2 == event.cursorid:
                    mapping = (id2, id1)
                    firstId = id2
                    secondId = id1
                    if id1 < id2:
                        mapping = (id1, id2)
                        firstId = id1
                        secondId = id2
                    
                    shield = self.__shieldNodeMapping[mapping]
            
                    self.space.delayRemove(shield._body.shape, shield._body)
                    shield.unlink(True)
                    del self.__shieldNodeMapping[mapping]
                    
                    if firstId == event.cursorid:                        
                        node = TouchPointNode(self.space,
                                              r=self._touchPointRadius,
                                              pos=shield.pos2,
                                              parent=self,
                                              fillopacity=1,
                                              owner=player)
                        node.eventId = secondId
                        self.__touchNodeMapping[secondId] = node
                    else:
                        node = TouchPointNode(self.space,
                                              r=self._touchPointRadius,
                                              pos=shield.pos1,
                                              parent=self,
                                              fillopacity=1,
                                              owner=player)
                        node.eventId = firstId
                        self.__touchNodeMapping[firstId] = node
                    return
  
    def delete(self):
        self.unlink(True)
        self._interactionDiv.unlink(True)
        self._interactionDiv = None
        self.space.delete()
        player = avg.Player.get()
        for timer in self.timers:
            player.clearInterval(timer)
            
        for player in self._players:
            player.base.delete()
            player.base= None
         
        self._players = []
        
        for structure in self.structures:
            structure.delete()
        self.structures = []
            
            
class CityDefenderGameNode(ComeAndPlayGameNode):
 
    def _initGameElements(self, parent):
        gameElement = AggressiveCenterNodeStructure(space=self.space,
                                                    radius=50,
                                                    rotationSpeed=self._structureStartRotationSpeed,
                                                    framesToGrowth= self._structureFramesToGrowth,
                                                    startCrystals=self._structureStartSize,
                                                    position=util.vectorMult(util.WINDOW_SIZE, 0.5),
                                                    parent=parent,
                                                    helpSystem=self._helpSystem,
                                                    crystalManager=self._generator,
                                                    shootFrequency = self._stuctureShootFrequency,
                                                    )
        
        gameElement.depletedCallback = lambda : self._winCB(True)
        gameElement.gameOverCallback = lambda : self._winCB(False)
        self.structures.append(gameElement)

    def __removePlayer(self, player):
        player.base.delete()
        self._players.remove(player)
        if len(self._players) == 0 or self.__cityCount == 0:
            self._winCB()
        
    def _checkAlive(self, player):
        if player in self._players:
            player.base.timeOutCB = None
                
    def _initPlayers(self, parent):
        players = []
        self.__activationTimers = {}
        self.__cityCount = 0
        
        for x in (1,-1):
            for y in (1,-1):
                angle = ((x+1)/2)*math.pi + (abs(y+x)/2)*math.pi/2 
                xPos = util.WINDOW_SIZE[0]/2 + x*(util.WINDOW_SIZE[0]/2- util.WINDOW_SIZE[1]/8 )  
                yPos = util.WINDOW_SIZE[1]/2 + y*(util.WINDOW_SIZE[1]/2 - util.WINDOW_SIZE[1]/8)
                
                player = StaticQuadrantPlayer((xPos, yPos), angle, (x,y), color=self.playerColors.pop())
                infoManager = InfoManager(self._helpSystem, self._theme, owner=player)
                players.append(player)

                self.__cityCount +=1
                base = playerBases.DiagonalPlayerBase3Room( self._generator,
                                                        space=self.space, 
                                                        angle=player.angle,
                                                        parent=parent,
                                                        size=self._getCannonSize(),
                                                        position=player.pos,
                                                        owner=player,
                                                        helpSystem=self._helpSystem,
                                                        hitPoints=5,
                                                        showExitButton=True,
                                                        infoManager=infoManager,
                                                        )
    
                avg.Player.get().setTimeout(int(util.CANNON_ACTIVATION_TIMEOUT*1.1), lambda p=player : self._checkAlive(p))
                
                base.timeoutDuration = util.CANNON_ACTIVATION_TIMEOUT
                base.timeOutCB = lambda p=player : self.__removePlayer(p)
                
                base.destructionCallback = self.informAboutDestroyedCity
                player.base = base
            
        return players
             
    def informAboutDestroyedCity(self):
        self.__cityCount -= 1
        if self.__cityCount == 0:
            self._winCB(False)
  
                
class NotEnoughPlayersException(Exception):
    pass


class VersusModeNode(ComeAndPlayGameNode):
   
    def __init__(self, numberOfPlayers=2, *args, **kwargs):

        if numberOfPlayers <1:
            raise NotEnoughPlayersException
        self.numberOfPlayers = numberOfPlayers

        ComeAndPlayGameNode.__init__(self,*args, **kwargs)
  
        self._highscore = str(numberOfPlayers-1)
        
        self.remainaingPlayers = list(self._players)
         
    def _setBackground(self):
        self._theme.VsGameBackGround(size=util.WINDOW_SIZE, parent=self)
   
    def delete(self):
        self.remainaingPlayers = []
        
        ComeAndPlayGameNode.delete(self)
   
    def _initPlayers(self, parent):     
        cannonSize = self._getCannonSize()
        players = []
        
        for playerNumber in range(self.numberOfPlayers):
            xPos = (util.WINDOW_SIZE[0] / (self.numberOfPlayers*2)) + playerNumber*util.WINDOW_SIZE[0]/(self.numberOfPlayers)
            yPos = util.WINDOW_SIZE[1] - cannonSize[1] / 2

            player = StaticSlicePlayer((xPos, yPos), 0, playerNumber,
                                       self.numberOfPlayers,
                                       color=self.playerColors.pop())
            infoManager = InfoManager(self._helpSystem, self._theme, owner=player)    
          
            base = playerBases.AlignedPlayerBase( self._generator,
                                                  space=self.space, 
                                                    angle=player.angle,
                                                    parent=parent,
                                                    size=self._getCannonSize(),
                                                    position=player.pos,
                                                    owner=player,
                                                    helpSystem=self._helpSystem,
                                                    infoManager=infoManager,
                                                    )
            base.destructionCallback = self._makeLoseCB(player)
            player.base = base
            players.append(player)
        return players   
            
    def _makeStructureWinCB(self, player):
        def cb():
            self._winCB(True, True)
            self.remainaingPlayers = [player]
        return cb
    
    def _makeLoseCB(self,player):
        def cb():
            if player not in self.remainaingPlayers:
                return
            self.remainaingPlayers.remove(player)
            
            toDel = None
            for structure in self.structures:
                if structure.owner ==player:
                    toDel = structure
                    break
            if toDel is not None:
                self.structures.remove(toDel)
                toDel.delete()
            
            if len(self.remainaingPlayers) < 2:
                self._winCB(True, True)
        return cb
    
    def _initGameElements(self, parent):
         
        for player in self._players:
            gameElement = CeilingStructure(width=150,
                                           space=self.space,
                                           position= (player.pos[0] , util.CRYSTAL_SIZE),
                                           parent=parent,
                                           helpSystem=self._helpSystem,
                                           owner = player,
                                           crystalManager=self._generator,
                                           framesToGrowth= self._structureFramesToGrowth,
                                           startCrystals=self._structureStartSize,                                   
                                           )
                  
            gameElement.depletedCallback = self._makeStructureWinCB(player)
            gameElement.gameOverCallback = self._makeLoseCB(player)
            self.structures.append(gameElement)
    
    def _makeBorder(self, a,b, collisionType):
        borderBody = pymunk.Body()
        shape = pymunk.Segment(borderBody, a, b, 1)
        shape.elasticity = 1
        shape.collision_type = collisionType
        self.space.add(shape)
  
    def _initBorders(self):
        borderOffset = util.CRYSTAL_SIZE*1.5

        topLeft = -borderOffset, 0
        topRight = util.WINDOW_SIZE[0] + borderOffset, 0
        lowerRight = util.WINDOW_SIZE[0] + borderOffset, util.WINDOW_SIZE[1]
        lowerLeft = -borderOffset, util.WINDOW_SIZE[1]  
        
        self._makeBorder(topLeft, topRight, BorderCollisionType)
        self._makeBorder(lowerLeft, lowerRight, BorderCollisionType)
        self._makeBorder(topLeft, lowerLeft, TeleportBorderCollisionType)
        self._makeBorder(topRight, lowerRight, TeleportBorderCollisionType)        

    
    def _makeKeyboards(self, finishedCB, parent):
        
        self._namesToEnter = len(self._players)
        playerScores = []
        for player in self._players:
            playerScores.append(player.score)
        
        for player in self._players:
 
            
            heading = avg.WordsNode( color="FFFFFF",
                                      fontsize=25,
                                      sensitive=False,
                                      angle=player.angle,
                                      alignment="center",
                                     )
            
            hsen = HighscoreEntryNode(self._highscore, player.score, playerScores, finishedCB, parent=parent, size=(util.WINDOW_SIZE[0]//3,util.WINDOW_SIZE[0]//9))
            hsen.angle = player.angle
            
            hsen.appendChild(heading)
 
            if player in self.remainaingPlayers:
                designation = "WINNER"
            else:
                designation = "LOSER"
            heading.text=  "{}<br/>{} Points".format(designation, player.score)
           
            util.centerNodeOnPosition(hsen, player.pos)
            util.centerNodeOnPosition(heading, util.vectorAdd((0,0), (hsen.size[0]/2, -heading.getMediaSize()[1])))

