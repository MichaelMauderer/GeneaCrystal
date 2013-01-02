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
import libavg as avg
import pymunk
from geneacrystal import util, physic
from geneacrystal.alphaKeyboard import AlphaKeyboard
from geneacrystal.highscore import Highscore


class ItemImageNode(avg.DivNode):
        
    def __init__(self, href, size, *args, **kwargs):
        avg.DivNode.__init__(self, *args, **kwargs)
        self.pivot = 0, 0
        self.opacity = 1
        self.sensitive = False
        imageNode = avg.ImageNode(parent=self,
                                  opacity=1,
                                  href=href,
                                  size=size,
                                  )
        imageNode.pos = util.vectorMult(size, -0.5)
        self.image = imageNode
        if __debug__:
            self.elementoutlinecolor = "FFFFFF"
        
    @property
    def size(self):
        return self.image.size
    
    @size.setter
    def size(self, value):
        self.image.size = value
        util.centerNodeOnPosition(self.image, (0,0))
        
    def setEffect(self, node):
        self.image.setEffect(node)
        
    def setEventHandler(self, *args, **kwargs):
        return self.image.setEventHandler(*args, **kwargs)
        

class TouchPointNode(avg.CircleNode):
    
    def delete(self):
        self.unlink(True)
        
    def __init__(self, space, theme=None, owner=None, *args, **kwargs):
        avg.CircleNode.__init__(self, *args, **kwargs)
        
        if theme is None:
            from geneacrystal import themes
            self._theme = themes.DefaultTheme
            
        self.owner = owner
        self._body = physic.TouchPointBody(self)
        self._body.position = tuple(self.pos)
        self.filltexhref = self._theme.getStaticImage("TouchPointNode")
        #self.fillcolor = "00FF00"
        self.strokewidth = 0
        self.shape = pymunk.Circle(self._body, self.r, (0, 0))
        self.shape.elasticity = 1
        self.shape.collision_type = physic.TouchPointCollisionType
        space.add(self._body, self.shape)
        
        if __debug__:
            print "Created ", self
        
    def __str__(self, *args, **kwargs):
        formatString = "TouchPointNode(pos={tp.pos}, owner={tp.owner})"
        return formatString.format(tp=self)
        
         
class ShieldNode(avg.LineNode):
    
    def __init__(self, space, owner=None, *args, **kwargs):
        avg.LineNode.__init__(self, *args, **kwargs)
        self._body = physic.ShieldBody(self)
        self.owner = owner
        self._body.position = tuple(self.pos1)
        from geneacrystal import themes
        self.texhref = themes.DefaultTheme.getStaticImage("Wall")
        self.fillopacity = 0
        self.opacity = 1
        space.add(self._body, self._body.shape)
        self._body.sleep()
        
    def update(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2
        self._body.position = tuple(self.pos1)
        self._body.shape.b = util.transformVector((pos2.x - pos1.x, pos2.y - pos1.y))
        
    def delete(self):
        pass
    

class HighscoreEntryNode(avg.DivNode):
 
    def __init__(self, mode, score, allScores, callback=None, theme=None, *args, **kwargs):
        avg.DivNode.__init__(self, *args, **kwargs)
        
        if theme is None:
            from geneacrystal import themes
            theme = themes.DefaultTheme
        
        bgPath = theme.getStaticImage("keySymbol")
        backPath = theme.getStaticImage("backspaceSymbol")
        enterPath = theme.getStaticImage("enterSymbol")
        shiftPath = theme.getStaticImage("shiftSymbol")
        emptyPath = theme.getStaticImage("spaceSymbol")
        
        highscore = Highscore(mode)
        
        myScores = []
        myScores.extend(allScores)        
        myScores.extend(highscore.scores)
        myScores.sort(reverse=True, key=lambda val: int(val))
        
        if len(myScores) < util.MAX_HIGHSCORE_LENGTH or score > int(myScores[9]) or score == int(myScores[9]) and not score in highscore.scores:
            
            self.__value = ""
    
            def onKeyDown(keyCode):
                if len(self.__value) < 20:
                    self.__value += keyCode
                    self.__edit.text += keyCode
    
            def onBack():
                self.__value = self.__value[0:-1]
                self.__edit.text = self.__value
               
            def onEnter():
                if not self.__value == "":
                    highscore.addEntry(self.__value, score)
                    if callback is not None:
                        callback(self.__value)
                
                self._keyboard.cleanup()
                self._keyboard.unlink(True)
                self._keyboard = None
                self.__edit.unlink(True)
                self.__edit = None
                self.unlink(True)
                
            self.__edit = avg.WordsNode(size=(self.size.x, self.size.y // 8),
                                        parent=self, fontsize=self.size.y // 8,
                                        alignment="center")
            self.__edit.pos = (self.size.x // 2, 0)
            self._keyboard = AlphaKeyboard(bgPath, backPath, enterPath, shiftPath,
                                           emptyPath , onKeyDown=onKeyDown,
                                           onBack=onBack, onEnter=onEnter,
                                           size=(self.size.x, self.size.y // 10 * 8),
                                           pos=(0, self.size.y // 5),
                                           parent=self) 
        
        else:
            if callback is not None:
                callback("")
            self.unlink(True)
          
            
class ItemImageLayeredNode(avg.DivNode):
    
    def __init__(self, layers,size, *args, **kwargs):
        avg.DivNode.__init__(self, *args, **kwargs)
        self.pivot = 0, 0
        self.opacity = 1
        self.sensitive = False
        childPos = util.vectorMult(size, -0.5) 
        self._layer = []
        self._topImage = None        
        for image in layers:
            node = avg.ImageNode(parent=self,
                          opacity=1,
                          href=image,
                          size=size,
                          pos=childPos,
                          sensitive=False
                          )
            self._layer.append(node)
            node.sensitive=True
        self._topImage = self._layer[-1]
        
    def removeLayer(self, index):
        node = self._layer[index]
        node.unlink(True)
        self._layer.remove(node)
        if node == self._topImage:
            self._topImage = self._layer[-1]
        
    @property
    def size(self):
        return self._layer[0].size
    
    def setEventHandler(self, *args, **kwargs):
        return self._topImage.setEventHandler(*args, **kwargs)
    
    def setEffect(self, *args, **kwargs):
        for node in self._layer:
            node.setEffect(*args, **kwargs)
            

class OverlayNode(avg.DivNode):
       
    def __init__(self, theme=None, *args, **kwargs):
        if theme is None:
            from geneacrystal import themes
            theme = themes.StandardTheme()
        super(OverlayNode, self).__init__(*args, **kwargs)
        self._background=theme.getNode("ExitButton")(size=self.size, parent=self, opacity=1);
    
        
class StaticOverlayNode(OverlayNode):
    
    def __init__(self, finishCB, *args, **kwargs):
        super(StaticOverlayNode, self).__init__(*args, **kwargs)
        self.__anim = None
        self.__initalRadius=self._background.size.x*0.08
        self.__circle = avg.CircleNode(pos=(self._background.size.x//2, self._background.size.y//2), r=self.__initalRadius, fillcolor="000000", fillopacity=1.0, parent=self)
        self.__finishCB = finishCB
        
        self.setEventHandler(avg.CURSORDOWN,avg.TOUCH | avg.MOUSE, lambda x: self.__start())
        self.setEventHandler(avg.CURSOROUT,avg.TOUCH | avg.MOUSE, lambda x: self.__abort())
        self.setEventHandler(avg.CURSORUP,avg.TOUCH | avg.MOUSE, lambda x: self.__abort())
        
    def __start(self):
        self.__circle.sensitive=False
        self.__aborted = True
        if self.__anim is not None:
            self.__anim.abort()
        self.__anim = avg.LinearAnim(self.__circle,"r", 2000, self.__circle.r, self._background.size.y//2,  False, None, self.__finish)
        self.__aborted = False
        self.__anim.start()
        
    def __abort(self):
        if self.__anim is not None:
            self.__aborted = True
            self.__anim.abort()
            self.__anim = None
            self.__circle.r = self.__initalRadius
            self.__circle.sensitive=True

    def __finish(self):
        if not self.__aborted:
            self.__anim = None
            self.__finishCB()
            self.__circle.r =  self.__initalRadius
            self.__circle.sensitive=True

        
