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
from geneacrystal import util, physic
import pymunk
from geneacrystal.gameElements import GameElementBase, structures
from libavg import avg, ui
from geneacrystal.util import pointValues


class Item(GameElementBase):

    itemType = None
    infoKey = "item"
    color = None
    
    mass = util.CRYSTAL_MASS
    size = util.CRYSTAL_SIZE, util.CRYSTAL_SIZE
    r = util.CRYSTAL_RADIUS 
    collisionType = physic.CrystalCollisionType

    def _initPhysic(self, position, angle):
        moment = pymunk.moment_for_circle(self.mass, 0, self.size[0]/2)
        self._body = body =  physic.BaseBody(self,self.mass, moment)
        
        shape = pymunk.Circle(body,self.size[0]/2)
        shape.collision_type = self.collisionType
        shape.elasticity = 1
        self._circle = shape
        self._space.add(body)
        self._space.add(shape)
        
    def _deletePhysic(self):
        self._space.delayRemove(self._circle)
        GameElementBase._deletePhysic(self)
        
    def _initLibavg(self, root):
        nodeCls = self._theme.getNode(self.itemType)        
        nodeCls(parent=self._root, size=self.size)
        
        self.dragHandler = ui.DragRecognizer(self._interactionDiv,
                                             coordSysNode= self._root.getParent(),
                                             upHandler=self._addImpulseForDrag,
                                             )
        
    def _addImpulseForDrag(self, event, offset):
        if not self.alive:
            return
        managers = list(self._helpSystem.getPlayerManagersForEvent(event))
        if managers:
            self._takeOwner(managers[0]) 
        
        impuls = util.vectorLength(event.speed) * 100
        impuls = max(300, impuls)
        impuls = min(impuls, 1000)            
        direction = util.vectorNormalize(offset)
         
        self._body.apply_impulse(util.vectorMult(direction, impuls))

    @classmethod
    def getPreview(cls, theme, color=""):
        if cls.itemType is None:
            print cls
        return theme.getNode(cls.itemType.format(color))  
    
    def _takeOwner(self, other):
        if other.owner is not None:
            self._owner = other.owner      
            if __debug__:
                print "Took Owner", self, ":", self._owner 
        
    def onTouchPointCollision(self, touchPoint): 
        self._takeOwner(touchPoint)
            
    def onShieldCollision(self, shield):
        self._takeOwner(shield)
        
    def _scorePointsForRemovedCrystal(self, crystalCount):
        points = pointValues.getPointsForDestroyedStructureElements(crystalCount)
        self._scorePoints(points)
    
    def _scorePoints(self, points):
        
        if points == 0 or self.owner.score is None:
            return
        
        animTime = 1500
        maxTextSize = min((75 + points,500))
        
        scoreNode = avg.WordsNode(text=str(points),
                          fontsize=maxTextSize,
                          parent=self._root.getParent(),
                          alignment="center",
                          color=self.owner.color)
       
        angle = util.getDirOfVector(util.vectorSub(self.owner.pos, self.position,))
        scoreNode.angle =angle
   
        util.centerNodeOnPosition(scoreNode,  self.position)
   
        anim = avg.LinearAnim(scoreNode, "pos",
                              animTime,
                              scoreNode.pos, self.owner.pos,
                              False, None, lambda:scoreNode.unlink(True))
        player = self.owner
        def addPoints():
            player.score+=points
            
        textShrinkAnim = avg.LinearAnim(scoreNode, "fontsize",
                              int(animTime*0.6),
                              maxTextSize, maxTextSize*0.2,
                              False, None, addPoints )
        
        textGrowAnim = avg.LinearAnim(scoreNode, "fontsize",
                              int(animTime*0.4),
                              maxTextSize*0.1, maxTextSize,
                              False, None, textShrinkAnim.start)
        textGrowAnim.start()
        anim.start()
        

class ColoredCrystal(Item):
    
    infoKey = "color_crystal"  
    
    itemType = "{color}Crystal" 
    elementToCreate = structures.ColoredElement
    color = "{color}"
    
    def __init__(self, color, *args,**kwargs):
        self._adjustColor(color)
        self.color = color
        Item.__init__(self, *args, **kwargs)
        
    def _adjustColor(self, color):
        self.itemType = self.itemType.format(color=color)
        
    def onStructureCollision(self, structure):          
        if not self.alive:
            return
        
        element = structure.addElement(self.elementToCreate, self.color,
                     structure.toRelPos(self.position),
                     rotation=self.angle-structure.angle)  
        deletedelements = structure.removeSurplusElements(element)
        self._scorePointsForRemovedCrystal(deletedelements)
        self.delete()


class CCWRotationCrystal(ColoredCrystal):
    infokey = "rotation_ccw"
    itemType = "{color}CCWCrystal" 
    
    def onStructureCollision(self, structure):
        ColoredCrystal.onStructureCollision(self, structure)
        structure.rotationSpeed = abs(structure.rotationSpeed)
    

class CWRotationCrystal(ColoredCrystal):
    infokey = "rotation_cw"
    itemType = "{color}CWRotationCrystal" 
    
    def onStructureCollision(self, structure):
        ColoredCrystal.onStructureCollision(self, structure)
        structure.rotationSpeed = -abs(structure.rotationSpeed)
   
    
class EaterCrystal(ColoredCrystal):
    eaterThreshold = 5
    infoKey = "flying_eater"
    itemType = "{color}EaterCrystal"   
    
    def __init__(self, color, *args, **kwargs):
        ColoredCrystal.__init__(self, color, *args, **kwargs)
        self._eatCounter = 0
    
    def onCrystalCollision(self, other):
        
        if self._eatCounter < self.eaterThreshold:
            other.delete()
            self._eatCounter += 1
        else:
            self.delete()
        
        return False    
    
    
class JokerItem(Item):
    itemType = "JokerCrystal"
   
    def onStructureCollision(self, structure):
          
        element = structure.addElement(structures.JokerElement,
                     structure.toRelPos(self.position),
                     rotation=self.angle-structure.angle)
        self.delete()
        
        neighbors = structure.getGraphNeighbors(element)
        for neighbor in neighbors:
            structure.removeSurplusElements(neighbor)
        
        
class BulletCrystal(Item):
    itemType = "BulletCrystal"
    infoKey = "bullet_crystal"
    
    explosionRadius = util.CRYSTAL_RADIUS * 1.5
    
    def onCrystalCollision(self, other):
        self.delete()
        other.delete()
        return False
   
    def onStructureCollision(self, structure):
        if self.owner is None:
            self.delete()
        else:
            deletedelements = structure.removeElementsInArea(self.position, self.explosionRadius )
            self._scorePointsForRemovedCrystal(deletedelements)
            self.delete()
            
    def onCannonCollision(self, other):
        other.applyDamage(1)
        self.delete()
        return False
    
    def onBorderCollision(self, other):
        self.delete()
    
 
class ExplosionCrystal(Item):
    
    infoKey = "explosion_crystal"
    itemType = "ExplosionCrystal"
    explosionRadius = 50
    
    def onCrystalCollision(self, other):
        self.delete()
        other.delete()

    def onStructureCollision(self, structure):
        
        deletedelements = structure.removeElementsInArea(self.position, self.explosionRadius )
        self._scorePointsForRemovedCrystal(deletedelements)
        
        node = avg.CircleNode(parent = self._root.getParent(),
                              pos=self.position,
                              r=self.explosionRadius,
                              color="FF0000",
                              
                              )
        avg.fadeIn(node, 200, 1, lambda: avg.fadeOut(node, 500, node.unlink(True) ))
        self.delete()

            
class RandomizationCrystal(Item):
    
    itemType = "RandomizationCrystal"
    infoKey = "randomization_crystal"
    
    def onStructureCollision(self, structure):
        element = structure.addElement(structures.StructureElement,
                     structure.toRelPos(self.position),
                     rotation=self.angle-structure.angle)
        self.delete()
        structure.randomizeNeighbors(element)
        structure.removeElement(element)
