# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

import numpy as np
# from pvconstants import PVconstants
from pvmodule import PVmodule
# from matplotlib import pyplot as plt

NPTS = 1001  # numper of I-V points to calculate
(PTS,) = np.linspace(0, 1, NPTS)
PTS = PTS.reshape(NPTS, 1)
_numberMods = 10  # default number of modules


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, pvmods=None, numberMods=_numberMods):
        """
        Constructor
        """
        self.numberMods = numberMods
        if pvmods is None:
            self.pvmods = []  # empty list
            for pvmod in range(self.numberMods):
                self.pvmods.append = PVmodule()
        elif (type(pvmods) is list) & (len(pvmods) == self.numberMods):
            self.pvmods = pvmods
        else:
            # TODO raise exception
            print "Invalid modules list!"
        self.calcString()

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        # TODO use common pvconst?
        Istring = self.pvmods[0].pvconst.Isc0 * PTS
        Vstring = np.zeros((NPTS, 1))
        for mod in range(self.numberMods):
            xp = np.flipud(self.pvmods[mod].Imod)
            fp = np.flipud(self.pvmods[mod].Vmod)
            Vstring += np.interp(Istring, xp, fp)
        Pstring = Istring * Vstring
        return (Istring, Vstring, Pstring)