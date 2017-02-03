# -*- coding: utf-8 -*-
"""
This module contains the :class:`~pvmismatch.pvmismatch_lib.pvsystem.PVsystem`
class.
"""

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
    def __init__(self, pvconst=PVconstants(), numberStrs=NUMBERSTRS,
                 pvstrs=None, numberMods=NUMBERMODS, pvmods=None):
        self.pvconst = pvconst
        self.numberStrs = numberStrs
        self.numberMods = numberMods
        if pvstrs is None:
            pvstrs = PVstring(numberMods=self.numberMods, pvmods=pvmods,
                              pvconst=self.pvconst)
        # use deep copy instead of making each object in a for-loop
        if isinstance(pvstrs, PVstring):
            pvstrs = [pvstrs] * self.numberStrs
        if len(pvstrs) != self.numberStrs:
            # TODO: use pvmismatch excecptions
            raise Exception("Number of strings don't match.")
        self.pvstrs = pvstrs
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
        Pmp = self.Psys[mpp]
        Vmp = self.Vsys[mpp]
        Imp = self.Isys[mpp]
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
            for pvstr, pvmod_Ee in Ee.iteritems():
                pvstr = int(pvstr)
                self.pvstrs[pvstr] = copy(self.pvstrs[pvstr])
                self.pvstrs[pvstr].setSuns(pvmod_Ee)
        self.Isys, self.Vsys, self.Psys = self.calcSystem()
        (self.Imp, self.Vmp, self.Pmp,
         self.Isc, self.Voc, self.FF, self.eff) = self.calcMPP_IscVocFFeff()

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
            for pvstr, pvmod_Tc in Tc.iteritems():
                pvstr = int(pvstr)
                self.pvstrs[pvstr] = copy(self.pvstrs[pvstr])
                self.pvstrs[pvstr].setTemps(pvmod_Tc)
        self.Isys, self.Vsys, self.Psys = self.calcSystem()
        (self.Imp, self.Vmp, self.Pmp,
         self.Isc, self.Voc, self.FF, self.eff) = self.calcMPP_IscVocFFeff()

    def plotSys(self, sysPlot=None):
        """
        Plot system I-V curves.
        Arguments sysPlot : matplotlib.figure.Figure
        Returns sysPlot : matplotlib.figure.Figure
        """
        # create new figure if sysPlot is None
        # or make the specified sysPlot current and clear it
        if not sysPlot:
            sysPlot = plt.figure()
        elif isinstance(sysPlot, (int, basestring)):
            sysPlot = plt.figure(sysPlot)
        else:
            try:
                sysPlot = plt.figure(sysPlot.number)
            except TypeError as e:
                print '%s is not a figure.' % sysPlot
                print 'Sorry, "plotSys" takes a "int", "str" or "Figure".'
                raise e
        sysPlot.clear()
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
