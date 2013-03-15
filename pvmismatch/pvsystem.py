# -*- coding: utf-8 -*-
"""
Created on Jul 16, 2012

@author: mmikofski
"""

from copy import deepcopy
from matplotlib import pyplot as plt
from pvmismatch.pvconstants import PVconstants, npinterpx, NUMBERCELLS, \
    NUMBERMODS, NUMBERSTRS
from pvmismatch.pvstring import PVstring
import numpy as np


class PVsystem(object):
    """
    PVsystem - A class for PV systems.
    """

    def __init__(self, pvconst=PVconstants(), numberStrs=NUMBERSTRS,
                 pvstrs=None, numberMods=NUMBERMODS, pvmods=None,
                 numberCells=NUMBERCELLS, Ee=1):
        """
        Constructor
        """
        self.pvconst = pvconst
        self.numberStrs = numberStrs
        self.numberMods = numberMods
        self.numberCells = numberCells
        if pvstrs is None:
            if pvmods is None:
                # use deep copy instead of making each object in a for-loop
                pvstrs = PVstring(self.pvconst, self.numberMods,
                                  numberCells=self.numberCells, Ee=Ee)
            else:
                pvstrs = PVstring(self.pvconst, pvmods=pvmods)
            self.pvstrs = [pvstrs] * self.numberStrs
            self.pvstrs[1:] = [deepcopy(pvstr) for pvstr in self.pvstrs[1:]]
        elif ((type(pvstrs) is list) and
              all([(type(pvstr) is PVstring) for pvstr in pvstrs])):
            self.numberStrs = len(pvstrs)
            self.pvstrs = pvstrs
            # Make sure that all modules have the same number of cells.
            pvstrsNumCells = [pvstr.numberCells == pvstrs[0].numberCells
                              for pvstr in pvstrs]
            if all(pvstrsNumCells):
                self.numberCells = pvstrs[0].numberCells
            else:
                errString = 'All modules must have the same number of cells.'
                raise Exception(errString)
            # Make sure that all strings have the same number of modules.
            pvstrsNumMods = [pvstr.numberMods == pvstrs[0].numberMods
                             for pvstr in pvstrs]
            if all(pvstrsNumMods):
                self.numberMods = pvstrs[0].numberMods
            else:
                errString = 'All strings must have the same number of modules.'
                raise Exception(errString)
        else:
            raise Exception("Invalid strings list!")
        self.pvmods = [pvstr.pvmods for pvstr in self.pvstrs]
        (self.Isys, self.Vsys, self.Psys) = self.calcSystem()
        (self.Imp, self.Vmp, self.Pmp,
         self.Isc, self.Voc, self.FF, self.eff) = self.calcMPP_IscVocFFeff()

    def calcSystem(self):
        """
        Calculate system I-V curves.
        Returns (Isys, Vsys, Psys) : tuple of numpy.ndarray of float
        """
        Isys = np.zeros((self.pvconst.npts, 1))
        Vstring = np.array([pvstr.Vstring for pvstr in self.pvstrs])
        Vsys = np.max(Vstring) * self.pvconst.pts
        for pvstr in self.pvstrs:
            (pvstr.Istring, pvstr.Vstring, pvstr.Pstring) = pvstr.calcString()
            xp = np.flipud(pvstr.Vstring.squeeze())
            fp = np.flipud(pvstr.Istring.squeeze())
            Isys += npinterpx(Vsys, xp, fp)
        Psys = Isys * Vsys
        return (Isys, Vsys, Psys)

    def calcMPP_IscVocFFeff(self):
        Pmp = np.max(self.Psys)
        # np.interp only likes 1-D data & xp must be increasing
        # Psys is *not* monotonically increasing but its derivative *is*
        dP = np.diff(self.Psys, axis=0)  # (1000, 1)
        dV = np.diff(self.Vsys, axis=0)  # (1000, 1)
        Pv = dP / dV  # (1000, 1) decreasing
        # reshape(scalar) converts 2-D array to 1-D array (vector)
        Pv = np.flipud(Pv.reshape(self.pvconst.npts - 1))  # (1000,) increasing
        Vhalf = (self.Vsys[1:] + self.Vsys[:-1]) / 2  # (1000, 1) increasing
        Vhalf = np.flipud(Vhalf.reshape(self.pvconst.npts - 1))  # (1000,)
        Vmp = np.interp(0., Pv, Vhalf)  # estimate Vmp
        Imp = Pmp / Vmp  # calculate Imp
        xp = np.flipud(self.Isys.reshape(self.pvconst.npts))  # must be increasing
        fp = np.flipud(self.Vsys.reshape(self.pvconst.npts))  # keep data correspondence
        Voc = np.interp(0., xp, fp)  # calucalte Voc
        xp = self.Vsys.reshape(self.pvconst.npts)
        fp = self.Isys.reshape(self.pvconst.npts)
        ImpCheck = np.interp(Vmp, xp, fp)  # check Imp
        print "Imp Error = {:10.4g}%".format((Imp - ImpCheck) / Imp * 100)
        Isc = np.interp(0, xp, fp)
        FF = Pmp / Isc / Voc
        totalSuns = 0
        for pvstr in self.pvstrs:
            for pvmod in pvstr.pvmods:
                totalSuns += np.sum(pvmod.Ee)
        # convert cellArea from cm^2 to m^2
        Psun = self.pvconst.E0 * totalSuns * self.pvconst.cellArea / 100 / 100
        eff = Pmp / Psun
        return (Imp, Vmp, Pmp, Isc, Voc, FF, eff)

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
