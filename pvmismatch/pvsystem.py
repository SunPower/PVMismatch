# -*- coding: utf-8 -*-
"""
Created on Jul 16, 2012

@author: mmikofski
"""

import numpy as np
from pvconstants import PVconstants, npinterpx
from pvmodule import PTS, NPTS
from pvstring import PVstring
from matplotlib import pyplot as plt

_numberStrs = 10  # default number of strings


class PVsystem(object):
    """
    PVsystem - A class for PV systems.
    """

    def __init__(self, pvconst=PVconstants(), numberStrs=_numberStrs,
                 pvstrs=None):
        """
        Constructor
        """
        self.pvconst = pvconst
        self.numberStrs = numberStrs
        if pvstrs is None:
            self.pvstrs = [PVstring(pvconst=self.pvconst)] * self.numberStrs
        elif (type(pvstrs) is list) & (len(pvstrs) == self.numberStrs):
            self.pvstrs = pvstrs
        else:
            raise Exception("Invalid strings list!")
        (self.Istring, self.Vstring, self.Pstring) = self.calcString()

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        Istring = self.pvconst.Isc0 * PTS
        Vstring = np.zeros((NPTS, 1))
        for mod in range(self.numberStrs):
            xp = self.pvstrs[mod].Imod.reshape(NPTS)
            fp = self.pvstrs[mod].Vmod.reshape(NPTS)
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
