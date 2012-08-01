# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

import numpy as np
from pvmismatch.pvconstants import PVconstants, npinterpx
from pvmismatch.pvmodule import PVmodule, PTS, NPTS
from matplotlib import pyplot as plt

_numberMods = 10  # default number of modules


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, pvconst=PVconstants(), numberMods=_numberMods,
                 pvmods=None):
        """
        Constructor
        """
        # TODO: use pvmods to determine numberMods OR input arg
        # http://www.logilab.org/card/pylintfeatures#miscellaneous-checker
        # pylint: disable = W0511
        self.pvconst = pvconst
        self.numberMods = numberMods
        if pvmods is None:
            self.pvmods = [PVmodule(pvconst=self.pvconst)
                           for pvmod in range(self.numberMods)]
        elif ((type(pvmods) is list) and
              all([(type(pvmod) is PVmodule) for pvmod in pvmods])):
            self.numberMods = len(pvmods)
            self.pvmods = pvmods
            # Don't use `itertools.repeat(e, n)` or `[e]  * n` because copies
            # all point to the same object.
        elif (type(pvmods) is list) and (len(pvmods) == self.numberMods):
            self.pvmods = pvmods
        else:
            raise Exception("Invalid modules list!")
        (self.Istring, self.Vstring, self.Pstring) = self.calcString()

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        Istring = self.pvconst.Isc0 * PTS
        Vstring = np.zeros((NPTS, 1))
        for mod in self.pvmods:
            xp = mod.Imod.reshape(NPTS)
            fp = mod.Vmod.reshape(NPTS)
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
