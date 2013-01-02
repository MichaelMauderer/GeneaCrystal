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
from libavg import avg, ui
import os
from geneacrystal import util, themes
from geneacrystal.menus.button import MenuButton
from geneacrystal.highscore import Highscore
from geneacrystal.util.config_reader import ConfigReader
from geneacrystal.menus.helpFile import Help


class Box(avg.DivNode):
    
    def __init__(self, mainMenu, theme=themes.StandardTheme(), **kwargs):
        avg.DivNode.__init__(self, **kwargs)
        self.mainMenu = mainMenu 
        self._theme=theme

        avg.ImageNode(
                      href=os.path.join(util.IMAGE_PATH , "menu/chooser/chooser.png"),
                      size=self.size,
                      parent=self
                      )    

          
        
        cancel_size = (self.size[0] * 0.1, self.size[0] * 0.1)
        self._cancel_button = MenuButton(
                                   upImg="ChooserCancelUp",
                                   downImg="ChooserCancelDown",
                                   pos=(self.size[0] - cancel_size[0] / 2, self.size[1] - cancel_size[1] / 2),
                                   size=cancel_size,
                                   clickHandler=lambda event: self.slideOutToLeft(),
                                   )
    
    def slideInFromLeft(self):
        
        slideIn = avg.EaseInOutAnim(self, "x", 700, -self.size[0], util.WINDOW_SIZE[0] / 2 - self.size[0] / 2,
                                    0, 200, False, lambda:self._setActive(True), None)
        slideIn.start()
    
    
    def slideInFromRight(self):
        
        slideIn = avg.EaseInOutAnim(self, "x", 700, util.WINDOW_SIZE[0], util.WINDOW_SIZE[0] / 2 - self.size[0] / 2,
                                    0, 200, False, lambda:self._setActive(True), None)
        slideIn.start()
    
    def slideOutToRight(self):
        
        slideOut = avg.EaseInOutAnim(self, "x", 700, self.pos[0], util.WINDOW_SIZE[0],
                                     200, 0, False, None, lambda:self._setActive(False))
        slideOut.start()
    
    def slideOutToLeft(self):
        
        slideOut = avg.EaseInOutAnim(self, "x", 700, self.pos[0], -self.size[0],
                                     200, 0, False, None, lambda:self._setActive(False))
        slideOut.start() 
        
    def _setActive(self, b):
        self.active = b
        

class ChooserBox(Box):
    
    def __init__(self, mainMenu, game_mode_left="", game_mode_right="", **kwargs): 
        
        Box.__init__(self, mainMenu, **kwargs)        

        
        choose_size = (self.size[0] * 0.6, self.size[1] * 0.15)
        choose_x = self.size[0] / 2 - choose_size[0] / 2        
        avg.ImageNode(
                      href=os.path.join(util.IMAGE_PATH, "menu/chooser/choose.png"),
                      size=choose_size,
                      pos=(choose_x, 0),
                      parent=self
                      )
        
        div_left = avg.DivNode(
                                pos=(0, 0),
                                size=(self.size[0] / 2, self.size[1]),
                                parent=self
                                )
        
        screenshot_img_left = "ChooserScreenshot_" + game_mode_left
        screenshot_left = MenuButton(
                                     upImg=screenshot_img_left,
                                     downImg=screenshot_img_left,
                                     size=(div_left.size[0] * 0.8, div_left.size[1] * 0.4),
                                     pos=(div_left.size[0] / 2, div_left.size[1] * 0.4),
                                     clickHandler=mainMenu.start_game_mode(game_mode_left),
                                     parent=div_left
                                     )
        
        info_left = MenuButton(
                               upImg="ChooserInfo",
                               downImg="ChooserInfo",
                               size=(div_left.size[0] * 0.5, div_left.size[1] * 0.1),
                               pos=(div_left.size[0] / 2, div_left.size[1] * 0.7),
                               clickHandler=lambda event: self.createSubBox("info", game_mode_left),
                               parent=div_left
                               )
        
        settings_left = MenuButton(
                                   upImg="ChooserSettings",
                                   downImg="ChooserSettings",
                                   size=(div_left.size[0] * 0.5, div_left.size[1] * 0.1),
                                   pos=(div_left.size[0] / 2, div_left.size[1] * 0.85),
                                   clickHandler=lambda event: self.createSubBox("settings", game_mode_left),
                                   parent=div_left
                                   )
        
        div_right = avg.DivNode(
                                pos=(self.size[0] / 2, 0),
                                size=(self.size[0] / 2, self.size[1]),
                                parent=self,
                                )

        
        screenshot_img_right = "ChooserScreenshot_" + game_mode_right
        screenshot_right = MenuButton(
                                      upImg=screenshot_img_right,
                                      downImg=screenshot_img_right,
                                      size=(div_right.size[0] * 0.8, div_right.size[1] * 0.4),
                                      pos=(div_right.size[0] / 2, div_right.size[1] * 0.4),
                                      clickHandler=mainMenu.start_game_mode(game_mode_right),
                                      parent=div_right
                                      )
        
        info_right = MenuButton(
                                upImg="ChooserInfo",
                                downImg="ChooserInfo",
                                size=(div_right.size[0] * 0.5, div_right.size[1] * 0.1),
                                pos=(div_right.size[0] / 2, div_right.size[1] * 0.7),
                                clickHandler=lambda event: self.createSubBox("info", game_mode_right),
                                parent=div_right
                                )
        
        settings_right = MenuButton(
                                    upImg="ChooserSettings",
                                    downImg="ChooserSettings",
                                    size=(div_right.size[0] * 0.5, div_right.size[1] * 0.1),
                                    pos=(div_right.size[0] / 2, div_right.size[1] * 0.85),
                                    clickHandler=lambda event: self.createSubBox("settings", game_mode_right),
                                    parent=div_right,
                                    )

        self.appendChild(self._cancel_button)       
        self.active = False
    
        
    def createSubBox(self, typ, game_mode):
        
        box_size = (util.WINDOW_SIZE[0]*0.7, util.WINDOW_SIZE[1]*0.7)
        box_pos_x = (util.WINDOW_SIZE[0]/2-box_size[0]/2)
        box_pos_y = (util.WINDOW_SIZE[1]/2-box_size[1]/2)
        
        if typ=="settings":
        
            self.subbox = SettingsBox(
                                         pos=(box_pos_x,box_pos_y),
                                         size=box_size,
                                         chooser=self, 
                                         game_mode=game_mode, 
                                         parent=self.mainMenu
                                         )
            
        elif typ=="info":
            
            self.subbox = InfoBox(
                                 pos=(box_pos_x,box_pos_y),
                                 size=box_size,
                                 chooser=self, 
                                 game_mode=game_mode, 
                                 parent=self.mainMenu
                                 )
             
        self.slideOutToRight()
        
        slideIn = avg.EaseInOutAnim(self.subbox, "x", 700, -self.size[0], util.WINDOW_SIZE[0]/2-self.size[0]/2, 0, 200)
        slideIn.start()
        

class SubBox(avg.DivNode):
    
    def __init__(self, chooser, game_mode, theme=themes.StandardTheme(), **kwargs): 
        
        self.chooser = chooser
        self.game_mode = game_mode
        self.theme = theme
        
        avg.DivNode.__init__(self, **kwargs)
        
        avg.ImageNode(
                      href=os.path.join(util.IMAGE_PATH , "menu/chooser/chooser.png"),
                      size=self.size,
                      parent=self
                      )
        
        descr_size = (self.size[0]*0.8, self.size[1]*0.9)
        descr_pos_x = self.size[0]/2 - descr_size[0]/2    
        descr_pos_y = self.size[1]/2 - descr_size[1]/2
        self.descr_div = avg.DivNode(
                                     pos=(descr_pos_x,descr_pos_y),
                                     size=descr_size,
                                     parent=self
                                     )
        
        button_size = (self.size[0]*0.1,self.size[0]*0.1)
        
        cancel_button = MenuButton(
                                   upImg="ChooserCancelUp",
                                   downImg="ChooserCancelDown", 
                                   pos=(self.size[0]-button_size[0]/2,self.size[1]-button_size[1]/2),
                                   size=button_size, 
                                   clickHandler=lambda event: self.remove(),
                                   parent=self
                                   )
        
    def remove(self):
        self.chooser.slideInFromRight()
        slideOut = avg.EaseInOutAnim(self, "x", 700, self.pos[0], -self.size[0]*1.1,
                                     200, 0, False, None, lambda:self.unlink())
        slideOut.start()
        
        
class InfoBox(SubBox):

    def __init__(self, **kwargs):
        SubBox.__init__(self, **kwargs)
        
        mode = self.game_mode
        if mode == "versus_2" or mode == "versus_3":
            mode = "versus"
        
        self.pages = Help(mode).pages
        self.curr_page = 0
        
        div_left = avg.DivNode(
                               pos=(0,0),
                               size=(self.descr_div.size[0]/2,self.descr_div.size[1]),
                               parent=self.descr_div
                               )
        
        div_right = avg.DivNode(
                                pos=(self.descr_div.size[0]/2,0),
                                size=(self.descr_div.size[0]/2,self.descr_div.size[1]),
                                parent=self.descr_div
                               )
        
        heading_size = (div_left.size[0]*0.7, div_left.size[1]*0.1)
        
        self.heading_left_div = avg.DivNode(
                                        pos=(div_left.size[0]/2-heading_size[0]/2,0),
                                        size=heading_size,
                                        parent=div_left,
                                        )
        self.heading_left = avg.WordsNode(text="", font="Arial",  parent=self.heading_left_div, pos=(self.heading_left_div.size[0]/2,0), alignment="center", color="FF9600", fontsize=30)
        
        self.heading_right_div = avg.DivNode(
                                         pos=(div_right.size[0]/2-heading_size[0]/2,0),
                                         size=heading_size,
                                         parent=div_right,
                                         )
        self.heading_right = avg.WordsNode(text="", font="Arial",  parent=self.heading_right_div, pos=(self.heading_right_div.size[0]/2,0), alignment="center", color="FF9600", fontsize=30)
        
        picture_size = (div_left.size[0]*0.9, div_left.size[1]*0.4)
        
        self.picture_left = avg.ImageNode(
                                          href="",
                                          pos=(div_left.size[0]/2-picture_size[0]/2, div_left.size[1]*0.1),
                                          size=picture_size,
                                          parent=div_left
                                          )
        
        self.picture_right = avg.ImageNode(
                                           href="",
                                           pos=(div_right.size[0]/2-picture_size[0]/2, div_right.size[1]*0.1),
                                           size=picture_size,
                                           parent=div_right
                                           )
        
        text_size = (div_left.size[0]*0.9, div_left.size[1]*0.4)
        
        self.text_left_div = avg.DivNode(
                                     pos=(div_left.size[0]/2-text_size[0]/2, div_left.size[1]*0.55),
                                     size=text_size,
                                     parent=div_left
                                     )
        self.text_left = avg.WordsNode(text="", font="Arial", parent=self.text_left_div, width=self.text_left_div.size[0], fontsize=18, color="FF9600", justify=True)
        
        self.text_right_div = avg.DivNode(
                                      pos=(div_right.size[0]/2-text_size[0]/2, div_right.size[1]*0.55),
                                      size=text_size,
                                      parent=div_right
                                     )
        self.text_right = avg.WordsNode(text="", font="Arial", parent=self.text_right_div, width=self.text_right_div.size[0], fontsize=18, color="FF9600", justify=True)
        
        
        
        button_size = (self.descr_div.size[0]*0.1, self.descr_div.size[1]*0.15)
        
        next = MenuButton(
                          upImg="GreaterUp",
                          downImg="GreaterDown", 
                          pos=(self.descr_div.size[0]/2+button_size[0]/2,self.descr_div.size[1]-button_size[1]*0.3),
                          size=button_size,
                          clickHandler=lambda event: self.nextPage(),
                          parent=self.descr_div
                          )
        
        prev = MenuButton(
                          upImg="LessUp",
                          downImg="LessDown", 
                          pos=(self.descr_div.size[0]/2-button_size[0]/2,self.descr_div.size[1]-button_size[1]*0.3),
                          size=button_size,
                          clickHandler=lambda event: self.prevPage(),
                          parent=self.descr_div
                          )
        
        self.nextPage()
        
    def nextPage(self):
        
        left = self.pages[self.curr_page]
        right = self.pages[self.curr_page + 1]
        self.curr_page = (self.curr_page + 2) % len(self.pages)
        
        self.heading_left.text = left.heading
        self.heading_right.text = right.heading
        
        self.picture_left.href = self.theme.getStaticImage(left.picture)
        self.picture_right.href = self.theme.getStaticImage(right.picture)

        self.text_left.text = left.text
        self.text_right.text = right.text
        
        
    def prevPage(self):
        
        left = self.pages[self.curr_page]
        right = self.pages[self.curr_page + 1]
        self.curr_page = (self.curr_page - 2) % len(self.pages)
        
        self.heading_left.text = left.heading
        self.heading_right.text = right.heading
        
        self.picture_left.href = self.theme.getStaticImage(left.picture)
        self.picture_right.href = self.theme.getStaticImage(right.picture)
        
        self.text_left.text = left.text
        self.text_right.text = right.text
        
  
        
class SettingsBox(SubBox):
    
    def __init__(self, **kwargs):
        
        SubBox.__init__(self, **kwargs)

        self.config = ConfigReader()
        
        self.slots = []
        self.itemButton = None
        
        game_mode_size = (self.descr_div.size[0]*0.5,self.descr_div.size[1]*0.15)
        self.game_mode_img = avg.ImageNode(href=self.theme.getStaticImage(self.game_mode), 
                                       size=game_mode_size,
                                       pos=(self.descr_div.size[0]/2-game_mode_size[0]/2,-self.descr_div.size[0]*0.01),
                                       parent=self.descr_div
                                       )
        
        self._appendSlot(pos=0, image="difficulty", startVal=0, endVal=3, difficulty=True, append=False)
        
        if self.game_mode == "come_n_play":
            self._appendSlot(pos=1, image="rotation_speed")
            self._appendSlot(pos=2, image="growing_speed")
            self._appendSlot(pos=3, image="crystals", startVal=4, endVal=8)
            self._appendItemButton()
        
        elif self.game_mode == "city_defense":
            self._appendSlot(pos=1, image="rotation_speed")
            self._appendSlot(pos=2, image="growing_speed")
            self._appendSlot(pos=3, image="shooting_speed")
            self._appendSlot(pos=4, image="crystals", startVal=4, endVal=8)
            self._appendItemButton()
        
        elif self.game_mode == "versus_2":
            self._appendSlot(pos=1, image="growing_speed")
            self._appendSlot(pos=2, image="crystals", startVal=4, endVal=8)
            self._appendItemButton()
        
        elif self.game_mode == "versus_3":
            self._appendSlot(pos=1, image="growing_speed")
            self._appendSlot(pos=2, image="crystals", startVal=4, endVal=8)
            self._appendItemButton()
        
        if not self.config.get_current_difficulty(self.game_mode) == "custom":
                self.deactivateSlots()
        
    def _appendSlot(self, pos, image, startVal=0, endVal=100, difficulty=False, append=True):
        
        settings_size_left = (self.descr_div.size[0]*0.5, self.descr_div.size[1]*0.13)
        settings_size_right = (self.descr_div.size[0]*0.35, self.descr_div.size[1]*0.13)
        
        left = avg.ImageNode(href=self.theme.getStaticImage(image), 
                            size=settings_size_left,
                            pos=(0,self.descr_div.size[1]*(pos+1)*0.14),
                            parent=self.descr_div
                            )
            
        right = avg.DivNode(
                            size=settings_size_right,
                            pos=(self.descr_div.size[0]*0.6,self.descr_div.size[1]*(pos+1)*0.14),
                            parent=self.descr_div
                            )

        difficulties = ["easy", "medium", "hard", "custom"]
        
        if difficulty==True:
            curr_diff = self.config.get_current_difficulty(self.game_mode)
            initVal = difficulties.index(curr_diff)
        else:
            infos = self.config.get_game_info(self.game_mode, "custom")[0]
            initVal = int(infos[image])
      
        self.Selector(settingsBox=self, setting_name=image, initVal=initVal, parent=right, startVal=startVal, endVal=endVal, difficulty=difficulty)
        
        if append:
            self.slots.append((left,right))
            
    def _appendItemButton(self):
         
        self.itemButton = MenuButton(
                                 upImg="ItemsUp",
                                 downImg="ItemsDown", 
                                 pos=(self.descr_div.size[0]/2,self.descr_div.size[1]-self.descr_div.size[1]*0.1),
                                 size=(self.descr_div.size[0]*0.5, self.descr_div.size[1]*0.13),
                                 clickHandler=lambda event: self._showItemSettings(),
                                 parent=self.descr_div
                                 )
        
         
    def _showItemSettings(self):
        
        self.item_settings = []
        
        new_bg = avg.RectNode(fillcolor="1D1100",fillopacity=1, strokewidth=0, size=self.descr_div.size, parent=self.descr_div)
        self.item_settings.append(new_bg)
        
        back = MenuButton(
                          upImg="BackUp",
                          downImg="BackDown", 
                          pos=(self.descr_div.size[0]/2,self.descr_div.size[1]-self.descr_div.size[1]*0.02),
                          size=(self.descr_div.size[0]*0.5, self.descr_div.size[1]*0.13),
                          clickHandler=lambda event: self._hideItemSettings(),
                          parent=self.descr_div
                          )
        
        self.item_settings.append(back)
        
        items = self.config.get_game_info(self.game_mode, "custom")[1]
        
        cannon = avg.ImageNode(
                               href=self.theme.getStaticImage("Structure"),
                               size=(self.descr_div.size[0]*0.45, self.descr_div.size[1]*0.1),
                               pos=(0,0),
                               parent=self.descr_div
                               ) 
        
        structure = avg.ImageNode(
                               href=self.theme.getStaticImage("Cannon"),
                               size=(self.descr_div.size[0]*0.45, self.descr_div.size[1]*0.1),
                               pos=(self.descr_div.size[0]*0.5,0),
                               parent=self.descr_div
                               ) 
        
        self.item_settings.append(cannon)
        self.item_settings.append(structure)

        
        i=0
        j=7  
        for item in items.keys():
            if item.endswith("Crystal"):
                i = i+1
                self.item_settings.append(self.ItemSelector(item, int(items[item]), i, self).selector_div)
            elif item.endswith("Element"):
                j = j+1
                self.item_settings.append(self.ItemSelector(item, int(items[item]), j, self).selector_div)

        
    def _hideItemSettings(self):
        for element in self.item_settings:
            element.unlink()
                
    def deactivateSlots(self):
        for (left,right) in self.slots:
            left.active = False
            right.active = False
        if not self.itemButton == None:
            self.itemButton.active = False
            
    def activateSlots(self):
        for (left,right) in self.slots:
            left.active = True
            right.active = True
        if not self.itemButton == None:
            self.itemButton.active = True
            
            
    class ItemSelector():
        
        def __init__(self, item, initVal, pos, settingsBox):
            
            self.item = item
            self.current_value = initVal
            self.settingsBox = settingsBox
            
            
            self.__upTimer = None
            self.__downTimer = None
                
            def startContInc():
                self.next(val)
                self.__upTimer = avg.Player.get().setTimeout(1, startContInc)
                
            def stopContInc():
                if self.__upTimer is not None:
                    avg.Player.get().clearInterval(self.__upTimer)
                        
            def startContDec():
                self.prev(val)
                self.__downTimer = avg.Player.get().setTimeout(1, startContDec)
                
            def stopContDec():
                if self.__downTimer is not None:
                    avg.Player.get().clearInterval(self.__downTimer)    
        
            
            theme = settingsBox.theme
            parent = settingsBox.descr_div
            
            if pos < 7:
                self.selector_div = avg.DivNode(
                                           size=(parent.size[0]*0.45, parent.size[1]*0.08),
                                           pos=(0,parent.size[1]*(pos)*0.12),
                                           parent=parent
                                           ) 
            else:
                self.selector_div = avg.DivNode(
                                           size=(parent.size[0]*0.45, parent.size[1]*0.08),
                                           pos=(parent.size[0]*0.5,parent.size[1]*(pos-7)*0.12),
                                           parent=parent
                                           )
                
            button_size = (self.selector_div.size[0]*0.2, self.selector_div.size[1])
            
            avg.ImageNode(
                          href=theme.getStaticImage(item[0:len(item)-7]),
                          size=(self.selector_div.size[0]*0.5, self.selector_div.size[1]),
                          parent=self.selector_div
                          )
            
            dec = MenuButton(
                            upImg="LessUp",
                            downImg="LessDown", 
                            pos=(self.selector_div.size[0]*0.5 + button_size[0]/2, button_size[1]/2),
                            size=button_size,
                            clickHandler=lambda event: self.prev(val),
                            parent=self.selector_div
                            )
            
            inc = MenuButton(
                            upImg="GreaterUp",
                            downImg="GreaterDown", 
                            pos=(self.selector_div.size[0]*0.8 + button_size[0]/2, button_size[1]/2),
                            size=button_size,
                            clickHandler=lambda event: self.next(val),
                            parent=self.selector_div
                            )
            
            val = avg.WordsNode(
                                text=str(self.current_value)+"%",
                                pos=(self.selector_div.size[0]*0.65 + button_size[0]/2, self.selector_div.size[1]*0.1),
                                size=button_size,
                                alignment="center",
                                fontsize=30,
                                color="FF9600",
                                parent=self.selector_div,
                                sensitive=False
                                )
            
            ui.HoldRecognizer(node=inc,
                              detectedHandler=lambda event: startContInc(),
                              stopHandler=lambda event: stopContInc()
                              )
            
            ui.HoldRecognizer(node=dec,
                              detectedHandler=lambda event: startContDec(),
                              stopHandler=lambda event: stopContDec()
                              )
            
        def next(self, val):
                self.current_value = (self.current_value + 1) % 101
                val.text = str(self.current_value) + "%"
                self.settingsBox.config.set_item_probability(self.settingsBox.game_mode, self.item, str(self.current_value))
                
        def prev(self, val):
                self.current_value = (self.current_value - 1) % 101
                val.text = str(self.current_value) + "%"
                self.settingsBox.config.set_item_probability(self.settingsBox.game_mode, self.item, str(self.current_value))

            
    class Selector():
        
        def __init__(self, settingsBox, setting_name, parent, initVal, startVal, endVal, difficulty):
            
            self.setting_name = setting_name
            self.parent = parent
            self.startVal = startVal
            self.endVal = endVal
            self.current_value = initVal
            self.settingsBox = settingsBox
            
            self.difficulty = difficulty
            self.difficulties = ["easy", "medium", "hard", "custom"]
            
            self.__upTimer = None
            self.__downTimer = None
            
            def startContInc():
                self.next(val)
                self.__upTimer = avg.Player.get().setTimeout(1, startContInc)
            
            def stopContInc():
                if self.__upTimer is not None:
                    avg.Player.get().clearInterval(self.__upTimer)
                    
            def startContDec():
                self.prev(val)
                self.__downTimer = avg.Player.get().setTimeout(1, startContDec)
            
            def stopContDec():
                if self.__downTimer is not None:
                    avg.Player.get().clearInterval(self.__downTimer)    

        
            dec = MenuButton(
                            upImg="LessUp",
                            downImg="LessDown", 
                            pos=(self.parent.size[0]*0.2*0.5, self.parent.size[1]/2),
                            size=(self.parent.size[0]*0.2, self.parent.size[1]),
                            pressHandler=lambda event: self.prev(val),
                            parent=self.parent
                            )
            
            inc = MenuButton(
                            upImg="GreaterUp",
                            downImg="GreaterDown", 
                            pos=(self.parent.size[0]-self.parent.size[0]*0.2*0.5,self.parent.size[1]/2),
                            size=(self.parent.size[0]*0.2, self.parent.size[1]),
                            pressHandler=lambda event: self.next(val),
                            parent=self.parent
                            )
            
            val = avg.WordsNode(
                                text=self._getText(),
                                pos=(self.parent.size[0]/2,self.parent.size[1]*0.1),
                                size=(self.parent.size[0]*0.6, self.parent.size[1]),
                                alignment="center",
                                fontsize=30,
                                color="FF9600",
                                parent=self.parent,
                                sensitive=False
                                )
            
            ui.HoldRecognizer(node=inc,
                              detectedHandler=lambda event: startContInc(),
                              stopHandler=lambda event: stopContInc()
                              )
            
            ui.HoldRecognizer(node=dec,
                              detectedHandler=lambda event: startContDec(),
                              stopHandler=lambda event: stopContDec()
                              )
  
            
        def next(self, val, stepSize=1):
                self.current_value = ((self.current_value - self.startVal + stepSize) % (self.endVal - self.startVal + 1)) + self.startVal
                
                val.text = self._getText()
                    
                self.settingsBox.config.set_setting(game_mode=self.settingsBox.game_mode,
                                                   id=self.setting_name,
                                                   new_val=self._getText())
                
                if not (val.text == "custom") and self.setting_name == "difficulty":
                    self.settingsBox.deactivateSlots()
                else:
                    self.settingsBox.activateSlots()
                
                
        def prev(self, val, stepSize=1):
                self.current_value = ((self.current_value - self.startVal - stepSize) % (self.endVal - self.startVal + 1)) + self.startVal
                
                val.text = self._getText()
                    
                self.settingsBox.config.set_setting(game_mode=self.settingsBox.game_mode,
                                                   id=self.setting_name,
                                                   new_val=self._getText())
                
                if not (val.text == "custom") and self.setting_name == "difficulty":
                    self.settingsBox.deactivateSlots()
                else:
                    self.settingsBox.activateSlots()
                    
                    
        def _getText(self):
            if self.difficulty:
                return self.difficulties[self.current_value]
            else: 
                return str(self.current_value)
            
        

class HighscoreBox(Box):
    
    def __init__(self, mainMenu, theme=themes.StandardTheme(), **kwargs): 
        
        Box.__init__(self, mainMenu, **kwargs)        
        self.__mode = 0
        

        
        highscore_div = avg.DivNode(
                                    pos=(0, 0),
                                    size=(self.size[0], self.size[1]),
                                    parent=self,
                                    )
        
        self.__mode_div = avg.DivNode(pos=(0, 0), size=(self.size[0], self.size[1] // 4), parent=highscore_div)
        
        
        choose_left = MenuButton(
                                   upImg="LessUp",
                                   downImg="LessDown",
                                   pos=(self.size[0] // 8, self.size[0] // 10),
                                   size=(self.size[0] // 8, self.size[1] // 7),
                                   parent=self.__mode_div,
                                   clickHandler=lambda event: self.__switchMode(-1))
        
        self.__caption = self._theme.getNode("city_defense")(
                               pos=(self.size[0] // 10 * 2.5, (self.size[0] // 4 - self.size[0] // 7) // 2),
                               size=(self.size[0] // 2, self.size[1] // 7),
                               parent=self.__mode_div
                               )
        
        choose_right = MenuButton(
                                    upImg="GreaterUp",
                                    downImg="GreaterDown",
                                    pos=(self.size[0] // 8 * 7 , self.size[0] // 10),
                                    size=(self.size[0] // 8, self.size[1] // 7),
                                    parent=self.__mode_div,
                  
                                    clickHandler=lambda event: self.__switchMode(1))
        
        self.appendChild(self._cancel_button)               
        self.active = False
        self.__highscoreDiv = None
        self.__switchMode(0)
        
    def __switchMode(self, amount):
        self.__mode = (self.__mode + amount) % 3
        
        self.__caption.unlink(True)
        if self.__mode == 0:
            captionNode = self._theme.getNode("city_defense")
            
        elif self.__mode == 1:
            captionNode = self._theme.getNode("versus_2")
        else:
            captionNode = self._theme.getNode("versus_3")

        self.__caption = captionNode(
                   pos=(self.size[0] // 10 * 2.5, (self.size[0] // 4 - self.size[0] // 6) // 2),
                   size=(self.size[0] // 2, self.size[1] // 7),
                   parent=self.__mode_div
                   )  
            
        self.__highscore = Highscore(str(self.__mode))
        
        if self.__highscoreDiv:
            self.__highscoreDiv.unlink(True)
        self.__highscoreDiv = avg.DivNode(parent=self)
                
        self.__highscoreDiv.pos = (self.size[0] // 10, self.size[1] // 4)
        self.__highscoreDiv.size = (self.size[0] // 10 * 8, self.size[1] // 4 * 3 - self.size[1] // 10)
        
        self.__highscore.readHighscore()
        for i, entry in enumerate(self.__highscore.entries):
            avg.WordsNode(text=("%02i" % (i + 1)) + ". " + unicode(entry[0]), color="FEFB00", fontsize=20, pos=(0, i * self.size[1] // 16), parent=self.__highscoreDiv)
            avg.WordsNode(text=str(entry[1]) + " ", color="FEFB00", fontsize=20, pos=(self.size[0] // 5 * 4, i * self.size[1] // 16), alignment="right", parent=self.__highscoreDiv)

                        
class StoryBox(Box):
    
    def __init__(self, mainMenu, **kwargs): 
        
        
        Box.__init__(self, mainMenu, **kwargs)   
        self.captureHolder = None          
        self.__mode = 0
        self.__downTimer = None
        self.__upTimer = None
        avg.ImageNode(
                      href=os.path.join(util.IMAGE_PATH , "menu/chooser/chooser.png"),
                      size=self.size,
                      parent=self
                      )
        
        
        box_div = avg.DivNode(
                                    pos=(self.size[0]//15, self.size[1]//10*2.25),
                                    size=(self.size[0]// 8 *6,  self.size[1]//10*6.75),
                                    parent=self,
                                    crop=True
                                    )
        
        words = avg.WordsNode(parent=box_div, width=self.size[0]// 8 *6, text="""Once upon a time, four mighty dwarf clan leaders explored caves in the mountains of Kreska'don, their names will never be forgotten: Gire Malachitkeeper, Azur Giantcrusher, Rubeus Marbleslasher and Citrio Swordcarver. <br/>
 <br/>
In the deepest cave of Kreska'don they found  rainbow crystals of a beauty and quality never found before. They took some of these crystals and brought them back to their lair, unknowing that this would awaken a grave danger in the depth of the cave. Soon they realized that with this crystal devastating weapons could be forged. They send this message to their clan strongholds and they returned to the darkness to collect more of the crystals ... and they disappeared.  <br/>
The crystals of this very cave were not only beautiful and precious but they were intelligent and had the magic abilities to create small crystals by themselves. As kind of a community they made a consensus that none of them would be stolen again and hide their beauty nature with the mask of a beast and turned black and evil. As the four clan leaders returned, they got more crystals as they had ever wanted as the rainbow crystals start to use their magic ability. Soon the cave was full of small crystals and buried the clan leaders. <br/>
 <br/>
Months ago fellow clan members of all four clans came to these mountains with the mission to found their leaders. Torgus Malachitkeeper, the son of Gire and most intelligent dwarf, found out what happened to them and realized the magic nature of the crystals: Destroying small crystals will weaken the magic of a rainbow crystal and would break their appearance. By a coincidence they found out, that the small crystals can not be taken by raw force. The magic makes it necessary that three or more of a kind would make them disappear. Torgus requested crystals of their settlements to accomplish this task and more dwarfs to help him to revenge the clan leaders. Many followed his call and many different entries to that cave were found. And first rainbow crystals were collected by brave dwarven adventures. <br/> 
 <br/>
Weeks later, the rainbow crystals that are remaining in the cave developed new ways of defending themselves. Special crystals were grown and made the quest of these adventures deadlier. In the strongholds, Torgus requested that dwarves should learn how to face that enemy and with the help of their sorcerers they created a cave in which young adventures may learn how to fight against a growing structure of crystals. Nowadays, two or three adventures fight against each other to improve their skill for the fight against the evil rainbow crystals...""", fontsize=20, justify=True)
        
        def startDragging(event):
            if self.captureHolder is None:
                self.captureHolder=event.cursorid
                self.dragOffset = words.pos.y - event.pos.y
                event.node.setEventCapture(event.cursorid)
            
    
        def doDragging(event):
            if event.cursorid==self.captureHolder:
                words.pos=(words.pos.x, event.pos.y+self.dragOffset)
                print words.pos
                if words.pos[1] > 0:
                    words.pos = 0,0
                if words.pos[1] < -(words.getMediaSize()[1]-box_div.size[1]):
                    words.pos = 0,-(words.getMediaSize()[1]-box_div.size[1])
                
        def endDragging(event):
            if event.cursorid==self.captureHolder:
                event.node.releaseEventCapture(event.cursorid)
                self.captureHolder=None
            
            
        words.setEventHandler(avg.CURSORDOWN,avg.TOUCH, startDragging)
        words.setEventHandler(avg.CURSORMOTION,avg.TOUCH, doDragging)
        words.setEventHandler(avg.CURSORUP,avg.TOUCH, endDragging)
        
        def startScrollUp():
            if words.pos[1]<0:
                words.pos=words.pos[0], words.pos[1]+5
                self.__upTimer = avg.Player.get().setTimeout(1, startScrollUp)
            
        def stopScrollUp():
            if self.__upTimer is not None:
                avg.Player.get().clearInterval(self.__upTimer)
        
        def startScrollDown():
            if words.pos[1]>-(words.getMediaSize()[1]-box_div.size[1]):    
                words.pos=words.pos[0], words.pos[1]-5
                self.__downTimer = avg.Player.get().setTimeout(1, startScrollDown)
            
        def stopScrollDown():
            if self.__downTimer is not None:      
                avg.Player.get().clearInterval(self.__downTimer)
        
        moveUp = MenuButton(
                                 upImg="UpUp",
                                 downImg="UpDown",
                                 pos=(self.size[0] // 8 * 7 , self.size[1] // 10*3),
                                 size=(self.size[0] // 10, self.size[1] // 5),
                                 parent=self,
                                 pressHandler=lambda event: startScrollUp(),
                                 clickHandler=lambda event: stopScrollUp())
        
#        self.__caption = self._theme.getNode("CityDefense")(
#                                                            pos=(self.size[0] // 10 * 2.5, (self.size[0] // 4 - self.size[0] // 7) // 2),
#                                                            size=(self.size[0] // 2, self.size[1] // 7),
#                                                            parent=self
#                                                            )
        
        avg.ImageNode(href=self._theme.getStaticImage("Story"), 
                                       pos=(self.size[0] // 10 * 2.5, (self.size[0] // 4 - self.size[0] // 7) // 2),
                                       size=(self.size[0] // 2, self.size[1] // 7),
                                       parent=self
                                       )
        
        moveDown = MenuButton(
                                  upImg="DownUp",
                                  downImg="DownDown",
                                  pos=(self.size[0] // 8 * 7 , self.size[1] // 10*8.5),
                                  size=(self.size[0] // 10, self.size[1] // 5),
                                  parent=self,
                                 pressHandler=lambda event: startScrollDown(),
                                 clickHandler=lambda event: stopScrollDown())
        
        
        self.appendChild(self._cancel_button)
        
        self.active = False        
        
   
        

      
