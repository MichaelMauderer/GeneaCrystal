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


class BaseStructure():
    
    def __init__(self, pos, growing, growing_time, mapFile):
        
        self.pos = pos
        self.growing = growing
        self.growing_time = growing_time
        self.mapFile = mapFile
     
        
class StructureVersus(BaseStructure):
    
    def __init__(self, pos, growing, growing_time, player, mapFile):
        BaseStructure.__init__(self, pos, growing, growing_time, mapFile)
        self.player = player
        
    def dump(self):
        print "+++++ BaseStructure Versus +++++"
        print "pos = " + str(self.pos)
        print "growing = " + str(self.growing)
        print "growing_time = " + str(self.growing_time)
        print "player = " + str(self.player)
        print "+++++++++++++++++++++++++++++"
  

class StructureComePlay(BaseStructure):
    
    def __init__(self, pos, growing, growing_time, rotation_speed, mapFile):
        BaseStructure.__init__(self, pos, growing, growing_time, mapFile)
        self.rotation_speed = rotation_speed
        
    def dump(self):
        print "+++++ BaseStructure Come'n'Play +++++"
        print "pos = " + str(self.pos)
        print "growing = " + str(self.growing)
        print "growing_time = " + str(self.growing_time)
        print "rotation_speed = " + str(self.rotation_speed)
        print "+++++++++++++++++++++++++++++"