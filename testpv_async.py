#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Aug 30, 2012

@author: marko
"""

from pvmismatch.pvsystem import PVsystem
import numpy as np

if __name__ == '__main__':
    pvsys = PVsystem()
    pvsys2 = PVsystem()
    pvsys2.pvmods[0][0].setSuns(np.random.random(12), np.arange(12))
    pvsys2.pvmods[0][1].setSuns(np.random.random(24), np.arange(24))
    pvsys2.pvmods[2][0].setSuns(np.random.random(36), np.arange(36))
    pvsys2.calcSystem()
