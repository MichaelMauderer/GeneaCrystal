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
import pymunk
import logging
import libavg as avg
import weakref
from geneacrystal import util


CrystalCollisionType = 32
StructureCollisionType = 33
ShieldCollisionType = 34
BorderCollisionType = 35
TouchPointCollisionType = 36
CannonCollisionType = 37
CityCollisionType = 38
TeleportBorderCollisionType = 39

class CrystalGameSpace(pymunk.Space):
    
    def __init__(self, iterations=10, endOfGameCallback=None):
        pymunk.Space.__init__(self, iterations=iterations)
        self.add_collision_handler(CrystalCollisionType,StructureCollisionType,post_solve=self.structureCollision)
        self.add_collision_handler(StructureCollisionType, BorderCollisionType,begin=self.finalCollision)
        self.add_collision_handler(CrystalCollisionType, BorderCollisionType,begin=self.crystalBorderCollision)
        self.add_collision_handler(CannonCollisionType, CrystalCollisionType, begin=self.crystalCannonCollision)
        self.add_collision_handler(TouchPointCollisionType, CrystalCollisionType, begin=self.touchpointCollision)
        self.add_collision_handler(StructureCollisionType, CannonCollisionType, begin=self.cannonStructureCollision)
        self.add_collision_handler(StructureCollisionType, CityCollisionType, begin=self.finalCollision)
        self.add_collision_handler(CrystalCollisionType, CrystalCollisionType, begin=self.crystalCollision)
        self.add_collision_handler(ShieldCollisionType, CrystalCollisionType, begin=self.shieldCollision)
        self.add_collision_handler(TeleportBorderCollisionType, CrystalCollisionType, begin=self.crystalTeleportBorderCollision)
       
        self.add_collision_handler(StructureCollisionType, StructureCollisionType, begin=lambda s,a :False)
        self.add_collision_handler(TouchPointCollisionType, StructureCollisionType, begin = lambda s,a:  False)
       
        self.endOfGameCallback=endOfGameCallback
        self.inStep = False
        
    def crystalTeleportBorderCollision(self, space, arbiter):
        borderShape, crystalShape = self.getShapesByType(arbiter.shapes,
                                                         TeleportBorderCollisionType,
                                                         CrystalCollisionType) 
        crystalShape.body.onTeleportBorderCollision(None)         
        return False
    
    def crystalBorderCollision(self, space, arbiter):
        borderShape, crystalShape = self.getShapesByType(arbiter.shapes,
                                                         BorderCollisionType,
                                                         CrystalCollisionType) 
           
        crystalShape.body.onBorderCollision(None)          
        return True
        
    def touchpointCollision(self, space, arbiter):
        touchBody, crystalBody = self.getShapeBodiesByType(arbiter.shapes,
                                                         TouchPointCollisionType,
                                                         CrystalCollisionType) 
        crystalBody.onTouchPointCollision(touchBody)           
        return True

    def shieldCollision(self, space, arbiter):
        shieldBody, crystalBody = self.getShapeBodiesByType(arbiter.shapes,
                                                         ShieldCollisionType,
                                                         CrystalCollisionType) 
        crystalBody.onShieldCollision(shieldBody)           
        return True
    
    def cityCollision(self, space, arbiter):
        assert(len(arbiter.shapes) == 2) 
        assert(len(arbiter.contacts) == 1)
        
        cityShape, crystalShape = self.getShapesByType(arbiter.shapes,
                                                         CityCollisionType,
                                                         CrystalCollisionType)
        
        cityShape.body.onCrystalCollision(crystalShape.body, cityShape)
        return crystalShape.body.onCityCollision(cityShape.body)
    
    def crystalCollision(self, space, arbiter):
        assert(len(arbiter.shapes) == 2) 
        assert(len(arbiter.contacts) == 1)
        return bool(arbiter.shapes[0].body.onCrystalCollision(arbiter.shapes[1].body) and 
                arbiter.shapes[1].body.onCrystalCollision(arbiter.shapes[0].body))
        
    def finalCollision(self, space, arbiter):
        
        for shape in arbiter.shapes:
            if shape.collision_type == StructureCollisionType:
                shape.body.onWallCollision(None)
        else:
            logging.warn("Bad End of Game Collision")
      
        if __debug__:
            print "---Game Over---"
        return False
   
    def cannonStructureCollision(self,space,arbiter):
        assert(len(arbiter.shapes) == 2) 
        assert(len(arbiter.contacts) == 1)
        
        structureBody, cannonBody = self.getShapeBodiesByType(arbiter.shapes,
                                                            StructureCollisionType,
                                                            CannonCollisionType)
        cannonBody.onStructureCollision(structureBody)
        structureBody.onWallCollision(cannonBody)
        
        return False
        
    def crystalCannonCollision(self, space, arbiter):
        assert(len(arbiter.shapes) == 2) 
        assert(len(arbiter.contacts) == 1)
        
        crystalBody, cannonBody = self.getShapeBodiesByType(arbiter.shapes,
                                                            CrystalCollisionType,
                                                            CannonCollisionType)
            
        contact = arbiter.contacts[0]
        
        dX = crystalBody.position[0]- cannonBody.position[0]
        dY = crystalBody.position[1]- cannonBody.position[1]
        
        crystalBody.onCannonCollision(cannonBody)
        return cannonBody.onCrystalCollision(crystalBody, abs(dX),abs(dY))
        
    def getShapeBodiesByType(self, shapes, typeA, typeB): 
        shapeA, shapeB = self.getShapesByType(shapes, typeA, typeB) 
        return shapeA.body, shapeB.body
    
    def getShapesByType(self, shapes, typeA, typeB):
        shapeA, shapeB = shapes 
        if shapeA.collision_type == typeA:
            assert(shapeB.collision_type == typeB)
            return shapeA, shapeB      
        else:
            assert(shapeA.collision_type == typeB)
            return shapeB, shapeA
                
    def structureCollision(self, space, arbiter):
        assert(len(arbiter.shapes) == 2) 
        assert(len(arbiter.contacts) == 1)
         
        incommingShape, structureShape = self.getShapesByType(arbiter.shapes,
                                                         CrystalCollisionType,
                                                         StructureCollisionType)
        
        incomming, structure = incommingShape.body, structureShape.body
        
        offset = util.vectorGetDirWithLength(structure.position,
                                             incomming.position,
                                             arbiter.contacts[0].distance)
        incomming.position = util.vectorAdd(incomming.position, offset)
        incomming.update()
        
        structure.onCrystalCollision(incomming, structureShape)    
        incomming.onStructureCollision(structure)     
        
        return False
    
    def step(self, dt):
        self.inStep =True
        pymunk.Space.step(self, dt)
        self.inStep = False
        for body in self.bodies:
            if isinstance(body, BaseBody): 
                body.update()
        
    def delayRemoveComplete(self, body):
        self.add_post_step_callback(self.remove, body)
        self.add_post_step_callback(self.remove, body.node.shape)
        self.add_post_step_callback(lambda x : x.unlink(True), body.node)
    
    def delayRemove(self, *objs):
        for obj in objs: 
            if obj in self._post_step_callbacks:
                del self._post_step_callbacks[obj]
                return
            
            self.add_post_step_callback(self.remove, obj)
        
    def delayedAdd(self, *objs):
        for obj in  objs:
            self.add_post_step_callback(self.add, obj)
    
    def getConstraintsForBody(self, body):
        result = filter(body.isConstraint, self.constraints )
        return result
    
    def delete(self):
        for shape in self.shapes:
            if isinstance(shape.body, BaseBody):
                shape.body.delete()
        self.step(0.1)

    
class DebugCrystalGameSpace(CrystalGameSpace):
    def __init__(self, iterations=10):
        CrystalGameSpace.__init__(self, iterations=iterations)
        self.debugNodes = weakref.WeakKeyDictionary()
        self.debugRoot =  avg.Player.get().getRootNode()
    
    def add(self, *objs):
        CrystalGameSpace.add(self, *objs)
        for obj in objs:
            if isinstance(obj, pymunk.Body):    
                node = avg.CircleNode(pos=tuple(obj.position),  r=5, parent=self.debugRoot)
                node.fillcolor = "FF0000"
            
            elif isinstance(obj, pymunk.Segment):
                node = avg.LineNode(parent=self.debugRoot)
                node.pos1 = tuple(obj._body.local_to_world(obj.a))
                node.pos2 = tuple(obj._body.local_to_world(obj.a))
                node.strokewidth = obj.radius *2
                node.fillcolor = "00FFFF"
            
            elif isinstance(obj, pymunk.Circle):
                node = avg.CircleNode(pos=tuple(obj._body.local_to_world(obj.offset)),  r=obj.radius, parent=self.debugRoot)
                node.fillcolor = "FFFFFF"
            elif isinstance(obj, pymunk.Poly):
                node = avg.PolygonNode(parent=self.debugRoot, pos=[(p[0],p[1]) for p in obj.get_points()])
                node.fillcolor = "FFFF00"
                
            else:
                continue
                self.debugNodes[obj] = avg.CircleNode(pos=tuple(obj.position),  r=5, parent=self.debugRoot)            
            node.opacity = 0.5
            node.fillopacity = 0.5
            node.sensitive=False
            self.debugNodes[obj] = node
            
    def remove(self, *objs):
        CrystalGameSpace.remove(self, *objs)
        for obj in objs:
            if obj in self.debugNodes:
                self.debugNodes[obj].unlink(True)
                del self.debugNodes[obj]
        
    def step(self, dt):
        CrystalGameSpace.step(self, dt)
        assert(len(self.debugNodes) < self.shapes + self.bodies)
        for item, node in self.debugNodes.items():
            assert(item in self.shapes or item in self.bodies)
            
        for body in self.bodies:
            node = self.debugNodes[body]
            node.pos = tuple(body.position)
        for shape in self.shapes:
            try:
                node = self.debugNodes[shape]
                if isinstance(shape, pymunk.Segment):
                    node.pos1 =tuple(shape._body.local_to_world(shape.a))
                    node.pos2 = tuple(shape._body.local_to_world(shape.b))
                else:
                    node.pos = tuple(shape._body.local_to_world(shape.offset))
            except:
                pass
                
    def delete(self):
        CrystalGameSpace.delete(self)
        for node in self.debugNodes.values():
            node.unlink(True)
        
        
class BaseBody(pymunk.Body):
    
    def __init__(self,gameElement, mass, moment):
        pymunk.Body.__init__(self, mass, moment)
        self._gameElement = gameElement       

        self._makeCollisionHandler("onWallCollision")
        self._makeCollisionHandler("onCrystalCollision")
        self._makeCollisionHandler("onCityCollision")
        self._makeCollisionHandler("onTouchPointCollision")
        self._makeCollisionHandler("onShieldCollision")
        self._makeCollisionHandler("onCannonCollision")
        self._makeCollisionHandler("onBorderCollision")
        
    @property
    def gameElement(self):
        return self._gameElement
    
    def update(self):
        try:
            self._gameElement._physicUpdate()
        except AttributeError:
            pass
        
    def _makeCollisionHandler(self, name):
        if hasattr(self, name):
            return
        
        def handler(otherBody, *args, **kwargs):
            if not hasattr(self._gameElement, name):
                return True
            
            fun = getattr(self._gameElement, name)
            
            if otherBody is not None:
                return fun(otherBody._gameElement, *args, **kwargs)
            else:
                return fun(None, *args, **kwargs)
                
        setattr(self, name, handler)    
        
    def onTeleportBorderCollision(self, other):
        
        bodyX, bodyY = self.position
        
        if bodyX <= util.CRYSTAL_SIZE:
            self.position = util.WINDOW_SIZE[0] + util.CRYSTAL_SIZE, bodyY
            
        elif bodyX >= util.WINDOW_SIZE[0]- util.CRYSTAL_SIZE:
            self.position = -util.CRYSTAL_SIZE, bodyY
           
    def onStructureCollision(self, other):
        
        bodyX, bodyY = self.position
        
        if bodyX <= 0 or bodyX >= util.WINDOW_SIZE[0]:
            self._gameElement.delete()
            return False
        
        if hasattr(self._gameElement, "onStructureCollision"):
            return self._gameElement.onStructureCollision(other._gameElement)
        
    def delete(self):
        if self._gameElement is not None and self._gameElement.alive:
            self._gameElement.delete()
        self._gameElement = None
        
        
class TouchPointBody(BaseBody):
    
    def __init__(self, node):
        inertia = pymunk.moment_for_circle(pymunk.inf, 0, node.r, (0,0))
        BaseBody.__init__(self, node, pymunk.inf, inertia)
        self.node = node
        
    def addShape(self, shape):
        shape._body = self
        shape.group = id(self)
        
    def delete(self):
        pass
        
        
class ShieldBody(BaseBody):
    
    def __init__(self, node, mass=100):
        a = (0,0)
        b = util.transformVector((node.pos2.x - node.pos1.x,node.pos2.y - node.pos1.y))
        inertia = pymunk.moment_for_segment(mass, a,b)
        BaseBody.__init__(self, node, mass, inertia)
        
        self.shape = pymunk.Segment(self, a, b, node.strokewidth)
        self.shape.elasticity=1
        self.shape.friction = 0
        self.shape.collision_type = ShieldCollisionType
        

class RectBody(pymunk.Body):
    
    def __init__(self, space, pos, size):
        self.points = []
        self.points.append(tuple(pos))
        self.points.append((pos[0], pos[1] + size[1]))
        self.points.append((pos[0]+ size[0], pos[1]+size[1]))
        self.points.append((pos[0]+ size[0], pos[1]))
        inertia = pymunk.moment_for_box(1, size[0], size[1])
        pymunk.Body.__init__(self, 1, inertia)
        self.shape = pymunk.Poly(self, self.points, util.vectorMult(size, -0.5))
        space.add(self, self.shape)
