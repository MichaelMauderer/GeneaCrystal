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
import xml.dom.minidom as dom
import os
from geneacrystal import util
from geneacrystal.helpSystem import InfoObject

class GameModes():
    ComeAndPlay = "come_n_play"
    Versus2P = "versus_2"
    Versus3P = "versus_3"
    CityDefense = "city_defense"
    
    
class Difficulties():
    Easy = "easy"
    Medium = "medium"
    Hard = "hard"
    Costum ="custom"


class ConfigReader(object):
    
    def __init__(self):
        self.config = dom.parse(os.path.join(util.XML_PATH, "genea_crystal.xml"))
        
    def refresh(self):
        self.config = dom.parse(os.path.join(util.XML_PATH, "genea_crystal.xml"))
       
    def get_items(self):
        
        items = {}
        
        for entry in self.config.childNodes:
            for node in entry.childNodes:
                if node.nodeName == "infos":
                    
                    for item in node.getElementsByTagName("item"):
                        
                        type = str(item.getAttribute("type"))
                        name = str(item.getAttribute("name"))
                        path = str(item.getAttribute("imgpath"))
                        description = str(item.getAttribute("description"))
                        
                        items[type] = InfoObject(heading=name, text=description, image=path)
        
        if __debug__:
            print "====== Item Info ======"  
            print  items
            print "====================================="
            print "\n"      
            
        return items
    
    def get_infos(self):

        
        infos = {}
        
        for entry in self.config.childNodes:
            for node in entry.childNodes:
                if node.nodeName == "infos":
                    
                    for item in node.getElementsByTagName("item"):
                        
                        type = str(item.getAttribute("type"))
                        name = str(item.getAttribute("name"))
                        path = str(item.getAttribute("imgpath"))
                        description = str(item.getAttribute("description"))
                        
                        infos[type] = InfoObject(heading=name, text=description, image=path)
                        
                    for info in node.getElementsByTagName("info"):
                        
                        type = str(item.getAttribute("type"))
                        name = str(item.getAttribute("name"))
                        description = str(item.getAttribute("description"))
                        
                        infos[type] = InfoObject(heading=name, text=description)
        
        if __debug__:
            print "============ Descriptions ==========="  
            print  infos
            print "====================================="
            print "\n"      
            
        return infos
                    
    def get_current_difficulty(self, game_mode):
        
        difficulty = "Error - Not Found"
        
        for entry in self.config.childNodes:
            for game in entry.childNodes:
                if game.nodeName == "game" and game.getAttribute("mode") == game_mode:
                    difficulty = str(game.getAttribute("difficulty"))
                    
        if __debug__:
            print "====== " + game_mode + " Difficulty ======"  
            print  difficulty
            print "====================================="
            print "\n"      
            
        return difficulty
            
    def get_game_info(self, game_mode, difficulty):
        
        settings = {}
        items = {}
        
        for entry in self.config.childNodes:
            for game in entry.childNodes:
                if game.nodeName == "game" and game.getAttribute("mode") == game_mode:
                    
                    for node in game.childNodes:
                        if node.nodeName == "difficulty" and node.getAttribute("val") == difficulty:
                            
                            for node in node.childNodes:
                
                                if node.nodeName == "setting":
                                    self.__read_setting_node(node, settings)
                                    
                                if node.nodeName == "items":
                                    self.__read_items_node(node, items)
                         
                       
    
        if __debug__:
            print "====== " + game_mode + " / " + difficulty + " - Game Info ======"  
            print "Settings: " + str(settings)
            print "Items: " + str(items)
            print "====================================="
            print "\n"
            
        return settings, items
    
    def set_setting(self, game_mode, id, new_val):
        
        for entry in self.config.childNodes:
            for game in entry.childNodes:
                if game.nodeName == "game" and game.getAttribute("mode") == game_mode:
                    
                    if id == "difficulty":
                        game.setAttribute("difficulty", new_val)
                        
                        if __debug__:
                            print "===== writing new difficulty ===="
                            print game.getAttribute("difficulty")
                            print "================================="
                            
                    
                    for node in game.childNodes:
                        if node.nodeName == "difficulty" and node.getAttribute("val") == "custom":
                            
                            for node in node.childNodes:
                
                                if node.nodeName == "setting" and node.getAttribute("id") == id:
                                
                                    node.setAttribute("val", new_val)
                                    
                                    if __debug__:
                                        print "===== writing ===="
                                        print game.getAttribute("mode")
                                        print node.getAttribute("val")
                                        print node.getAttribute("id")
                                        print "=================="
                                    
        f = open(os.path.join(util.XML_PATH, "genea_crystal.xml"), "w") 
        self.config.writexml(f, "", "", "") 
        f.close()
             
    def set_item_probability(self, game_mode, type, new_probability):
        
        for entry in self.config.childNodes:
            for game in entry.childNodes:
                if game.nodeName == "game" and game.getAttribute("mode") == game_mode:
                    
                    for node in game.childNodes:
                        if node.nodeName == "difficulty" and node.getAttribute("val") == "custom":
                            
                            for node in node.childNodes:
                
                                if node.nodeName == "items":
                                    
                                    for item in node.getElementsByTagName("item"): 
                                        
                                        if item.getAttribute("type") == type:
                                            item.setAttribute("probability", new_probability)
                                    
        f = open(os.path.join(util.XML_PATH, "genea_crystal.xml"), "w") 
        self.config.writexml(f, "", "", "") 
        f.close()
    
    def __read_setting_node(self, node, setting):
        
        type = str(node.getAttribute("id"))            
        val = node.getAttribute("val")
        
        if type=="map":
            setting[type] = str(val)
        else:
            setting[type] = eval(val)
            
    
    def __read_items_node(self, node, items):
        
        for item in node.getElementsByTagName("item"):
            type = str(item.getAttribute("type"))
            probability = item.getAttribute("probability")
    
            items[type] = eval(probability)


