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
from __future__ import division
from geneacrystal import util, physic
import networkx as nx
from _weakrefset import WeakSet
import pymunk
from libavg import avg
import itertools
import random
import math
from geneacrystal.gameElements import GameElementBase
from geneacrystal.helpSystem import AnnotatedObject
import logging
import collections


class StructureElement(AnnotatedObject):
    _idCounter = 0
    elementType = "None"
    nodeType = "None"
    color = None
    shapeOverflowFactor = 1.4
    
    _size = (util.CRYSTAL_SIZE,util.CRYSTAL_SIZE)
    
    def __init__(self, pos, angle, parentStructure, helpSystem=None):
        AnnotatedObject.__init__(self, helpSystem)
        self.parent = parentStructure
        self.id = StructureElement._idCounter   
        StructureElement._idCounter+=1
        self._helpSystem = helpSystem
        
        shape = self.parent._createCircleShape(self.parent.toAbsPos(pos),
                                               r=self.shapeOverflowFactor*self._size[0]/2)
        self.shape=shape
    
        self.node = self._makeNode(pos, angle)
    
        self._neigborIndicator = None
        self._neigborLines = dict()
        
    @property
    def size(self):
        return self._size
        
                  
    def _makeNode(self, pos, angle ):
        if self.nodeType == "None":
            logging.warn("No node type for element: %s" % self )
        parentNode = self.parent.getElementNodeParent()
        
        node = self.parent._theme.getNode(self.nodeType)(parent=parentNode,
                                                         size=self._size)
        node.pos = self.parent.getOffscreenPosForElement(pos)
        node.angle = angle

        self._setInfoHandler(node)
        return node
    
    @property
    def position(self):
        absPos = self.shape.body.local_to_world(self.shape.offset)
        return tuple(self.shape.body.world_to_local(absPos))
        
    def isSameType(self, other):
        if other.elementType == "All":
            return True
        if self.elementType == "None" or other.elementType == "None":
            return False
        
        return self.elementType == other.elementType
    
    def onDestroyAction(self):
        pass
    
    def onCollision(self, other):
        pass
    
    def delete(self):
        self.parent.removeElement(self)
        return self.parent.removeNotReachableElements() + 1


class ColoredElement(StructureElement):
    infoKey = "color_crystal"  
    elementType = "{color}Crystal"
    nodeType = "{color}Crystal"
    color= "{color}"
 
    
    def __init__(self, color, *args,**kwargs):
        self._adjustColor(color)
        StructureElement.__init__(self, *args, **kwargs)
        self.color = self.color.format(color=color)
        
    def _adjustColor(self, color):
        self.elementType = self.elementType.format(color=color)  
        self.nodeType = self.nodeType.format(color=color)          
        self.color = color 
   
class HiddenElement(ColoredElement):
    nodeType = "HiddenCrystal"
    infoKey = "hide_crystal"
    elementType = "{color}Crystal"
    unveiledNode = "{color}Crystal"
    
    def _adjustColor(self, color):
        ColoredElement._adjustColor(self, color)
        self.unveiledNode = self.unveiledNode.format(color=color)
        
    def onCollision(self, other):
        node = self.node
        self.node.unlink(True)
        self.node = self.parent._theme.getNode(self.unveiledNode)(parent=self.parent.getElementNodeParent(),
                                                  pos=node.pos,
                                                  angle=node.angle,
                                                  size=node.size)
        self.parent._updateElement(self)
        
               
class EaterElement(ColoredElement):
    maxEatCount = 3
    infoKey = "static_eater"
    elementType = "{color}Crystal"
    nodeType = "{color}EaterCrystal"
    
    def __init__(self,*args, **kwargs):
        ColoredElement.__init__(self, *args, **kwargs)
        self._eatCount = 1
    
    def onCollision(self, other):
        if other is None:
            return
        
        if self._eatCount < self.maxEatCount:
            self._eatCount += 1
            other.delete()
        elif self._eatCount == self.maxEatCount:
            other.delete()
            self.node.removeLayer(-1)
            self._eatCount += 1


    
class CenterCrystalElement(StructureElement):
    infoKey = "center_node"
    elementType = "None"
    nodeType = "CenterCrystal"
    _size = (2*util.CRYSTAL_SIZE, 2*util.CRYSTAL_SIZE)
    
class AggressionElement(StructureElement):
    elementType = "None"
    nodeType = "AgressiveCrystal"
    infoKey = "arms_crystal"
    
class JokerElement(StructureElement):
    elementType = "All"
    nodeType = "JokerCrystal"
       
class VeilElement(StructureElement):
    elementType = "None"
    nodeType = "VeilCrystal"
    infoKey = "veil_crystal"
    
    def onCollision(self, other):
        self.parent.veil(180)
        other.delete()
        self.delete()
        
    
class SpawnElement(StructureElement):
    elementType = "None"
    nodeType = "SpawnCrystal"
    infoKey = "spawn_crystal"
    overdriveDuration = 60 * 5 
        
    def onCollision(self, other):
        self.parent.startOverdrive(self.overdriveDuration)
        removeCounter = self.delete()
        #other.owner.points+= pointValues.BUBBLE_REMOVED_FROM_STRUCTURE * removeCounter


class IndestructibleElement(StructureElement):
    elementType = "None"
    nodeType = "IndestructibleCrystal"
    infoKey = "indestructible_crystal"
    
          
class BaseStructure(GameElementBase):
    
    neighbourhoodThreshold = 2
    REACTION_THRESHOLD = util.REACTION_THRESHOLD

    class Veil(object):
    
        def __init__(self, structure, time, stopCallback=None, fadeOutTime = 120.0, fadeInTime=120.0):
            self._structure = structure
            self._timeToVeil = time
            
            self._maxFadeOutTime = fadeOutTime
            self._fadeOutTime = fadeOutTime
            
            self._maxFadeInTime = fadeInTime
            self._fadeInTime = fadeInTime
            
            self._stopCallback = stopCallback
            
            self._action = self._veiling
            
        def onTick(self):
            if self._action is not None:
                self._action()
                 
                 
        def _veiling(self):
            if self._fadeInTime > 0:
                self._fadeInTime -= 1
                self._setVeil(self._fadeInTime/self._maxFadeInTime)
            else:
                self._action = self._veilHolding
                
        
        def _veilHolding(self):
            if self._timeToVeil > 0:
                self._timeToVeil -= 1
                self._setVeil(0)
            else:
                self._action= self._unveiling
                
        
        def _unveiling(self):
            if self._fadeOutTime > 0:
                self._fadeOutTime -= 1
                self._setVeil(1- (self._fadeOutTime / self._maxFadeOutTime))
            else:
                self._action = self._finished 
        
        def _finished(self):
            self._removeVeil()
            self._stopCallback()
            self._action = None
        
        def _setVeil(self, value):
            fxNode = avg.HueSatFXNode(0, 100*value-100, 100*value-100, False)
            self._structure._image.setEffect(fxNode)
                
        def _removeVeil(self):
            self._structure._image.setEffect(None)
            
       
            
    def __init__(self,crystalManager=None, framesToGrowth=None, startCrystals=20,
                 *args, **kwargs):
        GameElementBase.__init__(self, *args, **kwargs)
        
        if self.owner is not None:
            self.owner.addStructure(self)
        
        self._graph = nx.Graph()
        self._elementMapping = {}
                   
        self._fixElements = WeakSet()
        
        if __debug__:
            print "FRAMESTO GROWTH", framesToGrowth
        self.framesToGrowth = framesToGrowth
        self.growTimer = 0
        
        self._overDriveCounter = 0
        self._overdrive = False
        
        self._veil = None
        
        self._growLock = False
        self._depletedCallback = None
        self._gameOverCallback = None
    
        self.crystalManager = crystalManager
        if crystalManager is None:
            logging.warn("Structure {!s} has no valid CrystalManager".format(self) )
        else:
            self.crystalManager.registerStructure(self)
        
            
        self._shadowWidth = util.CRYSTAL_SIZE * StructureElement.shapeOverflowFactor**2
        if self.owner is None:
            self._shadowColor = "000000"
        else:
            self._shadowColor = self.owner.color
            
        player = avg.Player.get() 
        self._canvas = player.createCanvas(id=str(id(self)),
                                           size=(max(util.WINDOW_SIZE),max(util.WINDOW_SIZE)),
                                           handleevents=True,
                                           multisamplesamples=4,
                                           )
        
        self._blackCanvas = player.createCanvas(id=str(id(self))+"Black",
                                           size=(max(util.WINDOW_SIZE),max(util.WINDOW_SIZE)),
                                           handleevents=True,
                                           multisamplesamples=4,
                                           )
        
        self._canvasRoot = self._canvas.getRootNode()
        
        self._blackBackground = self._blackCanvas.getRootNode()
        self._shadowImage = avg.ImageNode(href="canvas:{}Black".format(id(self)),
                      parent=self._root,
                      size=(max(util.WINDOW_SIZE),max(util.WINDOW_SIZE)),
                      opacity=0.4)
        util.centerNodeOnPosition(self._shadowImage, (0,0))
        self._graphVisRoot = avg.DivNode(parent=self._canvasRoot)
                
        self._image = avg.ImageNode(href="canvas:{}".format(id(self)),
                      parent=self._root,
                      size=(max(util.WINDOW_SIZE),max(util.WINDOW_SIZE)))
        util.centerNodeOnPosition(self._image, (0,0))
        self._edgeNodes = dict()
        self._shadowNodes = dict()
        
        self._initStructureCore()
        
        assert(self.checkSanity())
        
        while len(self._graph) < startCrystals:
            self.growSimple()
        
        self.rotationEnabled = True
        self._tickTimer = None
        self._startTickTimer()  
     
    def getOffscreenPosForElement(self, pos):
        return util.vectorAdd(pos, util.vectorMult(self._canvasRoot.size, 0.5))
        
    def getElementNodeParent(self):
        return self._canvasRoot
    
    def _startTickTimer(self):
        self._stopTickTimer()
        player = avg.Player.get()
        self._tickTimer = player.setOnFrameHandler(self.onTick)
            
    def _stopTickTimer(self):
        player = avg.Player.get()
        if self._tickTimer is not None:
            player.clearInterval(self._tickTimer)
            self._tickTimer = None
            
    def delete(self):
        
        if not self.alive:
            return
        
        self._stopTickTimer()

        if self.owner is not None:
            self.owner.removeStructure(self)
        
        for element in self._elementMapping.values():
            if element.node is not None:
                element.node.unlink(True)
                element.node = None
            
        self._elementMapping = None
        
        for node in self._edgeNodes.values():
            node.unlink(True)
        
        for node in self._shadowNodes.values():
            node.unlink(True)
            
        self._edgeNodes = None
        self._shadowNodes = None
         
        self._rootParent = None
        
        self._canvasRoot.unlink(True)
        self._canvasRoot = None
        
        self._shadowImage.unlink(True)
        self._shadowImage = None
       
        self._graphVisRoot.unlink(True)       
        self._graphVisRoot= None
        
        self._image.unlink(True)
        self._image = None
        
        player = avg.Player.get()
        player.deleteCanvas(self._blackCanvas.getID())
        player.deleteCanvas(self._canvas.getID())
        
        self._blackCanvas = None
        self._canvas = None
       
        
        self._fixElements = None
        
        
        
        self.crystalManager.removeStructure(self)
        self.crystalManager = None
        
        GameElementBase.delete(self)
        
        
    def _initStructureCore(self):
        raise NotImplementedError
    
    def _updateElement(self, element):
        self._elementMapping[element.shape] = element
        self._elementMapping[element.node] = element
        self._elementMapping[element.id] = element
    
    def getElement(self, obj):
        return self._elementMapping[obj]
       
    def startOverdrive(self, duration):
        self._overDriveCounter += duration
    
    def _overdriveEnd(self):
        pass
    
    @property
    def size(self):
        return self._size
          
    def _initPhysic(self, position, angle):        
        mass = pymunk.inf
        moment = pymunk.moment_for_circle(mass, 0, 1)
        self._body = physic.BaseBody(self, mass, moment)
        self._space.add(self._body)                        
        
    def _createCircleShape(self, absPos, r=util.CRYSTAL_RADIUS):
        circle = pymunk.Circle(self._body, r, self._body.world_to_local(absPos))
        circle.collision_type = physic.StructureCollisionType
        self._addShape(circle)
        return circle
    
    @property
    def depletedCallback(self):
        return self._depletedCallback
    
    @depletedCallback.setter
    def depletedCallback(self, fun):
        self._depletedCallback=fun
    
    def veil(self, time):
        if self._veil is None:
            self._veil = BaseStructure.Veil(self, time, self._veilEnd)
            
    def _veilEnd(self):
        self._veil = None
        
    def getAllElements(self):
        return [ self.getElement(id) for id in self._graph]
        
    def onTick(self):
        
        if self._overDriveCounter > 0:
            self._overdrive = True
            self._overDriveCounter -= 1
            if self._overDriveCounter == 0:
                self._overdrive = False
                self._overdriveEnd()
        
        self.grow()
        
        if self._veil is not None:
            self._veil.onTick()    
            
    @property
    def gameOverCallback(self):
        return self._gameOverCallback
    
    @gameOverCallback.setter
    def gameOverCallback(self, fun):
        self._gameOverCallback=fun
    
    def onWallCollision(self, other):
        if self._gameOverCallback is not None:
            self._gameOverCallback()
            self.gameOverCallback = None
    
    def checkSanity(self):
        return True
  
    def updateNeigbourhoodVisualisation(self):
        if __debug__:
            if not hasattr(self, "debugNodes"):
                self.debugNodes = []
           
            while len(self.debugNodes) < self._graph.number_of_edges():
                debugNode = avg.LineNode(parent =self._root)
                debugNode.color = "FF0000"
                debugNode.strokewidth = 2
                debugNode.opacity = 0.5
                debugNode.fillopacity = 0.5
                self.debugNodes.append(debugNode)
                
            while len(self.debugNodes) > self._graph.number_of_edges():
                self.debugNodes.pop().unlink(True)
                            
            for edge, node in zip(self._graph.edges_iter(), self.debugNodes):
                nodeIdA, nodeIdB = edge
                node.unlink(False)
                node.pos1 = tuple(self.getElement(nodeIdA).shape.offset)
                node.pos2 = tuple(self.getElement(nodeIdB).shape.offset)
                self._root.appendChild(node)
        
    def removeSurplusElements(self, element):    
        assert(self.checkSanity())
        removeCounter = 0
        sameNeighbors = self.getSameExtendedNeighborhood(element)
        if self.REACTION_THRESHOLD > 0 and len(sameNeighbors) >= self.REACTION_THRESHOLD:
            for neighbor in sameNeighbors:
                    self.removeElement(neighbor)   
                    removeCounter+=1
            assert(self.checkSanity())
        
        removeCounter += self.removeNotReachableElements()
        return removeCounter
        
    def getGraphNeighbors(self, element):
        return [self.getElement(id) for id in self._graph.neighbors_iter(element.id)]
        
    def addElement(self, elementToCreate, color, relPos, rotation=0):
        assert(self.checkSanity())
        
        if color is None:
            element = elementToCreate(relPos, rotation, self, self._helpSystem)
        else:
            element = elementToCreate(color, relPos, rotation, self, self._helpSystem)
        self._updateElement(element)
        self._addElementShadow(element)
        self._graph.add_node(element.id)
        
        assert(self.checkSanity())
        self.updateNeigbors(element)    
        assert(self.checkSanity())
        
        return element
        
    def _removeEdgeNodesForElement(self, element):
        neighbors = self.getGraphNeighbors(element)
        for edge in self._graph.edges_iter([element.id] + neighbors):
            if element.id in edge:
                self._removeEdgeNodes(edge)    
                
    def _addEdgeNodes(self, edge):
        edge = tuple(sorted(edge))
        
        elementA = self.getElement(edge[0])
        elementB = self.getElement(edge[1])
        
        shadowLine = avg.LineNode(parent=self._blackBackground)
        shadowLine.color =  self._shadowColor
        shadowLine.strokewidth = self._shadowWidth
        shadowLine.opacity = 1
        shadowLine.fillopacity = 1
        shadowLine.pos1 = self.getOffscreenPosForElement(elementA.position)
        shadowLine.pos2 = self.getOffscreenPosForElement(elementB.position)
        self._shadowNodes[edge] = shadowLine
        avg.LinearAnim(shadowLine, "opacity", 700, 0, 1).start()
    
        edgeLine = avg.LineNode(parent=self._graphVisRoot)
        edgeLine.color = "F88017"
        edgeLine.strokewidth = util.CRYSTAL_SIZE*0.1
        edgeLine.opacity = 1
        edgeLine.fillopacity = 1
        edgeLine.pos1 = self.getOffscreenPosForElement(elementA.position)
        edgeLine.pos2 = self.getOffscreenPosForElement(elementB.position)
        avg.LinearAnim(edgeLine, "opacity", 5000, 0, 1).start()
        self._edgeNodes[edge] = edgeLine
        
    def _removeEdgeNodes(self, edge):
        edge = tuple(sorted(edge))
        if edge in self._edgeNodes:
            edgeNode = self._edgeNodes[edge]
            avg.LinearAnim(edgeNode, "opacity", 100, edgeNode.opacity, 0, False, None, lambda: edgeNode.unlink(True) ).start()
            del self._edgeNodes[edge]
        if edge in self._shadowNodes:
            shadowNode = self._shadowNodes[edge]
            avg.LinearAnim(shadowNode, "opacity", 700, shadowNode.opacity, 0, False, None, lambda:shadowNode.unlink(True) ).start()
            self._shadowNodes[edge].unlink(True)
            del self._shadowNodes[edge]
    
    def _addElementShadow(self, element):
        roundShadow = avg.CircleNode(parent=self._blackBackground,
                                                pos = self.getOffscreenPosForElement(element.position),
                                                r=self._shadowWidth/2,
                                                fillcolor= self._shadowColor,
                                                opacity=0,
                                                fillopacity=1,
                                                )
        avg.LinearAnim(roundShadow, "fillopacity", 700, 0, 1).start()
        self._shadowNodes[element.shape] = roundShadow
     
    def _removeElementShadow(self, element):
        self._shadowNodes[element.shape].unlink(True)
        del self._shadowNodes[element.shape]
        
    def onCrystalCollision(self, other, hitShape):
        try:
            element = self.getElement(hitShape)
        except KeyError:
            return
        
        element.onCollision(other)
    
    def getColorCount(self):
        return collections.Counter([e.color for e in self._elementMapping.values()])

    def removeElement(self, element):
        assert(self.checkSanity())
        assert isinstance(element, StructureElement)
        assert element.parent == self
                
        element.onDestroyAction()
        self._removeEdgeNodesForElement(element)
        self._removeElementShadow(element)
            
        self._graph.remove_node(element.id)
            
        self._removeShape(element.shape)
        if element in self._fixElements:
            self._fixElements.remove(element)
#            avg.LinearAnim(element.node, "opacity",1000, 1 , 0, False, None, lambda:element.node.unlink(True)).start()
#     
        if self._fixElements:
            targetPos = random.choice(list(self._fixElements)).node.pos
            avg.LinearAnim(element.node, "pos",1000, element.node.pos , targetPos, False, None, lambda:element.node.unlink(True)).start()
        else:
            avg.LinearAnim(element.node, "opacity",1000, 1 , 0, False, None, lambda:element.node.unlink(True)).start()

         
        del self._elementMapping[element.shape]
        del self._elementMapping[element.node]
        del self._elementMapping[element.id]
        
        assert(self.checkSanity())
        
        self._checkDepleted()
        
        if __debug__:
            self.updateNeigbourhoodVisualisation()
    
    
    def updateNeigbors(self, element, reset=False):
        assert(self.checkSanity())
        assert isinstance(element, StructureElement)
         
        if reset:
            self._removeEdgeNodesForElement(element)
            self._graph.remove_node(element.id)
            self._graph.add_node(element.id)
            assert len(self._graph.neighbors(element.id)) == 0
        
        for shape in self.getPhysicNeigbors(element):   
            shapeId = self.getElement(shape).id
            if shapeId in self._graph:
                self._graph.add_edge(element.id, shapeId)
                self._addEdgeNodes((element.id, shapeId))
                   
        assert(self.checkSanity())
        
        
        if __debug__:
            self.updateNeigbourhoodVisualisation()
                    
    def getPhysicNeigbors(self, element):
        shape = element.shape
        testBody = pymunk.Body()
        testBody.position = self._body.local_to_world(shape.offset)
        toTest = pymunk.Circle(testBody, self.neighbourhoodThreshold * util.CRYSTAL_SIZE/2)
        result = self._space.shape_query(toTest)
        result = filter(lambda s: s in self._shapes, result)   
        return result

            
    def randomizeNeighbors(self, element):
        spatialInfo = []
        for element in list(self.getGraphNeighbors(element)):
            spatialInfo.append((element.position, element.node.angle))
            self.removeElement(element)
        for pos, angle in spatialInfo:
            color, toCreate = self.crystalManager.getNextStructureElement(self)
            self.addElement(toCreate,color, pos, angle)
         
    
    def _checkDepleted(self):
        if len(self._graph) == 0 and self.depletedCallback is not None:
            self._depletedCallback()
            self._depletedCallback = None
        
    def removeNeighbors(self, element):
        for element in list(self.getGraphNeighbors(element)):
            self.removeElement(element)

    def _swapShapes(self, elementA, elementB):
        assert self.checkSanity()
      
        if (elementA in self._fixElements) ^ (elementB in self._fixElements):
            if elementA in self._fixElements:
                self._fixElements.remove(elementA)
                self._fixElements.add(elementB)
            elif elementB in self._fixElements:
                self._fixElements.remove(elementB)
                self._fixElements.add(elementA)
            
        elementA.shape, elementB.shape = elementB.shape, elementA.shape
        
        self._updateElement(elementA)
        self._updateElement(elementB)
        
        assert self.checkSanity()
    
    def getSameExtendedNeighborhood(self, element):
        assert(self.checkSanity())
        neighbourFilter = filter(lambda otherId: element.isSameType(self.getElement(otherId)), self._graph)
        subGraph = self._graph.subgraph(neighbourFilter)
        for graph in nx.connected_components(subGraph):
            if element.id in graph:
                assert(self.checkSanity())
                return [self.getElement(i) for i in graph ]
        else:
            assert(self.checkSanity())
            return []
    
    def removeNotReachableElements(self):
        toRemove = []
        removeCounter = 0
        for graph in nx.connected_component_subgraphs(self._graph):
            if all(element.id not in graph for element in self._fixElements):
                toRemove.append(graph)
                
        for graph in toRemove:
            for element in [self.getElement(i) for i in graph]:
                self.removeElement(element)
                removeCounter +=1
                
        return removeCounter
                
#    def writeState(self):
#            assert(self.checkSanity())
#            nodes = []
#            for i, node in self._idNodeMapping.items():
#                if node is not self:
#                    nodes.append((i,
#                                  node.itemType,
#                                  node.pos.x,
#                                  node.pos.y,
#                                  node.shape.offset[0],
#                                  node.shape.offset[1]))
#                else:
#                    nodes.append((0,
#                                  node.itemType,
#                                  node.pos.x,
#                                  node.pos.y,
#                                  0,0))
#                
#            edges= []    
#            for a,b in self._graph.edges_iter():
#                if a == id(self): a=0
#                if b == id(self): b=0
#                edges.append((a,b))
#            
#            with open("test", "w") as outFile:
#                pickle.dump((nodes,edges), outFile)
#            assert(self.checkSanity())
#    
#    def loadState(self, filename):
#        assert(self.checkSanity())
#        nodes, edges = pickle.load(filename)
#        
#        nodeMapping = dict()
#        
#        for i, crystalType, posX, posY, offsetX, offsetY in nodes:
#            if i == 0:
#                nodeMapping[i] = self
#                self._graph.add_node(id(self))
#            else:
#                nodeMapping[i]  = self.addElement(crystalType,
#                                               (posX,posY),
#                                               (offsetX, offsetY),
#                                               False)
#            self._idNodeMapping[id(nodeMapping[i])]= nodeMapping[i]
#            
#        for a,b in edges:
#            self._graph.add_edge(id(nodeMapping[a]), id(nodeMapping[b]) )
#        assert(self.checkSanity())
#            
    def grow(self):
        if self._growLock:
            return
        
        if self._overdrive:
            pass
        elif  self.framesToGrowth is None:
            return
        elif self.growTimer < self.framesToGrowth:
            self.growTimer +=1  
            return
        else:
            self.growTimer = 0
               
        newNode = self.growOutwards()
        #self.growSimple()
       
    def growOutwards(self):
        newSpot, elementChain = self.getRandomDestinationPath()
  
        if  newSpot is None:
            return
  
        color, crystalType = self.getElementTypeToGrow()
        
        newElement = self.addElement(crystalType,color, newSpot)
        
        for element in reversed(elementChain[1:]):  
            self._swapShapes(element, newElement)
            
        for element in elementChain[1:]:
            self.updateNeigbors(element, True)
        self.updateNeigbors(newElement, True)
         
        newElement.node.pos = elementChain[0].node.pos
        newPositions = itertools.chain([element.node.pos for element in elementChain[1:]], (self.getOffscreenPosForElement(newSpot),))
        elementChain = itertools.chain((newElement,), elementChain[1:])
        
        self._growLock = True
        for element, newPosition in zip(elementChain, newPositions): 
            avg.LinearAnim(element.node, "pos", 1000, element.node.pos, newPosition).start()
        
        avg.LinearAnim(newElement.node, "opacity", 1000, 0, 1, False, None, self._resetGrowLock).start()
        
        assert self.checkSanity()
        
    def _resetGrowLock(self):
        self._growLock = False
        
    def getRandomDestinationPath(self):
        newSpot, targetElement  = self.searchSpot() 
        if targetElement is None:
            return None, None
        assert isinstance(targetElement, StructureElement)
        paths = []
        for fixElement in self._fixElements:
            try:
                path = nx.shortest_path(self._graph,
                                    fixElement.id,
                                    targetElement.id)
                paths.append(path)
            except nx.exception.NetworkXNoPath:
                pass  
        if not paths:
                return None, None
        shortestPath = min(paths, key=len)  
        return  newSpot, map(lambda x: self.getElement(x), shortestPath) 
         
    def growSimple(self):
        newSpot, adjacentElement = self.searchSpot()
        if newSpot:
            color, crystalType = self.getElementTypeToGrow()
            element = self.addElement(crystalType, color, relPos=newSpot)
            return element    
        
    def getElementTypeToGrow(self):
        return self.crystalManager.getNextStructureElement(self)
            
    def removeElementsInArea(self, pos, radius):
        deletedelements = 0
        for shape in self._getShapesInCircle(pos, radius):
            if shape in self._elementMapping:
                deletedelements+= self.getElement(shape).delete()
        return deletedelements
    
    def _getShapesInCircle(self, pos, radius):
        testBody = pymunk.Body()
        testBody.position = pos
        shapeToTest = pymunk.Circle(body=testBody, radius=radius)
        intersections = self._space.shape_query(shapeToTest) 
        return  intersections
         
    def searchSpot(self):
        if self._graph.nodes():
            spots = []
            
            if not self._fixElements:
                return None,None
            
            fixelement = random.choice(list(self._fixElements))
            spots = self.checkForSpace(fixelement)
            spots =self._filterSpots(spots, fixelement)
            if spots:
                return random.choice(spots), fixelement
        
            node = random.choice(self._graph.nodes())
            element = self.getElement(node)
            spots = self.checkForSpace(element)
            spots =self._filterSpots(spots, element)
            if spots:
                return random.choice(spots), element
    
        return None,None
    
    def _filterSpots(self, spots, origin):
        return spots
            
    def checkForSpace(self, element):
        radius = element.shape.radius + util.CRYSTAL_RADIUS + 1
        availablePositions = []
        stepsize = 360//4
        maxNeigbors = 0
        for alpha in range(0, 360, stepsize):
            alpha += random.randint(0, stepsize-1)
            #alpha+= random.randrange(stepsize)
            angle = (2*math.pi)*(alpha/360.0)
            vector = util.getVectotInDirection(angle, radius)
            posToCheck = util.vectorAdd(self.toAbsPos(element.position), vector)
            testBody = pymunk.Body()
            testBody.position = posToCheck
            shapeToTestInner = pymunk.Circle(body=testBody, radius=util.CRYSTAL_SIZE/2)
            shapeToTestOuter = pymunk.Circle(body=testBody, radius=(util.CRYSTAL_SIZE/2)*self.neighbourhoodThreshold)
            intersectionsInner = self._space.shape_query(shapeToTestInner) 
            #dnode = avg.CircleNode(parent=self._root.getParent(), pos=posToCheck, r=util.CRYSTAL_SIZE/2,fillcolor="00FFFF", strokewidth=0)
            if len(intersectionsInner) == 0 or (len(intersectionsInner) == 1 and element.shape in intersectionsInner) :
                intersectionsOuter = self._space.shape_query(shapeToTestOuter)
                neighborCount = len(intersectionsOuter)
                #dnode.fillopacity=0.5
                if neighborCount > maxNeigbors:
                    maxNeigbors = neighborCount
                    availablePositions = [self.toRelPos(posToCheck)]
                elif neighborCount == maxNeigbors:
                    availablePositions.append(self.toRelPos(posToCheck))

        return availablePositions
        
class CenterNodeStructure(BaseStructure):
    
    monsterThreshold = 10
    
    def __init__(self,  radius, *args, **kwargs):
        self._centerRadius = radius
        self._crystalCount = 0
        BaseStructure.__init__(self, *args, **kwargs)
        
    def startOverdrive(self, duration):
        BaseStructure.startOverdrive(self, duration)
        self._overDriveAnim = avg.ContinuousAnim(self.centerElement.node, "angle", self.centerElement.node.angle, 3)
        self._overDriveAnim.start()
 
    def _overdriveEnd(self):
        self._overDriveAnim.abort()
        self._overDriveAnim = None
    
    def _changeCrystalCount(self, value):
        self._crystalCount+= value
        
        if self._crystalCount <= self.monsterThreshold:
            newOpacity = (self._crystalCount/self.monsterThreshold)
            avg.LinearAnim(self._monsterNode,"opacity", 500, self._monsterNode.opacity, newOpacity).start()
        
    def addElement(self, elementToCreate,color, relPos, rotation=0):
        self._changeCrystalCount(1)
        return BaseStructure.addElement(self, elementToCreate, color,  relPos, rotation=rotation)
        
    def removeElement(self, element):
        if element is self.centerElement:
            return
        self._changeCrystalCount(-1)
        BaseStructure.removeElement(self, element)
        
    def _checkDepleted(self):
        if len(self._graph) <= 1 :
            def cb():
                if self.depletedCallback is not None:
                    self._depletedCallback()
                    self._depletedCallback = None
            self.endAnimation(True, cb)
           
    def _filterSpots(self, spots, origin):
        originDistance = util.pointDistance(origin.position, self.centerElement.position)
        return filter(lambda position: util.pointDistance(position, self.centerElement.position) > originDistance, spots)
        
    def _initStructureCore(self):
        element = CenterCrystalElement(self.toRelPos(self._body.position),
                                       0, self, self._helpSystem)
        self._rainbowNode = element.node
        self._monsterNode = self._theme.MonsterCrystal(parent=self._rainbowNode,
                                                      pos = (0,0),
                                                      size=self._rainbowNode.size)
        
        self.centerElement = element
        self._updateElement(element)
        self._fixElements.add(element)
        self._graph.add_node(element.id)
        
    def _deleteLibavg(self):
        BaseStructure._deleteLibavg(self)
        self.centerElement = None
        self._rainbowNode = None
        self._monsterNode = None
        
    def onWallCollision(self, other):
        def cb():
            if self._gameOverCallback is not None:
                self._gameOverCallback()
                self.gameOverCallback = None
        self.endAnimation(False,cb)
          
    def endAnimation(self, won, endCallback=None):
        if won:
            node = self._rainbowNode
            self._monsterNode.unlink(False)
        else:
            node = self._monsterNode
        node.unlink(False)
        self._rootParent.getParent().appendChild(node)
        node.pos=self.position
        maxSize = min(util.WINDOW_SIZE),min(util.WINDOW_SIZE)
        animTime = 2000
        
        rotationAnim= avg.LinearAnim(node, "angle",
                              animTime,
                              node.angle,math.pi*4 + (2*math.pi - node.angle),
                              False, None,None)
        rotationAnim.start()
 
        
        growAnim = avg.LinearAnim(node, "size",
                              int(animTime),
                              node.size, maxSize,
                              False, None, None)
        
        avg.Player.get().setTimeout(int(1.1*animTime),endCallback)
        
        growAnim.start()
        
        
class CeilingStructure(BaseStructure):
    
    def __init__(self, width, *args, **kwargs):
        self._width = width
        BaseStructure.__init__(self, *args, **kwargs)
    
    def _initStructureCore(self):
        color, cls = self.crystalManager.getNextStructureElement(self)
        element = self.addElement(cls, color, (0,0))
        self._fixElements.add(element)
        
        for i in range(1,self._width//util.CRYSTAL_SIZE):
            color, cls = self.crystalManager.getNextStructureElement(self)
            element =self.addElement(cls, color, ( i*util.CRYSTAL_SIZE,0))
            self._fixElements.add(element)
            color, cls = self.crystalManager.getNextStructureElement(self)
            element = self.addElement(cls, color,(- i*util.CRYSTAL_SIZE,0))
            self._fixElements.add(element)
            
    def _filterSpots(self, spots, origin):
        yPos = origin.position[1] 
        result = filter(lambda position:  yPos - position[1] < 0 , spots)
        result = filter(lambda position: 0 < self.toAbsPos(position)[0] < util.WINDOW_SIZE[0], result)
        return result
        
    
class AggressiveCenterNodeStructure(CenterNodeStructure):
    
    def __init__(self,  shootFrequency= 120, *args, **kwargs):
        self._shootingElements = []
        CenterNodeStructure.__init__(self, *args, **kwargs)
        self._shootTimer = 0
        self.shootFrequency = shootFrequency
        
    def delete(self):
        self._shootingElements = None
        return CenterNodeStructure.delete(self)
    
    def addElement(self, elementToCreate,color, relPos, rotation=0):
        element = CenterNodeStructure.addElement(self, elementToCreate, color, relPos, rotation=rotation)
        if isinstance(element, AggressionElement):
            self._shootingElements.append(element)
        return element
    
    def removeElement(self, element):
        if isinstance(element, AggressionElement):
            self._shootingElements.remove(element)
        return CenterNodeStructure.removeElement(self, element)
        
    def getAggressionElement(self): 
        if self._shootingElements:
            return random.choice(self._shootingElements)
    
    def shoot(self):
        elementToShoot = self.getAggressionElement()
        if elementToShoot is None:
            return
        spots = self.checkForSpace(elementToShoot)
        if spots:
            from geneacrystal.gameElements import items
            spot = self.toAbsPos(random.choice(spots))
            c = items.BulletCrystal(self._space,
                                 self._root.getParent(),
                                 spot,
                                 helpSystem=self._helpSystem)
            impuls = util.vectorSub(c.position, self.toAbsPos(elementToShoot.position))
            impuls = util.vectorMult(impuls, 10)
            c._body.apply_impulse(impuls)

    def onTick(self):
        CenterNodeStructure.onTick(self)
        
        tickToAdd = len(self._shootingElements)
        self._shootTimer+= tickToAdd if not self._overdrive else 2*tickToAdd
        if self._shootTimer > self.shootFrequency:
            self._shootTimer = 0
            self.shoot()
    
class EditorStructureNode(CenterNodeStructure):
    REACTION_THRESHOLD = -1
        