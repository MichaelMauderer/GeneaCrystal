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


class MenuButton(ui.Button):
    
    def __init__(self, upImg, downImg, size, pos, theme=themes.StandardTheme(), **kwargs):
        
        upNode = theme.getNode(upImg)(size=size)
        downNode = theme.getNode(downImg)(size=size)
                
        transl_pos = (pos[0]-size[0]/2, pos[1]-size[1]/2)
        
        ui.Button.__init__(self, upNode=upNode, downNode=downNode, pos=transl_pos, size=size, **kwargs)