# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

from copy import deepcopy
from matplotlib import pyplot as plt
from pvmismatch.pvconstants import PVconstants, npinterpx, NUMBERMODS, \
    NUMBERCELLS
from pvmismatch.pvmodule import PVmodule
import numpy as np


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, pvconst=PVconstants(), numberMods=NUMBERMODS,
                 pvmods=None, numberCells=NUMBERCELLS, Ee=1):
        """
        Constructor
        """
        self.pvconst = pvconst
        self.numberMods = numberMods
        self.numberCells = numberCells
        if pvmods is None:
            # use deep copy instead of making each object in a for-loop
            self.pvmods = ([PVmodule(self.pvconst, self.numberCells, Ee)] *
                           self.numberMods)
            self.pvmods[1:] = [deepcopy(pvmod) for pvmod in self.pvmods[1:]]
        elif ((type(pvmods) is list) and
              all([(type(pvmod) is PVmodule) for pvmod in pvmods])):
            pvmodsNumCells = [pvmod.numberCells == pvmods[0].numberCells
                              for pvmod in pvmods]
            if all(pvmodsNumCells):
                self.numberMods = len(pvmods)
                self.pvmods = pvmods
                self.numberCells = pvmods[0].numberCells
            else:
                errString = 'All modules must have the same number of cells.'
                raise Exception(errString)
        else:
            raise Exception("Invalid modules list!")
        (self.Istring, self.Vstring, self.Pstring) = self.calcString()

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        IatVrbd = [[np.interp(self.pvconst.VRBD, Vcell, Icell) for
                    (Vcell, Icell) in zip(pvmod.Vcell.T, pvmod.Icell.T)] for
                   pvmod in self.pvmods]
        Imax = np.max(IatVrbd) * self.pvconst.pts  # max current
        Ineg = (np.min([pvmod.Icell for pvmod in self.pvmods]) *
                self.pvconst.negpts)  # min current
        Istring = np.concatenate((Ineg, Imax), axis=0)
        Vstring = np.zeros((2 * self.pvconst.npts, 1))
        for mod in self.pvmods:
            xp = mod.Imod.squeeze()  # IGNORE:E1103
            fp = mod.Vmod.squeeze()  # IGNORE:E1103
            Vstring += npinterpx(Istring, xp, fp)
        Pstring = Istring * Vstring
        return (Istring, Vstring, Pstring)

    def plotStr(self):
        """
        Plot string I-V curves.
        Returns strPlot : matplotlib.pyplot figure
        """
        strPlot = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.Vstring, self.Istring)
        plt.title('String I-V Characteristics')
        plt.ylabel('String Current, I [A]')
        plt.ylim(ymax=self.pvconst.Isc0 + 1)
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vstring, self.Pstring)
        plt.title('String P-V Characteristics')
        plt.xlabel('String Voltage, V [V]')
        plt.ylabel('String Power, P [W]')
        plt.grid()
        return strPlot
