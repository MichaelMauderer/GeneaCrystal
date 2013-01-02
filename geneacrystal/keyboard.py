# libavg - Media Playback Engine.
# Copyright (C) 2003-2011 Ulrich von Zadow
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Current versions can be found at www.libavg.de
#
# Original author of this module: Thomas Schott <scotty at c-base dot org>
#
from libavg import *

g_player = avg.Player.get()


class Key(avg.DivNode):
    """
    This class represents a single key.
    """
    
    def __init__(self, keyDef, keyImg, onDownCallback, onUpCallback, bgImg, font = None, textColor="000000", *args, **kwargs):
        kwargs['pos'] = keyDef[1]
        kwargs['size'] = keyDef[2]
        super(Key, self).__init__(*args, **kwargs)
        self._size = super(Key, self).size

        self.__keyDef = keyDef
        self.__backImg = avg.ImageNode(href=bgImg, pos=(0, 0), size=keyDef[2], parent=self)
        self.__isCommandKey = False
        if keyImg is None:
            self.__words = avg.WordsNode(text=keyDef[0][0], parent=self, color=textColor, fontsize=keyDef[2][1] * 0.8 * 72 / 96)
            if font is not None:
                self.__words.font = font
            self.__words.pos = ((self.size.x - self.__words.getMediaSize()[0]) / 2  , (self.size.y - self.__words.getMediaSize()[1]) / 2)
        else:
            self.__isCommandKey = True
            self.__imgNode = avg.ImageNode(href=keyImg, pos=(0.2 * keyDef[2][0], 0.2 * keyDef[2][1]), size=(0.6 * keyDef[2][0], 0.6 * keyDef[2][1]) , parent=self)

        self.__keyCode = keyDef[0]
        self.__onDownCallback = onDownCallback
        self.__onUpCallback = onUpCallback

        self.__cursorID = None
        self.setEventHandler(avg.CURSORDOWN, avg.MOUSE | avg.TOUCH, self.__onDown)
        self.setEventHandler(avg.CURSORUP, avg.MOUSE | avg.TOUCH, self.__onUpOut)
        self.setEventHandler(avg.CURSOROUT, avg.MOUSE | avg.TOUCH, self.__onUpOut)

    def shift(self, value):
        if not self.__isCommandKey:
            if value:
                self.__words.text = self.__keyDef[0][1]
                self.__words.pos = ((self.size[0] - self.__words.getMediaSize()[0]) / 2  , (self.size[1] - self.__words.getMediaSize()[1]) / 2)       
            else:
                self.__words.text = self.__keyDef[0][0]
                self.__words.pos = ((self.size[0] - self.__words.getMediaSize()[0]) / 2  , (self.size[1] - self.__words.getMediaSize()[1]) / 2)           

    def __onDown(self, event):
        if self.__cursorID:
            return
        self.__pseudoDown(event)

    def __onUpOut(self, event):
        if not self.__cursorID == event.cursorid:
            return
        self.__pseudoUp(event)

    def __pseudoDown(self, event):
        self.__cursorID = event.cursorid

        if self.__onDownCallback:
            self.__onDownCallback(event, self.__keyCode)
       
    def __pseudoUp(self, event):
        self.__cursorID = None

        if self.__onUpCallback:
            self.__onUpCallback(event, self.__keyCode)
       
    def _getSize(self):
        return self._size
    
    def _setSize(self, size):
        self._size = size
        self.__backImg.size = size
        if not self.__isCommandKey:
            self.__words.fontsize=size[1]*0.8*72/96
            self.__words.pos = ((self.size[0] - self.__words.getMediaSize()[0]) / 2  , (self.size[1] - self.__words.getMediaSize()[1]) / 2)
        else:
            self.__imgNode.size=(0.6 * size[0], 0.6 * size[1])
            self.__imgNode.pos=(0.2 * size[0], 0.2 * size[1])
            
    size=property(_getSize,_setSize)


class Keyboard(avg.DivNode):
    """
    This class represents a generic keyboard.
    """

    def __init__(self, keyDefs, shiftKeyCode="SHIFT", backKeyCode="BACKSPACE", enterKeyCode="ENTER", font = None,  *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.__shiftKeyCode = shiftKeyCode
        self.__backKeyCode = backKeyCode
        self.__enterKeyCode = enterKeyCode
        self.__shiftDownCounter = 0
        self.__downKeyHandler = None
        self.__upKeyHandler = None
        self.__backHandler = None
        self.__enterHandler = None
        self._size = super(Keyboard, self).size
        self.__keys = []

        for kd in keyDefs:
            if isinstance(kd[0], tuple):
                key = Key(kd, None, self.__onCharKeyDown, self.__onCharKeyUp, kd[3], parent=self, font=font)
            else:
                key = Key(kd, kd[4], self.__onCommandKeyDown, self.__onCommandKeyUp, kd[3], parent=self, font=font)
            self.__keys.append(key)

    
    def cleanup(self):
        self.__keys = []
        

    def setKeyHandler(self, downHandler, upHandler=None, backHandler=None, enterHandler=None):
        self.__downKeyHandler = downHandler
        self.__upKeyHandler = upHandler
        self.__backHandler = backHandler
        self.__enterHandler = enterHandler

    def _getCharKeyCode(self, keyCodes):
        if self.__shiftDownCounter:
            return keyCodes[1]
        else:
            return keyCodes[0]

    def __onCharKeyDown(self, event, keyCodes):
        if self.__downKeyHandler:
            self.__downKeyHandler(self._getCharKeyCode(keyCodes))

    def __onCharKeyUp(self, event, keyCodes):
        if self.__upKeyHandler:
            self.__upKeyHandler(self._getCharKeyCode(keyCodes))

    def __onCommandKeyDown(self, event, keyCode):
        if keyCode == self.__shiftKeyCode:
            self.__shiftDownCounter += 1
            for key in self.__keys:
                key.shift(True)
                
    def __onCommandKeyUp(self, event, keyCode):
        if keyCode == self.__shiftKeyCode:
            if self.__shiftDownCounter > 0:
                self.__shiftDownCounter -= 1
            if not self.__shiftDownCounter:
                for key in self.__keys:
                    key.shift(False)
        if keyCode == self.__backKeyCode:
            if self.__backHandler:
                self.__backHandler()
        if keyCode == self.__enterKeyCode:
            if self.__enterHandler:
                self.__enterHandler()

    def __scaleKeys(self, size):
        scaleX = size[0] / self.size.x 
        scaleY = size[1] / self.size.y
        
        for key in self.__keys:
            key.pos = (key.pos.x * scaleX, key.pos.y * scaleY)
            key.size = (key.size.x * scaleX, key.size.y * scaleY)

    def _getSize(self):
        return self._size
    
    def _setSize(self, size):    
        self.__scaleKeys(size)
        self._size = size
    
    size=property(_getSize,_setSize)

    @classmethod
    def makeRowKeyDefs(cls, startPos, keySize, spacing, keyStr, shiftKeyStr, bgImg):
        keyDefs = []
        curPos = startPos
        offset = keySize[0] + spacing
        for keyCode, shiftKeyCode in zip(keyStr, shiftKeyStr):
            keyDefs.append([(keyCode, shiftKeyCode), curPos, keySize, bgImg])
            curPos = (curPos[0] + offset, curPos[1])
        return keyDefs
    
