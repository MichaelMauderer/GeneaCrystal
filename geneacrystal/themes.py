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
import functools
from geneacrystal import nodes, util
import itertools
import logging


class Theme(object):
    """
    A theme contains attributes holding node classes that can be instantiated 
    and already contain some information about their appearance, mostly the
    used image file.
    
    To create a theme, subclass the Theme and add attributes holding the 
    required information. 
    Different kinds of node types are grouped in namespaces and as of now there
    are the CenteredImages and Images. (Look there for further information on what
    they do.)
    
    The nodes can be retrieved either by accessing the according attribute
    directly in the theme object (no namespace required!) or by using the
    getNode method with a string containing the name of the desired node. 
    
    """
    
    prefix=""
    
    NoImageAvailable="na.png"
    
    class CenteredImages():
        """
        Centered images are contained into ItemImageNodes.
        This means they will have a centered coordinate system.
        For an example on how to use this, please look at the StandardTheme.
        """
        pass
    
    class Images():
        """
        Images will be turned into avg.ImageNodes
        For an example on how to use this, please look at the StandardTheme.
        """
        pass
    
    class MenuImages():
        """
        MenuImages will be turned into avg.ImageNodes
        For an example on how to use this, please look at the StandardTheme.
        
        """
        pass

    class KeyboardImages():
        """
        KeyboardImages will be turned into avg.ImageNodes
        For an example on how to use this, please look at the StandardTheme.
        
        """
        pass
    
    class InfoImages():
        pass
    
    class SettingImages():
        pass


    
    class CrystalOverlayNodes():
        basesLayers = [{"Red": "",
                        "Green": "",
                        "Yellow": "",
                        "Blue": "",
                        },
                       ]
        
    class SingleOverlayNodes():
        baseLayers = [{"Red": "",
                        "Green": "",
                        "Yellow": "",
                        "Blue": "",
                        },
                      {"Silver": "", 
                        "Gold": "",
                        },
                       
                       ]
   
    def __init__(self):
        self.statics = dict()
        
        self.NoImageAvailablePath = self._makeImagePath(self.NoImageAvailable)
        self.NoImageAvailable = functools.partial(avg.ImageNode,
                                                  href=self.NoImageAvailablePath)
        self.wrapNamespaceForImage(self.CenteredImages, nodes.ItemImageNode)
        self.wrapNamespaceForImage(self.Images, avg.ImageNode)
        self.wrapNamespaceForImage(self.MenuImages, avg.ImageNode)
        self.wrapNamespaceForImage(self.SettingImages, avg.ImageNode)
        self.wrapNamespaceForImage(self.InfoImages, avg.ImageNode)
        self.wrapNamespaceForImage(self.KeyboardImages, avg.ImageNode)
        self.wrapNamespaceForLayeredImage(self.SilverOverlayNodes, nodes.ItemImageLayeredNode)
        self.wrapNamespaceForLayeredImage(self.BlackOverlayNodes, nodes.ItemImageLayeredNode)
        self.wrapNamespaceForLayeredImage(self.CrystalOverlayNodes, nodes.ItemImageLayeredNode)
        
        
    def wrapNamespaceForImage(self, namespace, nodeClass ):
        nodesToMake = filter( lambda s: not s.startswith("_"), namespace.__dict__)
        for nodeName in nodesToMake:
            imageToUse = getattr(namespace, nodeName)    
            assert(isinstance(imageToUse, basestring))
            imagePath = self._makeImagePath(imageToUse)
            self.statics[nodeName] = imagePath
            preparedConstructor = functools.partial(nodeClass, href=imagePath )
            setattr(self, nodeName, preparedConstructor)
                
    def wrapNamespaceForLayeredImage(self, namespace, nodeClass):
        nodesToMake = self._filterNamespace(namespace, ["baseLayers"])
        baseLayers = getattr(namespace, "baseLayers")
        
        for baseNodeName in nodesToMake:
            imageToUse = getattr(namespace, baseNodeName)
            assert(isinstance(imageToUse, basestring))
            for layerNames in itertools.product(*baseLayers):
                nodeName = "".join(layerNames) + baseNodeName
                paths = [layer[name] for name, layer in zip(layerNames, baseLayers)]
                paths += [getattr(namespace, baseNodeName)]
                paths = map(self._makeImagePath, paths)
                preparedConstructor = functools.partial(nodeClass,
                                                layers=paths )
                setattr(self, nodeName, preparedConstructor)
                    
            
    def __getattribute__(self, *args, **kwargs):
        try: 
            return object.__getattribute__(self, *args, **kwargs)
        except AttributeError as e:
            logging.warn("No image for name found: %s" % e )
            return self.NoImageAvailable
        
    def _filterNamespace(self, namespace, toRemove=[]):
        return filter( lambda s: not s.startswith("_") and not s in toRemove
                      , namespace.__dict__)
   
    def _makeImagePath(self, imagePath):
        relPath = os.path.join(self.preFix, imagePath)
        absPath = os.path.abspath(relPath)
        return absPath
   
    def getStaticImage(self, name):
        try:
            return self.statics[name]
        except KeyError:
            logging.warn("No image for name found: %s" % name )
            return self.NoImageAvailablePath
        
    def getNode(self, name):
        return getattr(self, name)


class StandardTheme(Theme):
    
    preFix = util.IMAGE_PATH
    
    class CenteredImages():
        BlueCrystal = "jewels/blue.png"
        YellowCrystal = "jewels/yellow.png"
        GreenCrystal = "jewels/green.png"
        RedCrystal = "jewels/red.png"
        OrangeCrystal = "jewels/orange.png"
        PurpleCrystal = "jewels/purple.png"
        PinkCrystal = "jewels/pink.png"
       
        JokerCrystal = "jewels/rainbow.png"
        ExplosionCrystal = "jewels/rainbow.png"
        AggressionCrystal = "jewels/rainbow.png" 
        RandomizationCrystal = "jewels/rainbow.png"
        CityFreezeCrystal = "jewels/rainbow.png"
        CityBlockCrystal = "jewels/rainbow.png"
        SlowCrystal = "jewels/rainbow.png"
        AgressiveCrystal = "jewels/monster2.png"
     
        CenterCrystal = "jewels/rainbow.png"
        MonsterCrystal = "jewels/monster2.png"
        
        BaseDiagonal3Room = "game/stationDivided.png"
        BaseDiagonal2Room = "game/stationDivided2.png"
        BaseAligned = "game/stationAligned.png"
     
    class Images():
        City = "game/long_city.png"  
        FreezeCity = "game/long_city_frozen.png" 
        JoinButton = "game/join.png"
        Wall = "info/brick.png"
        TouchPointNode = "game/touchPointNode.png"
        
        GameBackGround = "game/game_bg.png"
        VsGameBackGround = "game/game_bg_vs.png"
        
        ExitButton ="game/x.png"
     
    class MenuImages():
        
        CoopUp = "menu/coop_up.png"
        CoopDown = "menu/coop_down.png"
        
        VersusUp = "menu/versus_up.png"
        VersusDown = "menu/versus_down.png"

        HighscoreUp = "menu/highscores_up.png"
        HighscoreDown = "menu/highscores_down.png"
        
        ChooserInfo = "menu/chooser/info.png"
        ChooserSettings = "menu/chooser/settings.png"
        
        ChooserScreenshot_city_defense = "menu/chooser/screenshot_city_defense.png"
        ChooserScreenshot_come_n_play = "menu/chooser/screenshot_come_n_play.png"
        ChooserScreenshot_versus_2 = "menu/chooser/screenshot_versus_2.png"
        ChooserScreenshot_versus_3 ="menu/chooser/screenshot_versus_3.png"
        
        ChooserCancelDown = "menu/chooser/cancel_down.png"
        ChooserCancelUp = "menu/chooser/cancel_up.png"
        
        ChooserAcceptDown = "menu/chooser/accept_down.png"
        ChooserAcceptUp = "menu/chooser/accept_up.png"
        
        LessUp = "menu/settings/less_up.png"
        LessDown = "menu/settings/less_down.png"
        
        GreaterUp = "menu/settings/greater_up.png"
        GreaterDown = "menu/settings/greater_down.png"

        UpUp = "menu/settings/up_up.png"
        UpDown = "menu/settings/up_down.png"
        
        DownUp = "menu/settings/down_up.png"
        DownDown = "menu/settings/down_down.png"
        
        versus_2 = "menu/versus_2.png"
        versus_3 = "menu/versus_3.png"
        come_n_play = "menu/come_n_play.png"
        city_defense = "menu/city_defense.png"
        
        LeftDoor = "game/door_left.png"
        RightDoor = "game/door_right.png"
        
        StoryUp = "menu/story_up.png"
        StoryDown = "menu/story_down.png"
        Story = "menu/story.png"
        
    class SettingImages():
        
        difficulty = "menu/settings/difficulty.png"
        growing_speed = "menu/settings/growing_speed.png"
        rotation_speed = "menu/settings/rotation_speed.png"
        shooting_speed = "menu/settings/shooting_speed.png"
        crystals = "menu/settings/crystals.png"
        
        ItemsUp = "menu/settings/items_up.png"
        ItemsDown = "menu/settings/items_down.png"
        
        BackUp = "menu/settings/back_up.png"
        BackDown = "menu/settings/back_down.png"
        
        Structure = "menu/settings/items/Structure.png"
        Cannon = "menu/settings/items/Cannon.png"
        
        Aggression = "menu/settings/items/Aggression.png"
        CCWRotation = "menu/settings/items/CCWRotation.png"
        CWRotation = "menu/settings/items/CWRotation.png"
        Colored = "menu/settings/items/Colored.png"
        Eater = "menu/settings/items/Eater.png"
        Explosion = "menu/settings/items/Explosion.png"
        Hidden = "menu/settings/items/Hidden.png"
        Indestructible = "menu/settings/items/Indestructible.png"
        Spawn = "menu/settings/items/Spawn.png"
        Veil = "menu/settings/items/Veil.png"
     
     
    class InfoImages():
        
        InfoBoxBackground = "info/infoBoxBg.png"
        InfoButton = "info/showInfo.png"

        cannon_cap = "info/cannon_cap.png"
        cannon_cd = "info/cannon_cd.png"
        block = "info/block.png"
        goal_cap = "info/goal_cap.png"
        goal_cd = "info/goal_cd.png"
        goal_versus = "info/goal_versus.png"
        ingame_help = "info/ingame_help.png"
        items = "info/items.png"
        direction = "info/direction_change.png"
        
    class KeyboardImages():
        
        backspaceSymbol = "keyboard/backspaceSymbol.png"
        enterSymbol = "keyboard/enterSymbol.png"
        keySymbol = "keyboard/keySymbol.png"
        shiftSymbol = "keyboard/shiftSymbol.png"
        spaceSymbol = "keyboard/spaceSymbol.png"
        
        
    class CrystalOverlayNodes():
        baseLayers = [{"Red": "jewels/red.png",
                        "Green": "jewels/green.png",
                        "Yellow": "jewels/yellow.png",
                        "Blue": "jewels/blue.png",
                        "Orange": "jewels/orange.png",
                        "Pink": "jewels/pink.png",
                        "Purple": "jewels/purple.png",
                        },
                       ]
        EaterCrystal = "jewels/items/eater.png"
        CCWCrystal = "jewels/items/ccw.png"
        CWRotationCrystal = "jewels/items/cw.png"
      
    
    class SilverOverlayNodes():
        baseLayers = [{"": "jewels/silver.png",
                        }, 
                       ]
        
        ExplosionCrystal = "jewels/items/explosion.png"
        FlyingEaterCrystal = "jewels/items/eater.png"
        StaticEaterCrystal = "jewels/items/eater.png"
        HiddenCrystal = "jewels/items/hide.png"
        IndestructibleCrystal = "jewels/items/boss.png"
        FreezeCrystal = "jewels/items/freezer.png"
        
     
    class BlackOverlayNodes():
        baseLayers = [{"": "jewels/black.png",
                        }, 
                       ]
        
        BulletCrystal = "jewels/items/bullet.png"
        VeilCrystal = "jewels/items/veil.png"
        
        SpawnCrystal = "jewels/items/spawn.png"
        
        
DefaultTheme = StandardTheme()
        