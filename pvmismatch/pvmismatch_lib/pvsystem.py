# -*- coding: utf-8 -*-
"""
This module contains the :class:`~pvmismatch.pvmismatch_lib.pvsystem.PVsystem`
class.
"""

from __future__ import absolute_import
from past.builtins import basestring
from future.utils import iteritems
import numpy as np
from copy import copy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, NUMBERMODS, \
    NUMBERSTRS
from pvmismatch.pvmismatch_lib.pvstring import PVstring


class PVsystem(object):
    """
    A class for PV systems.

    :param pvconst: configuration constants object
    :type pvconst: :class:`~pvmismatch.pvmismatch_lib.pvconstants.PVconstants`
    :param numberStrs: number of strings
    :param pvstrs: list of parallel strings, a ``PVstring`` object or None
    :param numberMods: number of modules per string
    :param pvmods: list of modules, a ``PVmodule`` object or None
    """
    def __init__(self, pvconst=None, numberStrs=NUMBERSTRS,
                 pvstrs=None, numberMods=NUMBERMODS, pvmods=None):
        # is pvstrs a list?
        try:
            pvstr0 = pvstrs[0]
        except TypeError:
            # is pvstrs a PVstring object?
            try:
                pvconst = pvstrs.pvconst
            except AttributeError:
                # try to use the pvconst arg or create one if none
                if not pvconst:
                    pvconst = PVconstants()
                # create a pvstring
                pvstrs = PVstring(numberMods=numberMods, pvmods=pvmods,
                                  pvconst=pvconst)
            # expand pvstrs to list
            pvstrs = [pvstrs] * numberStrs
            numberMods = [numberMods] * numberStrs
        else:
            pvconst = pvstr0.pvconst
            numberStrs = len(pvstrs)
            numberMods = []
            for p in pvstrs:
                if p.pvconst is not pvconst:
                    raise Exception('pvconst must be the same for all strings')
                numberMods.append(len(p.pvmods))
        self.pvconst = pvconst  #: ``PVconstants`` used in ``PVsystem``
        self.numberStrs = numberStrs  #: number strings in the system
        self.numberMods = numberMods  #: list of number of modules per string
        self.pvstrs = pvstrs  #: list of ``PVstring`` in system
        # calculate pvsystem
        self.update()

    def update(self):
        """Update system calculations."""
        self.Isys, self.Vsys, self.Psys = self.calcSystem()
        (self.Imp, self.Vmp, self.Pmp,
         self.Isc, self.Voc, self.FF, self.eff) = self.calcMPP_IscVocFFeff()

    # TODO: use __getattr__ to check for updates to pvcells

    @property
    def pvmods(self):
        return [pvstr.pvmods for pvstr in self.pvstrs]

    @property
    def Istring(self):
        return np.asarray([pvstr.Istring.flatten() for pvstr in self.pvstrs])

    @property
    def Vstring(self):
        return np.asarray([pvstr.Vstring.flatten() for pvstr in self.pvstrs])

    def calcSystem(self):
        """
        Calculate system I-V curves.
        Returns (Isys, Vsys, Psys) : tuple of numpy.ndarray of float
        """
        Isys, Vsys = self.pvconst.calcParallel(
            self.Istring, self.Vstring, self.Vstring.max(), self.Vstring.min()
        )
        Psys = Isys * Vsys
        return Isys, Vsys, Psys

    def calcMPP_IscVocFFeff(self):
        mpp = np.argmax(self.Psys)
        P = self.Psys[mpp - 1:mpp + 2]
        V = self.Vsys[mpp - 1:mpp + 2]
        I = self.Isys[mpp - 1:mpp + 2]
        # calculate derivative dP/dV using central difference
        dP = np.diff(P, axis=0)  # size is (2, 1)
        dV = np.diff(V, axis=0)  # size is (2, 1)
        Pv = dP / dV  # size is (2, 1)
        # dP/dV is central difference at midpoints,
        Vmid = (V[1:] + V[:-1]) / 2.0  # size is (2, 1)
        Imid = (I[1:] + I[:-1]) / 2.0  # size is (2, 1)
        # interpolate to find Vmp
        Vmp = (-Pv[0] * np.diff(Vmid, axis=0) / np.diff(Pv, axis=0) + Vmid[0]).item()
        Imp = (-Pv[0] * np.diff(Imid, axis=0) / np.diff(Pv, axis=0) + Imid[0]).item()
        # calculate max power at Pv = 0
        Pmp = Imp * Vmp
        # calculate Voc, current must be increasing so flipup()
        Voc = np.interp(np.float64(0), np.flipud(self.Isys),
                        np.flipud(self.Vsys))
        Isc = np.interp(np.float64(0), self.Vsys, self.Isys)  # calculate Isc
        FF = Pmp / Isc / Voc
        totalSuns = sum(
            [pvmod.Ee.sum() * pvmod.cellArea for pvstr in self.pvmods
             for pvmod in pvstr]
        )
        # convert cellArea from cm^2 to m^2
        Psun = self.pvconst.E0 * totalSuns / 100 / 100
        eff = Pmp / Psun
        return Imp, Vmp, Pmp, Isc, Voc, FF, eff

    def setSuns(self, Ee):
        """
        Set irradiance on cells in modules of string in system.
        If Ee is ...
        ... scalar, then sets the entire system to that irradiance.
        ... a dictionary, then each key refers to a pv-string in the system,
        and the corresponding value is either a dictionary or a scalar.
        If the dictionary's value is another dictionary, then its keys are pv-
        modules and its values are either cells and corresponding Ee, cells and
        a scalar Ee, a scalar Ee value for all cells or an array of Ee values
        for all cells in the module. The values of pv-modules are passed to
        :meth:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule.setSuns()`

        :param Ee: irradiance [suns]
        :type Ee: dict, float

        For Example::

            Ee={0: {0: {'cells': (0, 1, 2), 'Ee': (0.9, 0.3, 0.5)}}}
            Ee=0.91  # set all modules in all strings to 0.91 suns
            Ee={12: 0.77}  # set all modules in string with index 12 to 0.77 suns
            Ee={3: {8: 0.23, 7: 0.45}}
            # set module with index 8 to 0.23 suns and module with index 7 to
            # 0.45 suns in string with index 3

        """
        if np.isscalar(Ee):
            for pvstr in self.pvstrs:
                pvstr.setSuns(Ee)
        else:
            for pvstr, pvmod_Ee in iteritems(Ee):
                pvstr = int(pvstr)
                self.pvstrs[pvstr] = copy(self.pvstrs[pvstr])
                self.pvstrs[pvstr].setSuns(pvmod_Ee)
        # calculate pvsystem
        self.update()

    def setTemps(self, Tc):
        """
        Set temperature on cells in modules of string in system.
        If Tc is ...
        ... scalar, then sets the entire system to that cell temperature.
        ... a dictionary, then each key refers to a pv-string in the system,
        and the corresponding value is either a dictionary or a scalar.
        If the dictionary's value is another dictionary, then its keys are pv-
        modules and its values are either cells and corresponding Tc, cells and
        a scalar Tc, a scalar Tc value for all cells or an array of Tc values
        for all cells in the module. The values of pv-modules are passed to
        :meth:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule.setTemps()`

        :param Tc: temperature [K]
        :type Tc: dict, float

        For Example::

            Tc={0: {0: {'cells': (1,2,3), 'Tc': (323.15, 348.15, 373.15)}}}
            Tc=323.15  # set all modules in all strings to 323.15K (50°C)
            Tc={12: 348.15}  # set all modules in string with index 12 to 348.15K (75°C)
            Tc={3: {8: 333.15, 7: 373.15}}
            # set module with index 8 to 333.15K (60°C) and module with index 7 to
            # 373.15K (100°C) in string with index 3

        """
        if np.isscalar(Tc):
            for pvstr in self.pvstrs:
                pvstr.setTemps(Tc)
        else:
            for pvstr, pvmod_Tc in iteritems(Tc):
                pvstr = int(pvstr)
                self.pvstrs[pvstr] = copy(self.pvstrs[pvstr])
                self.pvstrs[pvstr].setTemps(pvmod_Tc)
        # calculate pvsystem
        self.update()

    def plotSys(self, sysPlot=None):
        """
        Plot system I-V curves.

        :param sysPlot: integer, string, or existing figure
        :returns: new figure
        """
        # create new figure if sysPlot or make the specified sysPlot current
        # and clear it
        try:
            sysPlot.clear()
        except (AttributeError, SyntaxError):
            sysPlot = plt.figure(sysPlot)
        plt.subplot(2, 1, 1)
        plt.plot(self.Vsys, self.Isys)
        plt.xlim(0, self.Voc * 1.1)
        plt.ylim(0, self.Isc * 1.1)
        plt.axvline(self.Vmp, color='r', linestyle=':')
        plt.axhline(self.Imp, color='r', linestyle=':')
        plt.title('System I-V Characteristics')
        plt.ylabel('System Current, I [A]')
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vsys, self.Psys / 1000)
        plt.xlim(0, self.Voc * 1.1)
        plt.ylim(0, self.Pmp * 1.1 / 1000)
        plt.axvline(self.Vmp, color='r', linestyle=':')
        plt.axhline(self.Pmp / 1000, color='r', linestyle=':')
        plt.title('System P-V Characteristics')
        plt.xlabel('System Voltage, V [V]')
        plt.ylabel('System Power, P [kW]')
        plt.grid()
        return sysPlot
