# -*- coding: utf-8 -*-
"""
This module contains the :class:`~pvmismatch.pvmismatch_lib.pvstring.PVstring`
class.
"""

from __future__ import absolute_import
from past.builtins import range
from future.utils import iteritems
import numpy as np
from copy import copy
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
                 pvconst=None):
        # is pvmods a list?
        try:
            pvmod0 = pvmods[0]
        except TypeError:
            # is pvmods an object?
            try:
                pvconst = pvmods.pvconst
            except AttributeError:
                #  try to use the pvconst arg or create one if none
                if not pvconst:
                    pvconst = PVconstants()
                # create pvmod
                pvmods = PVmodule(pvconst=pvconst)
            # expand pvmods to list
            pvmods = [pvmods] * numberMods
        else:
            pvconst = pvmod0.pvconst
            numberMods = len(pvmods)
            for p in pvmods:
                if p.pvconst is not pvconst:
                    raise Exception('pvconst must be the same for all modules')
        self.pvconst = pvconst  #: ``PVconstants`` used in  ``PVstring``
        self.numberMods = numberMods  #: number of module in string
        self.pvmods = pvmods  #: list of ``PVModule`` in ``PVstring``
        # calculate string
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

        :param Ee: irradiance [suns]
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
            new_pvmods = range(self.numberMods)  # new list of modules
            old_pvmods = dict.fromkeys(self.pvmods)  # same as set(pvmods)
            for mod_id, pvmod in enumerate(self.pvmods):
                if old_pvmods[pvmod] is None:
                    new_pvmods[mod_id] = copy(pvmod)
                    old_pvmods[pvmod] = new_pvmods[mod_id]
                else:
                    new_pvmods[mod_id] = old_pvmods[pvmod]
            self.pvmods = new_pvmods
            for pvmod in iter(self.pvmods):
                pvmod.setSuns(Ee)
        else:
            self.pvmods = copy(self.pvmods)  # copy list first
            try:
                for pvmod, cell_Ee in iteritems(Ee):
                    pvmod = int(pvmod)
                    self.pvmods[pvmod] = copy(self.pvmods[pvmod])
                    if hasattr(cell_Ee, 'keys'):
                        self.pvmods[pvmod].setSuns(**cell_Ee)
                    else:
                        try:
                            self.pvmods[pvmod].setSuns(*cell_Ee)
                        except TypeError:
                            self.pvmods[pvmod].setSuns(cell_Ee)
            except AttributeError:
                # Ee was a list? just take first item in list
                if len(Ee) > 1:
                    raise TypeError('Irradiance, Ee, should be scalar or dict')
                Ee = Ee[0]
                new_pvmods = range(self.numberMods)  # new list of modules
                old_pvmods = dict.fromkeys(self.pvmods)  # same as set(pvmods)
                for mod_id, pvmod in enumerate(self.pvmods):
                    if old_pvmods[pvmod] is None:
                        new_pvmods[mod_id] = copy(pvmod)
                        old_pvmods[pvmod] = new_pvmods[mod_id]
                    else:
                        new_pvmods[mod_id] = old_pvmods[pvmod]
                self.pvmods = new_pvmods
                for pvmod in iter(self.pvmods):
                    pvmod.setSuns(Ee)
        # update modules
        self.Istring, self.Vstring, self.Pstring = self.calcString()

    def setTemps(self, Tc):
        """
        Set temperature on cells in modules of string in system.
        If Tc is ...
        ... scalar, then sets the entire string to that temperature.
        ... a dictionary, then each key refers to a module in the string,
        and the corresponding value are passed to
        :meth:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule.setTemps()`

        :param Tc: temperature [K]
        :type Tc: dict or float

        For Example::

            Tc={0: {'cells': (1,2,3), 'Tc': (323.15, 348.15, 373.15)}}  # set module 0
            Tc=323.15  # set all modules to 323.15K (50°C)
            Tc={12: 348.15}  # set module with index 12 to 348.15K (75°C)

        """
        if np.isscalar(Tc):
            new_pvmods = range(self.numberMods)  # new list of modules
            old_pvmods = dict.fromkeys(self.pvmods)  # same as set(pvmods)
            for mod_id, pvmod in enumerate(self.pvmods):
                if old_pvmods[pvmod] is None:
                    new_pvmods[mod_id] = copy(pvmod)
                    old_pvmods[pvmod] = new_pvmods[mod_id]
                else:
                    new_pvmods[mod_id] = old_pvmods[pvmod]
            self.pvmods = new_pvmods
            for pvmod in iter(self.pvmods):
                pvmod.setTemps(Tc)
        else:
            self.pvmods = copy(self.pvmods)  # copy list first
            try:
                for pvmod, cell_Tc in iteritems(Tc):
                    pvmod = int(pvmod)
                    self.pvmods[pvmod] = copy(self.pvmods[pvmod])
                    if hasattr(cell_Tc, 'keys'):
                        self.pvmods[pvmod].setTemps(**cell_Tc)
                    else:
                        try:
                            self.pvmods[pvmod].setTemps(*cell_Tc)
                        except TypeError:
                            self.pvmods[pvmod].setTemps(cell_Tc)
            except AttributeError:
                # Tc was a list? just take first item in list
                if len(Tc) > 1:
                    raise TypeError('Irradiance, Ee, should be scalar or dict')
                Tc = Tc[0]
                new_pvmods = range(self.numberMods)  # new list of modules
                old_pvmods = dict.fromkeys(self.pvmods)  # same as set(pvmods)
                for mod_id, pvmod in enumerate(self.pvmods):
                    if old_pvmods[pvmod] is None:
                        new_pvmods[mod_id] = copy(pvmod)
                        old_pvmods[pvmod] = new_pvmods[mod_id]
                    else:
                        new_pvmods[mod_id] = old_pvmods[pvmod]
                self.pvmods = new_pvmods
                for pvmod in iter(self.pvmods):
                    pvmod.setTemps(Tc)
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
