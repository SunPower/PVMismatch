# -*- coding: utf-8 -*-
"""
This module defines the :class:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule`.
"""

import numpy as np
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, npinterpx, \
    MODSIZES, SUBSTRSIZES, NUMBERCELLS
from pvmismatch.pvmismatch_lib.pvcell import PVcell


class PVmodule(object):
    """
    PVmodule - A Class for PV modules.

    :param pvconst: An object with common parameters and constants.
    :type pvconst: :class:`PVconstants`
    :param numberCells: The number of cells in the module.
    :type numberCells: int
    :param subStrCells: A sequence of the number of cells in each
        substring. The length of the sequence is the number of substrings.
        The sum of the sequence must equal the number of cells in the
        module or else raises error.
    :param Ee: Effective irradiance in suns [1].
    :type Ee: float
    """
    def __init__(self, pvcells=PVcell(), numberCells=NUMBERCELLS, Ee=1,
                 subStrCells=None, pvconst=PVconstants()):
        # Constructor
        self.pvconst = pvconst
        self.numberCells = numberCells
        if subStrCells:
            self.subStrCells = subStrCells  # sequence of cells per substring
        elif self.numberCells in MODSIZES:
            self.subStrCells = SUBSTRSIZES[MODSIZES.index(self.numberCells)]
        else:
            self.subStrCells = [self.numberCells]
        self.numSubStr = len(self.subStrCells)  # number of substrings
        if sum(self.subStrCells) != self.numberCells:
            raise Exception("Invalid cells per substring!")
        self.Ee = Ee
        # initialize members so PyLint doesn't get upset
        self.Voc = self.Vcell = self.Vmod = self.Vsubstr = 0
        self.Icell = self.Imod = 0
        self.Pcell = self.Pmod = 0
        self.setSuns(Ee)

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
        self.Voc = self.calcVoc()
        (self.Icell, self.Vcell, self.Pcell) = self.calcCell()
        (self.Imod, self.Vmod, self.Pmod, self.Vsubstr) = self.calcMod()

    def calcCell(self):
        """
        Calculate cell I-V curves.
        Returns (Icell, Vcell, Pcell) : tuple of numpy.ndarray of float
        """
        Vdiode = self.Voc * self.pvconst.pts
        VPTS = self.pvconst.VRBD * self.pvconst.negpts
        VPTS = VPTS.repeat(self.numberCells, axis=1)
        Vdiode = np.concatenate((VPTS, Vdiode), axis=0)
        Igen = self.pvconst.Aph * self.pvconst.Isc0 * self.Ee
        Idiode1 = (self.pvconst.Isat1 * (np.exp(self.pvconst.q * Vdiode /
                   self.pvconst.k / self.pvconst.Tcell) - 1))
        Idiode2 = (self.pvconst.Isat2 * (np.exp(self.pvconst.q * Vdiode / 2 /
                   self.pvconst.k / self.pvconst.Tcell) - 1))
        Ishunt = Vdiode / self.pvconst.Rsh
        fRBD = (1 - Vdiode / self.pvconst.VRBD)
        fRBD_zeros = (fRBD == 0)
        if np.any(fRBD_zeros):
            # use epsilon = 2.2204460492503131e-16 to avoid "divide by zero"
            fRBD[fRBD_zeros] = np.finfo(np.float64).eps
        fRBD = self.pvconst.aRBD * fRBD ** (-self.pvconst.nRBD)
        Icell = Igen - Idiode1 - Idiode2 - Ishunt * (1 + fRBD)
        Vcell = Vdiode - Icell * self.pvconst.Rs
        Pcell = Icell * Vcell
        return (Icell, Vcell, Pcell)

    def calcMod(self):
        """
        Calculate module I-V curves.
        Returns (Imod, Vmod, Pmod) : tuple of numpy.ndarray of float
        """
        # create range for interpolation, it must include reverse bias
        # and some negative current to interpolate all cells
        # find Icell at Vrbd for all cells in module
        IatVrbd = [np.interp(self.pvconst.VRBD, Vcell, Icell) for
                   (Vcell, Icell) in zip(self.Vcell.T, self.Icell.T)]
        Isc = np.mean(self.Ee) * self.pvconst.Isc0
        # max current
        Imax = (np.max(IatVrbd) - Isc) * self.pvconst.Imod_pts + Isc
        Imin = np.min(self.Icell)
        Imin = Imin if Imin < 0 else 0
        Ineg = (Imin - Isc) * self.pvconst.Imod_negpts + Isc  # min current
        Imod = np.concatenate((Ineg, Imax), axis=0)  # interpolation range
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
