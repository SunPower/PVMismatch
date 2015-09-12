# -*- coding: utf-8 -*-
"""
This module defines the :class:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule`.
"""

import numpy as np
from copy import copy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, npinterpx, \
    MODSIZES, SUBSTRSIZES, NUMBERCELLS
from pvmismatch.pvmismatch_lib.pvcell import PVcell


def zip_flat_meshgrid(nrows, ncols):
    x, y = np.meshgrid(np.arange(nrows), np.arange(ncols))
    return zip(x.flat, y.flat)


def serpentine(nrows, ncols):
    x, y = np.meshgrid(np.arange(nrows), np.arange(ncols))
    x[1::2] = np.fliplr(x[1::2])  # flip alternate rows
    return zip(x.flat,y.flat)


# cell positions presets
STD72 = [
    {'row': r, 'col': c,
     'series': (n + 1 if n < 71 else None), 'parallel': None,
     'substring': n / 24} for n, (r, c) in enumerate(serpentine(12, 6))
]
STD96 = [
    {'row': r, 'col': c,
     'series': (n + 1 if n < 95 else None), 'parallel': None,
     'substring': (n + 24) / 48} for n, (r, c) in enumerate(serpentine(12, 8))
]
STD128 = [
    {'row': r, 'col': c,
     'series': (n + 1 if n < 127 else None), 'parallel': None,
     'substring': (n + 32) / 64} for n, (r, c) in enumerate(serpentine(16, 8))
]
TCT96 = [
    {'row': r, 'col': c,
     'series': c * 12 + r + 1 if r < 11 else None,
     'parallel': (c + 1) * 12 + r if c < 7 else None,
     'substring': r / 4} for r, c in zip_flat_meshgrid(12, 8)
]


class PVmodule(object):
    """
    PVmodule - A Class for PV modules.

    :param pvconst: An object with common parameters and constants.
    :type pvconst: :class:`PVconstants`
    :param numberCells: The number of cells in the module.
    :param Ee: Effective irradiance in suns [1].
    :type Ee: float
    """
    def __init__(self, cell_pos=STD96, pvcells=None, pvconst=PVconstants()):
        # TODO: check cell position pattern
        self.cell_pos = cell_pos
        self.numberCells = len(self.cell_pos)
        self.pvconst = pvconst
        if pvcells is None:
            # faster to use copy instead of making each object in a for-loop
            # use copy instead of deepcopy to keey same pvconst for all objects
            # PVcell.calcCell() creates new np.ndarray if attributes change
            pvc = PVcell(pvconst=pvconst)
            pvcells = [copy(pvc) for _ in xrange(self.numberCells)]
        else:
            if len(pvcells) != self.numberCells:
                # TODO: use pvexception
                raise Exception(
                    "Number of cells doesn't match cell position pattern."
                )
        self.pvcells = pvcells  #: list of `PVcell` objects in this `PVmodule`
        self.substrings = {z['substring'] for z in self.cell_pos}
        self.substr_cellidx = [[idx for idx, cidx in enumerate(self.cell_pos)
                                if cidx['substring'] == substr]
                               for substr in self.substrings]
        self.subStrCells = [len([_ for _ in self.substr_cellidx])]
        self.numSubStr = len(self.substrings)  # number of substrings
        if sum(self.subStrCells) != self.numberCells:
            # TODO: use pvexception
            raise Exception("Invalid cells per substring!")
        # initialize members so PyLint doesn't get upset
        self.Vmod = self.Vsubstr =  self.Imod = self.Pmod = 0
        # self.setSuns(Ee)

    # copy some values from cells to modules
    @property
    def Ee(self):
        return np.array([pvc.Ee.flatten() for pvc in self.pvcells])

    @property
    def Tcell(self):
        return np.array([pvc.Tcell.flatten() for pvc in self.pvcells])

    @property
    def Icell(self):
        return np.array([pvc.Icell.flatten() for pvc in self.pvcells])

    @property
    def Vcell(self):
        return np.array([pvc.Vcell.flatten() for pvc in self.pvcells])

    @property
    def Pcell(self):
        return np.array([pvc.Pcell.flatten() for pvc in self.pvcells])

    @property
    def Isc(self):
        return np.array([pvc.Isc.flatten() for pvc in self.pvcells])

    @property
    def Voc(self):
        return np.array([pvc.Voc.flatten() for pvc in self.pvcells])

    @property
    def VRBD(self):
        return np.array([pvc.VRBD.flatten() for pvc in self.pvcells])

    def setSuns(self, Ee, cells=None):
        """
        Set the irradiance in suns, Ee, on the solar cells in the module.
        Recalculates cell current (Icell [A]), voltage (Vcell [V]) and power
        (Pcell [W]) as well as module current (Imod [A]), voltage (Vmod [V])
        and power (Pmod [W]).
        Arguments
            Ee : <float> or <np.array of floats> Effective Irradiance
        Optional
            cells : <np.array of int> Cells to change
        """
        if cells is None:
            if np.isscalar(Ee):
                self.Ee = np.ones((1, self.numberCells)) * Ee
            elif np.size(Ee) == self.numberCells:
                self.Ee = np.reshape(Ee, (1, self.numberCells))
            else:
                raise Exception("Input irradiance value (Ee) for each cell!")
        else:
            Nsuns = np.size(cells)
            if np.isscalar(Ee):
                self.Ee[0, cells] = np.ones(Nsuns) * Ee
            elif np.size(Ee) == Nsuns:
                self.Ee[0, cells] = Ee
            else:
                raise Exception("Input irradiance value (Ee) for each cell!")
        (self.Icell, self.Vcell, self.Pcell) = self.calcCell()
        (self.Imod, self.Vmod, self.Pmod, self.Vsubstr) = self.calcMod()

        # VPTS = VPTS.repeat(self.numberCells, axis=1)

    def calcMod(self):
        """
        Calculate module I-V curves.
        Returns (Imod, Vmod, Pmod) : tuple of numpy.ndarray of float
        """
        # range of currents in reverse bias from max cell current to mean Isc
        meanIsc = self.Isc.mean()  # average short circuit current
        Imax = (self.Icell.max() - meanIsc) * self.pvconst.Imod_pts + meanIsc
        Imin = min(self.Icell.min(), 0.)  # minimum cell current, at most zero
        # range of currents in forward bias from mean Isc to min current
        Imin = (Imin - meanIsc) * self.pvconst.Imod_negpts + meanIsc
        # create range for interpolation from reverse and forward bias
        Imod = np.concatenate((Imin, Imax), axis=0)  # interpolation range
        Vsubstr = np.zeros((2 * self.pvconst.npts, self.numSubStr))
        start = np.cumsum(self.subStrCells) - self.subStrCells
        stop = np.cumsum(self.subStrCells)
        for substr in range(self.numSubStr):
            for cell in range(start[substr], stop[substr]):
                xp = np.flipud(self.Icell[:, cell])
                fp = np.flipud(self.Vcell[:, cell])
                Vsubstr[:, substr] += npinterpx(Imod.flatten(), xp, fp)
        bypassed = Vsubstr < self.pvconst.Vbypass
        Vsubstr[bypassed] = self.pvconst.Vbypass
        Vmod = np.sum(Vsubstr, 1).reshape(2 * self.pvconst.npts, 1)
        Pmod = Imod * Vmod
        return (Imod, Vmod, Pmod, Vsubstr)

    def plotCell(self):
        """
        Plot cell I-V curves.
        Returns cellPlot : matplotlib.pyplot figure
        """
        cellPlot = plt.figure()
        plt.subplot(2, 2, 1)
        plt.plot(self.Vcell, self.Icell)
        plt.title('Cell Reverse I-V Characteristics')
        plt.ylabel('Cell Current, I [A]')
        plt.xlim(self.pvconst.VRBD - 1, 0)
        plt.ylim(0, self.pvconst.Isc0 + 10)
        plt.grid()
        plt.subplot(2, 2, 2)
        plt.plot(self.Vcell, self.Icell)
        plt.title('Cell Forward I-V Characteristics')
        plt.ylabel('Cell Current, I [A]')
        plt.xlim(0, np.max(self.Voc))
        plt.ylim(0, self.pvconst.Isc0 + 1)
        plt.grid()
        plt.subplot(2, 2, 3)
        plt.plot(self.Vcell, self.Pcell)
        plt.title('Cell Reverse P-V Characteristics')
        plt.xlabel('Cell Voltage, V [V]')
        plt.ylabel('Cell Power, P [W]')
        plt.xlim(self.pvconst.VRBD - 1, 0)
        plt.ylim((self.pvconst.Isc0 + 10) * (self.pvconst.VRBD - 1), -1)
        plt.grid()
        plt.subplot(2, 2, 4)
        plt.plot(self.Vcell, self.Pcell)
        plt.title('Cell Forward P-V Characteristics')
        plt.xlabel('Cell Voltage, V [V]')
        plt.ylabel('Cell Power, P [W]')
        plt.xlim(0, np.max(self.Voc))
        plt.ylim(0, (self.pvconst.Isc0 + 1) * np.max(self.Voc))
        plt.grid()
        return cellPlot

    def plotMod(self):
        """
        Plot module I-V curves.
        Returns modPlot : matplotlib.pyplot figure
        """
        modPlot = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.Vmod, self.Imod)
        plt.title('Module I-V Characteristics')
        plt.ylabel('Module Current, I [A]')
        plt.ylim(ymax=self.pvconst.Isc0 + 1)
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vmod, self.Pmod)
        plt.title('Module P-V Characteristics')
        plt.xlabel('Module Voltage, V [V]')
        plt.ylabel('Module Power, P [W]')
        plt.grid()
        return modPlot
