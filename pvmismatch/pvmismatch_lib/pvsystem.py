# -*- coding: utf-8 -*-
"""
Created on Jul 16, 2012

@author: mmikofski
"""

import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, NUMBERMODS, \
    NUMBERSTRS
from pvmismatch.pvmismatch_lib.pvstring import PVstring
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule
from pvmismatch.pvmismatch_lib.parallel_calcs import parallel_calcSystem


class PVsystem(object):
    """
    A class for PV systems.
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
            pvstrs = [deepcopy(pvstrs) for _ in self.numberStrs]
        if len(pvstrs) != self.numberStrs:
            # TODO: use pvmismatch excecptions
            raise Exception("Number of strings don't match.")
        self.pvstrs = pvstrs
        (self.Isys, self.Vsys, self.Psys) = self.calcSystem()
        (self.Imp, self.Vmp, self.Pmp,
         self.Isc, self.Voc, self.FF, self.eff) = self.calcMPP_IscVocFFeff()

    @property
    def pvmods(self):
        return  [pvstr.pvmods for pvstr in self.pvstrs]

    @property
    def Istring(self):
        return [pvstr.Istring.flatten() for pvstr in self.pvstrs]

    @property
    def Vstring(self):
        return [pvstr.Vstring.flatten() for pvstr in self.pvstrs]

    def calcSystem(self):
        """
        Calculate system I-V curves.
        Returns (Isys, Vsys, Psys) : tuple of numpy.ndarray of float
        """
        Isys = np.zeros((self.pvconst.npts, 1))
        Vmax = np.max([pvstr.Vstring for pvstr in self.pvstrs])
        Vsys = Vmax * self.pvconst.pts

        Isys, Vsys = self.pvconst.calcParallel(self.Istring, self.Vstring)
        Psys = Isys * Vsys
        return (Isys, Vsys, Psys)

    def calcMPP_IscVocFFeff(self):
        mpp = np.argmax(self.Psys)
        Pmp = self.Psys[mpp,0]
        Vmp = self.Vsys[mpp,0]
        Imp = self.Isys[mpp,0]
        # xp must be increasing
        Isys = self.Isys.reshape(self.pvconst.npts)  # IGNORE:E1103
        Vsys = self.Vsys.reshape(self.pvconst.npts)  # IGNORE:E1103
        xp = np.flipud(Isys)
        fp = np.flipud(Vsys)
        Voc = np.interp(0, xp, fp)  # calculate Voc
        xp = Vsys
        fp = Isys
        Isc = np.interp(0, xp, fp)
        FF = Pmp / Isc / Voc
        totalSuns = 0
        for pvstr in self.pvstrs:
            for pvmod in pvstr.pvmods:
                totalSuns += np.sum(pvmod.Ee)
        # convert cellArea from cm^2 to m^2
        Psun = self.pvconst.E0 * totalSuns * self.pvconst.cellArea / 100 / 100
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
        :meth:`~pvmodules.PVmodules.setSuns()`

        Example::
        Ee={0: {0: {'cells': (0, 1, 2), 'Ee': (0.9, 0.3, 0.5)}}}
        Ee=0.91  # set all modules in all strings to 0.91 suns
        Ee={12: 0.77}  # set all modules in string with index 12 to 0.77 suns
        Ee={3: {8: 0.23, 7: 0.45}}  # set module with index 8 to 0.23 suns and
            module with index 7 to 0.45 suns in string with index 3

        :param Ee: irradiance [W/m^2]
        :type Ee: dict or float
        """
        if np.isscalar(Ee):
            for pvstr in self.pvstrs:
                pvstr.setSuns(Ee)
        else:
            for pvstr, pvmod_Ee in Ee.iteritems():
                self.pvstrs[pvstr].setSuns(pvmod_Ee)
        (self.Isys, self.Vsys, self.Psys) = self.calcSystem()
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
        elif type(sysPlot) in [int, str]:
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
