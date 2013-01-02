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
from __future__ import division
import collections
import random
from geneacrystal.gameElements import items, structures
import itertools
import inspect
from geneacrystal import gameElements


def _discoversSublassesFromModule(cls, module):    
    clsList = []
    for obj in module.__dict__.values():
        if inspect.isclass(obj) and issubclass(obj, cls):
            clsList.append(obj)
    return clsList

_items = _discoversSublassesFromModule(items.Item, items)
_itemMap = {item.__name__: item for item in _items}
_elements = _discoversSublassesFromModule(structures.StructureElement, structures)
_elementMap = {element.__name__:element for element in _elements}

if __debug__:
    print  "---------------------"
    for key in _itemMap:
        print '<item type="{}" probability="1"/>'.format(key)
    for key in _elementMap:
        print  '<item type="{}" probability="1"/>'.format(key)
    print  "---------------------"    
    

class CrystalManager(object):
      
    def __init__(self, weights, numberOfColors = 3):
        assert weights
        self._weightedItems = self._makeWeightedList(weights, _itemMap)
        self._weightedElements = self._makeWeightedList(weights, _elementMap)
        self._numberOfColors = min(numberOfColors, len(gameElements.availableColors))
        self._structures = []
        assert len(self._weightedItems) != 0
        assert len(self._weightedElements)  !=0
        self._crystalLog = collections.defaultdict(lambda : 0)
        
    def getNextItemOrCrystalConstructor(self, source=None):
            node =self._getRandomforWeightedList(self._weightedItems)
            self._crystalLog[node.itemType] +=1
            if node.color == None:
                color = None
            else:
                color = self._getRandomColor(True)
            return color, node
        
    def getNextStructureElement(self, source=None):
        node = self._getRandomWeightedStructureElementOrItem()   
        if node.color == None:
            color = None
        else:
            color = self._getRandomColor(False)
        return color, node
    
    def _makeWeightedList(self, weights, classes):
        result = []
        for key in weights:
            if key in classes:
                result.append((weights[key], classes[key]))
        return result
                  
    def _getRandomforWeightedList(self, weightedlist):
        return random.choice(list(itertools.chain(*[itertools.repeat(element, weight) for weight, element in weightedlist])))
    
    def _getRandomWeightedStructureElementOrItem(self):
        element = self._getRandomforWeightedList(self._weightedElements)
        return element   
    
    def _getRandomColor(self, weighted=False):
        
        if weighted:
            colorDistribution = self._getColorDistribution()
            rand = random.uniform(0,1)
            
            intervall = 0
            for color, value in colorDistribution.items():
                intervall += value
                if intervall >= rand:
                    return color
        
        return random.choice(gameElements.availableColors[:self._numberOfColors])

    def _getColorDistribution(self):
        overallCount = collections.Counter()
        for structure in self._structures:
            overallCount += structure.getColorCount()
        del overallCount[None]
        #normalize
        overallSum = sum(overallCount.values())
        return {key:(value/overallSum) for key,value in overallCount.items()}

    def registerStructure(self, structure):
        self._structures.append(structure)
        
    def removeStructure(self, structure):
        self._structures.remove(structure)
