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

class Help():
    
    def __init__(self, game_mode):
        self.pages = []
        
        help = dom.parse(os.path.join(util.XML_PATH, "help.xml"))
        
        print game_mode
        
        for entry in help.childNodes:
            for mode in entry.childNodes:
                if mode.nodeName == game_mode:
                    for page in mode.getElementsByTagName("page"):
                        p = Page(page.getAttribute("heading"), page.getAttribute("pic"), page.getAttribute("text"))
                        self.pages.append(p)
                        
        
class Page():
    
    def __init__(self, heading, picture, text):
        
        self.heading = heading
        self.picture = picture
        self.text = text
        