# -*- coding: utf-8 -*-
"""
Created on Thu Jun 07 09:44:08 2012

@author: mmikofski
)
"""

#from pvmismatch.pvmodule import PVmodule
#from pvmismatch.pvstring import PVstring
from pvmismatch.pvsystem import PVsystem


def test():
    pvsys = PVsystem()
    return pvsys


if __name__ == "__main__":
    pvsys = test()
    pvsys.plotSys().show()
    pvsys.pvstrs[0].pvmods[0].setSuns(0.5, 0)
    pvsys.plotSys().show()
    pass
