# -*- coding: utf-8 -*-
"""
Created on Thu Dec 05 14:03:40 2013

@author: mmikofski
"""

from pvmismatch.pvconstants import MODSIZES, SUBSTRSIZES
from pvmismatch.pvmodule import PVmodule

def test_pvmodule_subStrCells():
    return PVmodule(numberCells=MODSIZES[0], subStrCells=SUBSTRSIZES[0], Ee=7)

if __name__ == '__main__':
    pvmod = test_pvmodule_subStrCells()