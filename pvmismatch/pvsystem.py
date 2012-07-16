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
        elif ((type(pvstrs) is list) and
              all([type(pvstr) is PVstring for pvstr in pvstrs])):
            self.numberStrs = len(pvstrs)
            self.pvstrs = pvstrs
        else:
            raise Exception("Invalid strings list!")
        (self.Isys, self.Vsys, self.Psys) = self.calcSystem()

    def calcSystem(self):
        """
        Calculate system I-V curves.
        Returns (Isys, Vsys, Psys) : tuple of numpy.ndarray of float
        """
        Isys = np.zeros((NPTS, 1))
        Vstring = np.array([pvstr.Vstring for pvstr in self.pvstrs]
                           ).reshape(NPTS, self.numberStrs
                                     )  # pylint: disable=E1103
        Vsys = np.max(Vstring, 1) * PTS
        for pvstr in range(self.numberStrs):
            fp = self.pvstrs[pvstr].Vstring.reshape(NPTS)
            xp = self.pvstrs[pvstr].Istring.reshape(NPTS)
            Isys += npinterpx(Vsys[pvstr].reshape(NPTS), xp, fp)
        Psys = Isys * Vsys
        return (Isys, Vsys, Psys)

    def plotSys(self):
        """
        Plot system I-V curves.
        Returns sysPlot : matplotlib.pyplot figure
        """
        sysPlot = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.Vsys, self.Isys)
        plt.title('System I-V Characteristics')
        plt.ylabel('System Current, I [A]')
        plt.ylim(ymax=self.pvconst.Isc0 + 1)
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vsys, self.Psys)
        plt.title('System P-V Characteristics')
        plt.xlabel('System Voltage, V [V]')
        plt.ylabel('System Power, P [W]')
        plt.grid()
        return sysPlot
