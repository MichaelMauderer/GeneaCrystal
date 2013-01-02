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
from geneacrystal.keyboard import Keyboard


class AlphaKeyboard(Keyboard):
    """
    This class represents a letter keyboard.
    """
        
    def __init__(self, bgImg, backImg, enterImg, shiftImg, emptyImg, onKeyDown=None, onKeyUp=None, onBack=None, onEnter=None, *args, **kwargs):
        keyHeight = kwargs.setdefault('size', (0,0))[1] / 4
        keywidth = kwargs.setdefault('size', (0,0))[0] / 12
        keySpacing = 2
        keyDefs = Keyboard.makeRowKeyDefs((keywidth / 2, 0), (keywidth, keyHeight), keySpacing, u"qwertyuiop", u"QWERTYUIOP", bgImg)
        keyDefs.append(["BACKSPACE", (10.5 * (keywidth + keySpacing), 0), (keywidth * 1.5, keyHeight), bgImg, backImg])
        keyDefs.extend(Keyboard.makeRowKeyDefs((keywidth, keyHeight + keySpacing), (keywidth, keyHeight), keySpacing, u"asdfghjkl", u"ASDFGHJKL", bgImg))
        if onEnter is not None:
            keyDefs.append(["ENTER", (10 * (keywidth + keySpacing), keyHeight + keySpacing), (2 * keywidth, keyHeight), bgImg, enterImg])
        keyDefs.extend(Keyboard.makeRowKeyDefs((1.5*keywidth+keySpacing, 2 * (keyHeight + keySpacing)), (keywidth, keyHeight), keySpacing, u"zxcvbnm,.-", u"ZXCVBNM;:_", bgImg))
        keyDefs.append(["SHIFT", (0, 2 * (keyHeight + keySpacing)), (1.5 * keywidth, keyHeight), bgImg, shiftImg])
        keyDefs.append([(' ', ' '), (2 * keywidth, 3 * (keyHeight + keySpacing)), (8 * keywidth, keyHeight), emptyImg])
      
        super(AlphaKeyboard, self).__init__(keyDefs,*args, **kwargs)
        
        self.setKeyHandler(onKeyDown, onKeyUp, onBack, onEnter)
