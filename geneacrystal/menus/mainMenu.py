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
import os
from geneacrystal import util
from geneacrystal.menus.boxes import ChooserBox, HighscoreBox
from geneacrystal.menus.button import MenuButton
from geneacrystal.menus.boxes import StoryBox


class MainMenu(avg.DivNode):
    
    def __init__(self, start_cap_mode, start_city_defense_mode, start_versus_2_mode, start_versus_3_mode, *args, **kwargs):    
        avg.DivNode.__init__(self, *args, **kwargs)
        
        self.start_cap_mode = start_cap_mode
        self.start_city_defense_mode = start_city_defense_mode
        self.start_versus_2_mode = start_versus_2_mode
        self.start_versus_3_mode = start_versus_3_mode
        
        main_bg = avg.ImageNode(
                                href=os.path.join(util.IMAGE_PATH , "menu/main_bg.png"), 
                                size=(util.WINDOW_SIZE[0],util.WINDOW_SIZE[1]), 
                                parent=self
                                )
        
        self.bg_rect = avg.RectNode(
                                    size=(util.WINDOW_SIZE[0], util.WINDOW_SIZE[1]),
                                    fillopacity=0,
                                    fillcolor="000000",
                                    strokewidth=0,
                                    parent=self
                                    )
        
        genea_crystal_size = (util.WINDOW_SIZE[0]*0.7, util.WINDOW_SIZE[1]/6)
        
        genea_crystal = avg.ImageNode(
                                      href=os.path.join(util.IMAGE_PATH , "menu/genea_crystal.png"), 
                                      pos=(util.WINDOW_SIZE[0]/2-0.5*genea_crystal_size[0], util.WINDOW_SIZE[1]*0.1),
                                      size=genea_crystal_size,
                                      parent=self
                                      )
        
      
        
        button_size = (util.WINDOW_SIZE[0]/2, util.WINDOW_SIZE[1]/8)
        
        coop_button = MenuButton(
                                 upImg="CoopUp", 
                                 downImg="CoopDown", 
                                 pos=(util.WINDOW_SIZE[0]/2, util.WINDOW_SIZE[1]*0.4),
                                 size=button_size, 
                                 clickHandler=lambda event : self.coop_chooser.slideInFromLeft(),
                                 parent=self
                                 )
        
        versus_button = MenuButton(
                                   upImg="VersusUp", 
                                   downImg="VersusDown", 
                                   pos=(util.WINDOW_SIZE[0]/2, util.WINDOW_SIZE[1]*0.6),
                                   size=button_size, 
                                   clickHandler=lambda event : self.versus_chooser.slideInFromLeft(),
                                   parent=self
                                   )
        
        highscores_button = MenuButton(
                                       upImg="HighscoreUp", 
                                       downImg="HighscoreDown", 
                                       pos=(util.WINDOW_SIZE[0]/2, util.WINDOW_SIZE[1]*0.8),
                                       size=button_size, 
                                       clickHandler=lambda event : self.highscore_div.slideInFromLeft(),
                                       parent=self
                                       )
        
        story_button = MenuButton(
                                  upImg="StoryUp",
                                  downImg="StoryDown",
                                  pos=(util.WINDOW_SIZE[0]*0.28,util.WINDOW_SIZE[1]*0.85),
                                  size=(util.WINDOW_SIZE[0]/10,util.WINDOW_SIZE[0]/10),
                                  clickHandler=lambda event : self.storyDiv.slideInFromLeft(),
                                  parent=self
                                  )
        
        
        chooser_size = (util.WINDOW_SIZE[0]*0.7, util.WINDOW_SIZE[1]*0.7)
        chooser_pos_x = (util.WINDOW_SIZE[0]/2-chooser_size[0]/2)
        chooser_pos_y = (util.WINDOW_SIZE[1]/2-chooser_size[1]/2)
        
        self.coop_chooser = ChooserBox(
                                       mainMenu=self, 
                                       game_mode_left="come_n_play",
                                       game_mode_right="city_defense",
                                       pos=(chooser_pos_x,chooser_pos_y),
                                       size=chooser_size, 
                                       parent=self
                                       )
        
        self.versus_chooser = ChooserBox(
                                         mainMenu=self, 
                                         game_mode_left="versus_2",
                                         game_mode_right="versus_3",
                                         pos=(chooser_pos_x,chooser_pos_y),
                                         size=chooser_size, 
                                         parent=self
                                         )
        
        self.highscore_div = HighscoreBox(
                                          mainMenu=self,
                                          pos=(chooser_pos_x, chooser_pos_y),
                                          size=(chooser_size[0]*0.8,chooser_size[1]),
                                          parent=self
                                          )
        
        self.storyDiv = StoryBox(
                                  mainMenu=self,
                                  pos=(chooser_pos_x, chooser_pos_y-chooser_size[1]//8),
                                  size=(chooser_size[0]*.9,chooser_size[1]*1.25),
                                  parent=self
                                  )
        
    def start_game_mode(self, game_mode):
        if game_mode == "come_n_play": 
            return self.start_cap_mode
        elif game_mode == "city_defense":
            return self.start_city_defense_mode
        elif game_mode == "versus_2":
            return self.start_versus_2_mode
        elif game_mode == "versus_3":
            return self.start_versus_3_mode
        else:
            return None
        
       