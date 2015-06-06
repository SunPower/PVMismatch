# -*- coding: utf-8 -*-
"""
Created on Thu Dec 05 14:03:40 2013

@author: mmikofski
"""

from pvmismatch.pvmismatch_lib.pvconstants import MODSIZES, SUBSTRSIZES
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule

def test_pvmodule_subStrCells():
    return PVmodule(numberCells=MODSIZES[0], subStrCells=SUBSTRSIZES[0], Ee=7)

if __name__ == '__main__':
    pvmod = test_pvmodule_subStrCells()