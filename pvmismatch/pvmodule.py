# -*- coding: utf-8 -*-
"""
Created on Thu May 31 23:17:04 2012

@author: mmikofski
"""

import numpy as np
from pvconstants import PVconstants
from matplotlib import pyplot as plt

NPTS = 1001  # numper of I-V points to calculate
PTS = np.linspace(0, 1, NPTS).reshape(NPTS, 1)  # pylint: disable=E1103
NUMBERCELLS = [72, 96, 128]  # list of possible number of cells per module
_numberCells = 96  # default number of cells


class PVmodule(object):
    """
    PVmodule - A Class for PV modules.
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
        if np.isscalar(Ee):
            Ee = np.ones((1, self.numberCells)) * Ee
        elif np.size(Ee, 1) != self.numberCells:
            #todo raise an exception
            print "Invalid number of cells."
        self.Ee = Ee
        self.Voc = self.calcVoc()
        (self.Icell, self.Vcell, self.Pcell) = self.calcCell()
        (self.Imod, self.Vmod, self.Pmod) = self.calcMod()

    def calcVoc(self):
        """
        Estimate open circuit voltage of cells.
        Returns Voc : numpy.ndarray of float, estimated open circuit voltage
        """
        C = self.pvconst.Aph * self.pvconst.Isc0 * self.Ee
        C += self.pvconst.Isat1 + self.pvconst.Isat2
        VT = self.pvconst.k * self.pvconst.T / self.pvconst.q
        delta = self.pvconst.Isat2 ** 2 + 4 * self.pvconst.Isat1 * C
        Voc = VT * np.log(((-self.pvconst.Isat2 + np.sqrt(delta))
                   / 2 / self.pvconst.Isat1) ** 2)
        return Voc

    def calcCell(self):
        """
        Calculate cell I-V curves.
        Returns (Icell, Vcell, Pcell) : tuple of numpy.ndarray of float
        """
        Vdiode = self.Voc * PTS
        Igen = self.pvconst.Aph * self.pvconst.Isc0 * self.Ee
        Idiode1 = self.pvconst.Isat1 * (np.exp(self.pvconst.q * Vdiode
                  / self.pvconst.k / self.pvconst.T) - 1)
        Idiode2 = self.pvconst.Isat2 * (np.exp(self.pvconst.q * Vdiode
                  / 2 / self.pvconst.k / self.pvconst.T) - 1)
        Ishunt = Vdiode / self.pvconst.Rsh
        Icell = Igen - Idiode1 - Idiode2 - Ishunt
        Vcell = Vdiode - Icell * self.pvconst.Rs
        Pcell = Icell * Vcell
        return (Icell, Vcell, Pcell)

    def calcMod(self):
        """
        Calculate module I-V curves.
        Returns (Imod, Vmod, Pmod) : tuple of numpy.ndarray of float
        """
        Imod = self.pvconst.Isc0 * PTS
        Vmod = np.zeros((NPTS, 1))
        for cell in range(self.numberCells):
            xp = np.flipud(self.Icell[:, cell])
            fp = np.flipud(self.Vcell[:, cell])
            Vmod += np.interp(Imod, xp, fp)
        Pmod = Imod * Vmod
        return (Imod, Vmod, Pmod)

    def plotCell(self):
        """
        Plot cell I-V curves.
        Returns cellPlot : matplotlib.pyplot figure
        """
        cellPlot = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.Vcell, self.Icell)
        plt.title('Cell I-V Characteristics')
        plt.xlabel('Cell Voltage, V [V]')
        plt.ylabel('Cell Current, I [A]')
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vcell, self.Pcell)
        plt.title('Cell P-V Characteristics')
        plt.ylabel('Cell Power, P [W]')
        plt.grid()
        return cellPlot

    def plotMod(self):
        """
        Plot module I-V curves.
        Returns modPlot : matplotlib.pyplot figure
        """
        modPlot = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.Vmod, self.Imod)
        plt.title('Module I-V Characteristics')
        plt.xlabel('Module Voltage, V [V]')
        plt.ylabel('Module Current, I [A]')
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vmod, self.Pmod)
        plt.title('Module P-V Characteristics')
        plt.ylabel('Module Power, P [W]')
        plt.grid()
        return modPlot