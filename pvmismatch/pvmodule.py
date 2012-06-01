# -*- coding: utf-8 -*-
"""
Created on Thu May 31 23:17:04 2012

@author: mmikofski
"""

import numpy
from pvconstants import PVconstants
from matplotlib import pyplot

NUMBERCELLS = [72, 96, 128]
_numberCells = 96


class PVmodule(object):
    """
    PVmodule - A Class for PV modules
    """

    def __init__(self, numberCells=_numberCells, pvconst=PVconstants()):
        self.numberCells = numberCells
        if numberCells not in NUMBERCELLS:
            #todo raise an exception
            print "Invalid number of cells."
        self.pvconst = pvconst

    def calcCell(self, Ee=1):
        Vdiode = numpy.array(range(61), 'float') / 100
        Igen = self.pvconst.Aph * self.pvconst.Isc0 * Ee
        Idiode1 = self.pvconst.Isat1 * (numpy.exp(self.pvconst.q * Vdiode
                  / self.pvconst.k / self.pvconst.T) - 1)
        Idiode2 = self.pvconst.Isat2 * (numpy.exp(self.pvconst.q * Vdiode
                  / 2 / self.pvconst.k / self.pvconst.T) - 1)
        Ishunt = Vdiode / self.pvconst.Rsh
        self.Icell = Igen - Idiode1 - Idiode2 - Ishunt
        self.Vcell = Vdiode - self.Icell * self.pvconst.Rs

    def plotCell(self):
        pyplot.plot(self.Vcell, self.Icell)