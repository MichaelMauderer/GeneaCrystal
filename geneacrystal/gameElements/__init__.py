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
from geneacrystal import themes, util, physic
import libavg as avg
import pymunk
from geneacrystal.helpSystem import AnnotatedObject
import threading


availableColors = ["Red", "Green","Blue", "Yellow", "Orange", "Pink", "Purple"]

htmlForColor  = {"Red": "FF0000",
                 "Green": "00FF00",
                 "Blue": "0000FF",
                 "Yellow": "FFFF00",
                 "Orange" : "FFA500",
                 "Pink": "FF00FF",
                 "Purple":"800080",
                 }


class GameElementBase(AnnotatedObject):
    
    def __init__(self, space, parent, position, size=None, angle=0, rotationSpeed=0,
                 rotationEnabled=False, theme=themes.DefaultTheme, owner=None, 
                 helpSystem=None):
               
        AnnotatedObject.__init__(self, helpSystem)
      
        self._size = size
        assert size is None or len(size) == 2
        self._space = space
        self._parent = parent
        self._theme = theme
        self._owner = owner
               
        self._rootParent = parent
        self._hidden = False
        self._hideLock = threading.Lock()
        self._shapes = []
        self._body = None
        self._initPhysic(position, angle)        
        assert(self._body is not None)
         
        self._root = avg.DivNode(parent=parent)
        self._root.pivot = (0,0)
        
        if self.size is not None:
            self._interactionDiv = avg.DivNode(parent=self._root)
            self._interactionDiv.pos = util.vectorMult(self.size, -0.5)
            self._interactionDiv.size = self.size
            self._setInfoHandler(self._interactionDiv)
            if __debug__:
                self._interactionDiv.elementoutlinecolor = "FFFFFF"
        else:
            avg.Logger.get().trace(avg.Logger.WARNING, 
                                   "{0} has no size".format(self))
        
        self._initLibavg(parent)
        
        self._setPosition(position)
        self.angle = angle
        
        self.alive = True
        
        self._rotationSpeed = rotationSpeed
        self._rotationEnabled = rotationEnabled
    
        if rotationEnabled:
            self._body.angular_velocity = rotationSpeed

    @property
    def interactive(self):
        return self._interactionDiv.sensitive

    @interactive.setter
    def interactive(self, value):
        self._interactionDiv.sensitive = value

    def setInteractive(self, value):
            self._interactionDiv.sensitive = value
        
    def _initPhysic(self, position, angle):
        self._body = pymunk.Body()
        self._body.position = position
        self._body.angle = angle
        
    def _initLibavg(self, root):
        pass
    
    def _setPosition(self, position):
        position = tuple(position)
        self._root.pos = self._root.getParent().getRelPos(position)
        self._body.position = position
        
    def onEvent(self, event):
        event.activate(self)
    
    @property 
    def owner(self):
        return self._owner
    
    @property
    def size(self):
        return self._size
        
    @property
    def position(self):
        return tuple(self._body.position)
    
    @property
    def angle(self):
        return self._body.angle
    
    @angle.setter
    def angle(self, angle):
        self._body.angle = angle
        self._root.angle = angle
        
    def show(self):
        self._hideLock.acquire()
        if self._hidden:
            self._rootParent.appendChild(self._root)
            self._space.add(*self._shapes)
            self._hidden =False
        self._hideLock.release()    

    def hide(self):
        self._hideLock.acquire()
        if not self._hidden and self.alive:
            self._root.unlink(False)
            self._space.remove(*self._shapes)
            self._hidden = True
        self._hideLock.release()
        
    def delete(self):
        if self.alive:
            self.alive = False
            self._deletePhysic()
            self._deleteLibavg()
            self._owner = None
            
    def _deletePhysic(self):
        if not self._body.is_static:
            self._space.delayRemove(self._body)
        if not self._hidden:
            self._space.delayRemove(*self._shapes)  
        
        if isinstance(self._body,physic.BaseBody):
            self._body.delete()  
          
        self._space = None
        self._body = None
        self._shapes = None
        
    def _deleteLibavg(self):
        self._root.unlink(True)
        self._root = None
        self._interactionDiv = None
        
    def _physicUpdate(self):
        self._setPosition(self._body.position)
        self.angle = self._body.angle
        
    def _addShape(self, shape):
        if self._space.inStep:
            self._space.delayedAdd(shape)
        else:
            self._space.add(shape)
      
        self._shapes.append(shape)
        
    def _removeShape(self, shape):
        if self._space.inStep:
            self._space.delayRemove(shape)
        else:
            self._space.remove(shape)
        
        self._shapes.remove(shape)
        
    @property
    def rotationSpeed(self):
        return self._rotationSpeed
    
    @rotationSpeed.setter
    def rotationSpeed(self, value):
        self._rotationSpeed = value
        self._body.angular_velocity = value
    
    @property    
    def rotationEnabled(self):
        return self._rotationEnabled
    
    @rotationEnabled.setter
    def rotationEnabled(self, value):
        self._rotationEnabled = value
        if value:
            self._body.angular_velocity = self._rotationSpeed
        else:
            self._body.angular_velocity = 0
            
    def toAbsPos(self, pos):
        x,y = pos
        return self._root.getAbsPos((x,y))
        
    def toRelPos(self, pos):
        x,y = pos
        return self._root.getRelPos((x,y))
    
    def changeParent(self, newParent):
        absPos = self._root.getParent().getAbsPos(self._root.pos)
        self._root.unlink(False)
        self._root.pos = newParent.getRelPos(absPos)
        newParent.appendChild(self._root)

