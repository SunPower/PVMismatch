# -*- coding: utf-8 -*-
"""
Created on Thu May 31 23:17:04 2012

@author: mmikofski
"""

import numpy
from pvconstants import PVconstants
from matplotlib import pyplot

RESOLUTION = 0.01
NUMBERCELLS = [72, 96, 128]
_numberCells = 96


class PVmodule(object):
    """
    PVmodule - A Class for PV modules
    """

    def __init__(self, pvconst=PVconstants(), numberCells=_numberCells, Ee=1):
        """
        Constructor
        """
        self.pvconst = pvconst
        self.numberCells = numberCells
        if numberCells not in NUMBERCELLS:
            #todo raise an exception
            print "Invalid number of cells."
        if numpy.isscalar(Ee):
            Ee = numpy.ones((self.numberCells, 1)) * Ee
        elif numpy.size(Ee, 0) != self.numberCells:
            #todo raise an exception
            print "Invalid number of cells."
        self.Ee = Ee
        self.Voc = self.calcVoc()

    def calcVoc(self):
        """
        Estimate open circuit voltage of cells
        """
        C = self.pvconst.Aph * self.pvconst.Isc0 * self.Ee
        C += self.pvconst.Isat1 + self.pvconst.Isat2
        VT = self.pvconst.k * self.pvconst.T / self.pvconst.q
        delta = self.pvconst.Isat2 ** 2 + 4 * self.pvconst.Isat1 * C
        Voc = VT * numpy.log(((-self.pvconst.Isat2 + numpy.sqrt(delta))
                   / 2 / self.pvconst.Isat1) ** 2)
        return Voc

    def calcCell(self):
        """
        Calculate cell I-V curves
        """
        tmpRange = numpy.arange(0, 1, RESOLUTION)
        Vdiode = Voc * tmpRange
        Igen = self.pvconst.Aph * self.pvconst.Isc0 * self.Ee
        Idiode1 = self.pvconst.Isat1 * (numpy.exp(self.pvconst.q * Vdiode
                  / self.pvconst.k / self.pvconst.T) - 1)
        Idiode2 = self.pvconst.Isat2 * (numpy.exp(self.pvconst.q * Vdiode
                  / 2 / self.pvconst.k / self.pvconst.T) - 1)
        Ishunt = Vdiode / self.pvconst.Rsh
        self.Icell = Igen - Idiode1 - Idiode2 - Ishunt
        self.Vcell = Vdiode - self.Icell * self.pvconst.Rs

    def plotCell(self):
        pyplot.plot(self.Vcell, self.Icell
