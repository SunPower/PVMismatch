# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, npinterpx, \
    NUMBERMODS, NUMBERCELLS
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, numberMods=NUMBERMODS, pvmods=None,
                 pvconst=PVconstants()):
        """
        Constructor
        """
        self.pvconst = pvconst
        self.numberMods = numberMods
        if pvmods is None:
            # use copy instead of making each object in a for-loop
            pvmod = PVmodule(pvconst=self.pvconst)
            pvmods = [deepcopy(pvmod) for _ in xrange(self.numberMods)]
        elif len(pvmods) != self.numberMods:
            # TODO: use pvmismatch exceptions
            raise Exception("Number of modules doesn't match.")
        self.numberMods = len(pvmods)
        self.pvmods = pvmods
        self.Istring, self.Vstring, self.Pstring = self.calcString()

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        # Imod is already set to the range from Vrbd to the minimum current
        zipped = zip(*[(pvmod.Imod[0], pvmod.Imod[-1], np.mean(pvmod.Ee)) for
                       pvmod in self.pvmods])
        Isc = np.mean(zipped[2]) * self.pvconst.Isc0
        # max current
        Imax = (np.max(zipped[1]) - Isc) * self.pvconst.Imod_pts + Isc
        # min current
        Ineg = (np.min(zipped[0]) - Isc) * self.pvconst.Imod_negpts + Isc
        Istring = np.concatenate((Ineg, Imax), axis=0)
        Vstring = np.zeros((2 * self.pvconst.npts, 1))
        for mod in self.pvmods:
            xp = mod.Imod.squeeze()  # IGNORE:E1103
            fp = mod.Vmod.squeeze()  # IGNORE:E1103
            Vstring += npinterpx(Istring, xp, fp)
        Pstring = Istring * Vstring
        return (Istring, Vstring, Pstring)

    def setSuns(self, Ee):
        """
        Set irradiance on cells in modules of string in system.
        If Ee is ...
        ... scalar, then sets the entire string to that irradiance.
        ... a dictionary, then each key refers to a module in the string,
        and the corresponding value are passed to
        :meth:`~pvmodules.PVmodules.setSuns()`

        Example::
        Ee={0: {'cells': (1,2,3), 'Ee': (0.9, 0.3, 0.5)}}  # set module 0
        Ee=0.91  # set all modules to 0.91 suns
        Ee={12: 0.77}  # set module with index 12 to 0.77 suns
        Ee={8: [0.23 (0, 1, 2)], 7: [(0.45, 0.35), (71, 72)]}

        :param Ee: irradiance [W/m^2]
        :type Ee: dict or float
        """
        if np.isscalar(Ee):
            for pvmod in self.pvmods:
                pvmod.setSuns(Ee)
        else:
            for pvmod, cell_Ee in Ee.iteritems():
                if hasattr(cell_Ee, 'keys'):
                    self.pvmods[pvmod].setSuns(**cell_Ee)
                else:
                    self.pvmods[pvmod].setSuns(*cell_Ee)
        # update modules
        self.Istring, self.Vstring, self.Pstring = self.calcString()

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
