# -*- coding: utf-8 -*-
"""
This module contains the :class:`~pvmismatch.pvmismatch_lib.pvstring.PVstring`
class.
"""

import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, NUMBERMODS
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule


class PVstring(object):
    """
    A class for PV strings.

    :param numberMods: number of modules in string
    :param pvmods: either a list of modules, an instance of
        :class:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule` [Optional]
    :type pvmods: list, :class:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule`
    :param pvconst: a configuration constants object
    """
    def __init__(self, numberMods=NUMBERMODS, pvmods=None,
                 pvconst=PVconstants()):
        self.pvconst = pvconst
        self.numberMods = numberMods
        if pvmods is None:
            # use deepcopy instead of making each object in for-loop, 2x faster
            pvmods = PVmodule(pvconst=self.pvconst)
        if isinstance(pvmods, PVmodule):
            # GH35: don't make copies, use same reference for all objects
            #pvmods = [deepcopy(pvmods) for _ in xrange(self.numberMods)]
            pvmods = [pvmods] * self.numberMods
            # reset pvconsts in all pvcells and pvmodules
            for p in pvmods:
                for c in p.pvcells:
                    c.pvconst = self.pvconst
                p.pvconst = self.pvconst
        if len(pvmods) != self.numberMods:
            # TODO: use pvmismatch exceptions
            raise Exception("Number of modules doesn't match.")
        self.pvmods = pvmods
        self.Istring, self.Vstring, self.Pstring = self.calcString()

    # TODO: use __getattr__ to check for updates to pvcells

    @property
    def Imod(self):
        return np.array([mod.Imod.flatten() for mod in self.pvmods])

    @property
    def Vmod(self):
        return np.array([mod.Vmod.flatten() for mod in self.pvmods])

    def calcString(self):
        """
        Calculate string I-V curves.
        Returns (Istring, Vstring, Pstring) : tuple of numpy.ndarray of float
        """
        # Imod is already set to the range from Vrbd to the minimum current
        meanIsc = np.mean([pvmod.Isc.mean() for pvmod in self.pvmods])
        Istring, Vstring = self.pvconst.calcSeries(self.Imod, self.Vmod,
                                                   meanIsc, self.Imod.max())
        Pstring = Istring * Vstring
        return Istring, Vstring, Pstring

    def setSuns(self, Ee):
        """
        Set irradiance on cells in modules of string in system.
        If Ee is ...
        ... scalar, then sets the entire string to that irradiance.
        ... a dictionary, then each key refers to a module in the string,
        and the corresponding value are passed to
        :meth:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule.setSuns()`

        :param Ee: irradiance [W/m^2]
        :type Ee: dict or float

        For Example::

            Ee={0: {'cells': (1,2,3), 'Ee': (0.9, 0.3, 0.5)}}  # set module 0
            Ee=0.91  # set all modules to 0.91 suns
            Ee={12: 0.77}  # set module with index 12 to 0.77 suns
            Ee={8: [0.23, (0, 1, 2)], 7: [(0.45, 0.35), (71, 72)]}
            # set module 8, cells 0, 1 and 2 to 0.23 suns, then set module 7, cell
            #   71 to 0.45 suns and module 72 to 0.35 suns.

        """
        if np.isscalar(Ee):
            for pvmod in iter(self.pvmods):
                pvmod.setSuns(Ee)
        else:
            try:
                for pvmod, cell_Ee in Ee.iteritems():
                    if hasattr(cell_Ee, 'keys'):
                        self.pvmods[pvmod].setSuns(**cell_Ee)
                    else:
                        try:
                            self.pvmods[pvmod].setSuns(*cell_Ee)
                        except TypeError:
                            self.pvmods[pvmod].setSuns(cell_Ee)
            except AttributeError:
                Ee = Ee[0]
                for pvmod in iter(self.pvmods):
                    pvmod.setSuns(Ee)
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
        plt.ylim(ymin=0)
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vstring, self.Pstring)
        plt.title('String P-V Characteristics')
        plt.xlabel('String Voltage, V [V]')
        plt.ylabel('String Power, P [W]')
        plt.grid()
        return strPlot
