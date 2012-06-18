# -*- coding: utf-8 -*-
"""
Created on Thu Jun 07 09:44:08 2012

@author: mmikofski
)
"""

from pvmismatch.pvmodule import PVmodule


def test():
    pvmod = PVmodule()
    pvmod.setSuns(0.5, 0)
    return pvmod


if __name__ == "__main__":
    test()
    