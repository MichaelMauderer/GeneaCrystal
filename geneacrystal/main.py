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
from libavg import AVGApp, avg
from geneacrystal.menus.mainMenu import MainMenu
import geneacrystal.util as util
from geneacrystal.gameNodes import ComeAndPlayGameNode, CityDefenderGameNode,\
    VersusModeNode
from geneacrystal import nodes, themes
from geneacrystal.util.config_reader import ConfigReader, GameModes


class Main(AVGApp):
    
    multitouch = True
    
    def __init__(self, parent):
        
        self.configReader = ConfigReader()
        self.mainMenu = MainMenu(start_cap_mode=self.startCapCallback, 
                                 start_city_defense_mode=self.startCityDefenseCallback,
                                 start_versus_2_mode=self.startVersus2Callback, 
                                 start_versus_3_mode=self.startVersus3Callback,
                                 pos=(0,0), size=(1280,800))
        parent.appendChild(self.mainMenu)
        self.rootNode = parent
        self._theme = themes.StandardTheme()
                
    def endGameAndShowMenuAgain(self, fade=True, oldNode=None):
        
        if fade:
            self.rootNode.appendChild(self.mainMenu)
            self.mainMenu.opacity = 0
            avg.LinearAnim(self.gameNode, "opacity", 2000, 1, 0, False, None, self.gameNode.delete).start()
            avg.LinearAnim(self.mainMenu, "opacity", 3000, 0, 1).start()
        else:
            self.gameNode.delete()
            self.rootNode.insertChildBefore(self.mainMenu, oldNode)
            self.mainMenu.opacity = 1
           
    def startCapCallback(self, event):
        self.mainMenu.coop_chooser.slideOutToLeft()
        self.configReader.refresh()
        currentDifculty =  self.configReader.get_current_difficulty(GameModes.ComeAndPlay)
        settings, items = self.configReader.get_game_info(GameModes.ComeAndPlay,
                                                                        currentDifculty)
        infos = self.configReader.get_infos()
        self.mainMenu.unlink(False)      
        self.gameNode = ComeAndPlayGameNode(settings, items, self.endGameAndShowMenuAgain,
                                    size=util.WINDOW_SIZE, parent = self.rootNode,
                                    infos=infos)
      
    def startCityDefenseCallback(self, event):
        self.mainMenu.coop_chooser.slideOutToLeft()
       
        self.mainMenu.unlink(False)
        self.configReader.refresh()
        currentDifculty =  self.configReader.get_current_difficulty(GameModes.CityDefense)
        settings, items = self.configReader.get_game_info(GameModes.CityDefense,
                                                          currentDifculty)
        infos = self.configReader.get_infos()
        
        self.gameNode = CityDefenderGameNode(settings, items,
                                             self.endGameAndShowMenuAgain,
                                             size=util.WINDOW_SIZE,
                                             parent = self.rootNode,
                                             infos=infos,
                                             )
       
    def startVersus2Callback(self, event):
        self.mainMenu.coop_chooser.slideOutToLeft()
        self.mainMenu.unlink(False)
        self.configReader.refresh()
        currentDifculty =  self.configReader.get_current_difficulty(GameModes.Versus2P)
      
        settings, items = self.configReader.get_game_info(GameModes.Versus2P,
                                                          currentDifculty)
        infos = self.configReader.get_infos()
        self.gameNode = VersusModeNode(2, settings, items,
                                       self.endGameAndShowMenuAgain,
                                       size=util.WINDOW_SIZE,
                                       parent = self.rootNode,
                                       infos=infos)

    def startVersus3Callback(self, event):
        self.mainMenu.coop_chooser.slideOutToLeft()
        self.mainMenu.unlink(False)
        self.configReader.refresh()
        currentDifculty =  self.configReader.get_current_difficulty(GameModes.Versus3P)
      
        settings, items = self.configReader.get_game_info(GameModes.Versus3P,
                                                         currentDifculty)
        infos = self.configReader.get_infos()
        self.gameNode = VersusModeNode(3, settings, items,
                                       self.endGameAndShowMenuAgain,
                                       size=util.WINDOW_SIZE,
                                       parent = self.rootNode,
                                       infos=infos)

    def onKeyDown(self, event):
        if event.keystring == "b":
            node = self.crystalGenerator.getNextCrystalConstructor(self)(1, self.gameNode.space, pos=(400,500), parent=self.gameNode)
            node._body.apply_impulse((0,-825))
        elif event.keystring == "x":
            node = nodes.ShieldNode(self.gameNode.space, pos1=(200,200), pos2=(600, 200), strokewidth=20, color="FF0000", parent=self.gameNode)
        elif event.keystring == "r":
            self.gameNode.toggleRotations()
            
            
if __name__ == '__main__':
    Main.start(resolution=(util.WINDOW_SIZE))
