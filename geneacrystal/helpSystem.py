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
from libavg import avg
from geneacrystal import themes
import logging


class InfoObject(object):
    
    def __init__(self, heading, text, image=None):
        self.text = text
        self.heading = heading
        self.image = image
        
    def getFormatDict(self):
        return {"text":self.text,
                "heading":self.heading}


class AnnotatedObject(object):
    
    infoKey = None
    
    def __init__(self, helpSystem=None):
        
        self._helpSystem = helpSystem
        if helpSystem is None:
            avg.Logger.get().trace(avg.Logger.WARNING, 
                                   "{0} has no help system".format(self))
        
    def _onInfoAction(self, event):
        if self._helpSystem is not None:
            self._helpSystem.onInfoEvent(self, event)
            
    def _setInfoHandler(self, node):
        node.setEventHandler(avg.CURSOROVER,
                             avg.TOUCH|avg.MOUSE,
                             self._onInfoAction)
        node.sensitive = True


class InfoBox(avg.DivNode):
    
    def __init__(self, theme, defaultInfo=None, *args, **kwargs):
        avg.DivNode.__init__(self, *args, **kwargs)
        
        self._theme = theme
        self._defaultInfo=defaultInfo
        self._parent = self.getParent()
        self.opacity = 1
        self.sensitive = False
        if __debug__:
            self.elementoutlinecolor = 'FFFFFF'
        self._formatText = '<span underline="single" size="larger" >{heading}</span><br/>{text}'
        theme.InfoBoxBackground(parent=self, size=self.size, opacity=0.5)
        self._text = avg.WordsNode(pos = (self.size.x/2, self.size.y/20),
                                   parent=self, text="",
                                   size=(self.size.x*0.9,self.size.y*0.9),
                                   fontsize=self.size.y/13,
                                   alignment='center',
                                   )
        
    def updateInfo(self, infoItem):
        self._text.text = self._formatText.format(**infoItem.getFormatDict()) 
    
    def hide(self):
        self.unlink(False)
        
    def show(self):
        if self.getParent() is None:
            self._parent.appendChild(self)
            if self._defaultInfo is not None:
                self.updateInfo(self._defaultInfo)
        
class HelpSystem(object):
    
    def __init__(self, elementInfos):
        self._playerInfoManagers = []
        self._infos = elementInfos
        
    @property
    def infos(self):
        return self._infos
        
    def onInfoEvent(self, source, event):
        try:
            info = self.infos[source.infoKey]
        except:
            text = "No information available for {!s}".format(source.infoKey)
            info = InfoObject(source.__class__.__name__, text, themes.DefaultTheme.NoImageAvailable)
            logging.warn(text)
        
        infoManagers = self.getPlayerManagersForEvent(event)
        
        for infoManager in infoManagers:
            infoManager.addInfo(info)
    
    def getPlayerManagersForEvent(self, event):
        return filter(lambda m: m.isActive and m.isForManager(event) ,
                      self._playerInfoManagers )
        
    def addPlayerInfoManager(self, playerInfoManager):
        self._playerInfoManagers.append(playerInfoManager)
        
        
class InfoManager(object):
    
    def __init__(self, helpSystem, theme=themes.DefaultTheme, owner=None):
        self._owner=owner
        self._helpSystem = helpSystem
        self._helpSystem.addPlayerInfoManager(self)
        self._infoBoxes=[]
        self._infoButtons = []
        self._theme = theme
        self.isActive = False
        
    @property
    def owner(self):
        return self._owner
        
    def addInfo(self, info):
        for infoBox in self._infoBoxes:
            infoBox.updateInfo(info)
        
    def getInfoBox(self, *args, **kwargs):
        box = InfoBox(self._theme, *args, **kwargs)
        self._infoBoxes.append(box)
        box.hide()
        return box
    
    def _showBoxes(self, event):
        self.isActive = True
        self.addInfo(self._helpSystem.infos["infobox"])
        for box in self._infoBoxes:
            box.show()
    
    def _hideBoxes(self, event):
        self.isActive = False
        for box in self._infoBoxes:
            box.hide()
    
    def getInfoButton(self, *args, **kwargs):
        infoButton = self._theme.InfoButton(*args, **kwargs)
        self._infoButtons.append(infoButton)
        infoButton.setEventHandler(avg.CURSORDOWN, avg.TOUCH|avg.MOUSE, self._showBoxes)
        infoButton.setEventHandler(avg.CURSORUP, avg.TOUCH|avg.MOUSE, self._hideBoxes)
        return infoButton
    
    def isForManager(self, event):
        return self._owner.isForPlayer(event)
            
