# -*- coding: utf-8 -*-
"""
Created on Jul 16, 2012

@author: mmikofski
"""

from matplotlib import pyplot as plt
from pvmismatch.pvconstants import PVconstants, npinterpx
from pvmismatch.pvmodule import PTS, NPTS
from pvmismatch.pvstring import PVstring
import numpy as np

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
            self.pvstrs = [PVstring(pvconst=self.pvconst)
                           for pvstr in range(self.numberStrs)]
            # Don't use `itertools.repeat(e, n)` or `[e]  * n` because copies
            # all point to the same object.
        elif ((type(pvstrs) is list) and
              all([(type(pvstr) is PVstring) for pvstr in pvstrs])):
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
        Vstring = np.array([pvstr.Vstring for pvstr in self.pvstrs])
        Vsys = np.max(Vstring) * PTS
        for pvstr in self.pvstrs:
            (pvstr.Istring, pvstr.Vstring, pvstr.Pstring) = pvstr.calcString()
            xp = np.flipud(pvstr.Vstring.reshape(NPTS))
            fp = np.flipud(pvstr.Istring.reshape(NPTS))
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
        Pv = np.flipud(Pv.reshape(NPTS - 1))  # (1000,) increasing
        Vhalf = (self.Vsys[1:] + self.Vsys[:-1]) / 2  # (1000, 1) increasing
        Vhalf = np.flipud(Vhalf.reshape(NPTS - 1))  # (1000,)
        Vmp = np.interp(0., Pv, Vhalf)  # estimate Vmp
        Imp = Pmp / Vmp  # calculate Imp
        xp = np.flipud(self.Isys.reshape(NPTS))  # must be increasing
        fp = np.flipud(self.Vsys.reshape(NPTS))  # keep data correspondence
        Voc = np.interp(0., xp, fp)  # calucalte Voc
        xp = self.Vsys.reshape(NPTS)
        fp = self.Isys.reshape(NPTS)
        ImpCheck = np.interp(Vmp, xp, fp)  # check Imp
        print " Imp Error = {:10.4g}%".format((Imp - ImpCheck) / Imp * 100)
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
        plt.title('System I-V Characteristics')
        plt.ylabel('System Current, I [A]')
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vsys, self.Psys)
        plt.title('System P-V Characteristics')
        plt.xlabel('System Voltage, V [V]')
        plt.ylabel('System Power, P [W]')
        plt.grid()
        return sysPlot
