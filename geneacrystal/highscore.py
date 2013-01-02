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
import os
from geneacrystal import util


class Highscore(object):
    """
    Highscore object manages the highscore data and how it is showed.
    """
    
    def __init__(self, mode, path=util.HIGHSCORE_PATH, length = util.MAX_HIGHSCORE_LENGTH):
        self._path = os.path.join(path,".geneaCrystal")
        if not os.path.exists(self._path): 
            os.mkdir(self._path)

        self.entries = []
        self.scores = []
        
        self._path
        
        self._path = os.path.join(self._path,mode)
        if not os.path.exists(self._path):          
            try:
                fobj = open(self._path,"w")
            finally:
                fobj.close()
            
        self._length = length
        
        self.readHighscore()
    
    def readHighscore(self):
        self.entries = []
        self.scores = []
         
        with open(self._path,"r") as f:
            for line in f:
                readStr = line.strip().split("\t")
                self.scores.append(readStr[1])
                self.entries.append(readStr)
        
    def addEntry(self, name, score):
        """
        Adds an entry in the highscore
        """
        if self.entries:
            for i, entry in enumerate(self.entries):
                if int(entry[1]) <=  score:
                    self.entries.insert(i, [name, score])
                    break
            else:
                self.entries.append([name, str(score)])
        else:
            self.entries.append([name, str(score)])
             
        if len(self.entries) > self._length:
            del self.entries[self._length:]
                
        with open(self._path, "w") as f:          
            c=""
            for entry in self.entries:
                f.write(c)
                f.write(unicode(entry[0]) + "\t" +  str(entry[1]))
                c="\n"
