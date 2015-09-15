# -*- coding: utf-8 -*-
"""
This module defines the :class:`~pvmismatch.pvmismatch_lib.pvmodule.PVmodule`.
"""

import numpy as np
from copy import copy
from matplotlib import pyplot as plt
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants, get_series_cells
from pvmismatch.pvmismatch_lib.pvcell import PVcell

VBYPASS = -0.5  # [V] trigger voltage of bypass diode


def standard_cellpos_pat(nrows, ncols_per_substr):
    cellpos = []
    ncols = [0, 0]
    for substr_cols in ncols_per_substr:
        ncols[0], ncols[1] = ncols[1], ncols[1] + substr_cols
        newsubstr = []
        for col in xrange(*ncols):
            newrow = []
            for row in xrange(nrows):
                idx = col * nrows
                if col % 2 == 0:
                    idx += row
                else:
                    idx += (nrows - row - 1)
                newrow.append({'circuit': 'series', 'idx': idx})
            newsubstr.append(newrow)
        cellpos.append(newsubstr)
    return cellpos

# standard cell positions presets
STD72 = standard_cellpos_pat(12, [2, 2, 2])
STD96 = standard_cellpos_pat(12, [2, 4, 2])
STD128 = standard_cellpos_pat(16, [2, 4, 2])


def crosstied_cellpos_pat(nrows_per_substrs, ncols, partial=False):
    trows = sum(nrows_per_substrs)
    cellpos = []
    nrows = [0, 0]
    for substr_row in nrows_per_substrs:
        nrows[0], nrows[1] = nrows[1], nrows[1] + substr_row
        newsubstr = []
        for col in xrange(ncols):
            newrow = []
            for row in xrange(*nrows):
                circuit = 'parallel'
                if partial and newrow:
                    circuit = 'series'
                newrow.append({'circuit': circuit, 'idx': col * trows + row})
            newsubstr.append(newrow)
        cellpos.append(newsubstr)
    return cellpos

# crosstied cell positions presets
TCT96 = crosstied_cellpos_pat([4, 4, 4], 8)
PCT96 = crosstied_cellpos_pat([4, 4, 4], 8, partial=True)


def combine_parallel_circuits(IVprev_cols, pvconst):
    """
    Combine parallel circuits in a substring
    :param IVprev_cols: lists of IV curves of parallel and series circuits
    :return:
    """
    # combine parallel circuits
    Irows, Vrows = [], []
    Isc_rows, Imax_rows = [], []
    for IVcols in zip(*IVprev_cols):
        Iparallel, Vparallel = zip(*IVcols)
        Iparallel = np.asarray(Iparallel)
        Vparallel = np.asarray(Vparallel)
        Irow, Vrow = pvconst.calcParallel(
            Iparallel, Vparallel, Vparallel.max(),
            Vparallel.min()
        )
        Irows.append(Irow)
        Vrows.append(Vrow)
        Isc_rows.append(np.interp(0., Vrow, Irow))
        Imax_rows.append(Irow.max())
    Irows, Vrows = np.asarray(Irows), np.asarray(Vrows)
    Isc_rows = np.asarray(Isc_rows)
    Imax_rows = np.asarray(Imax_rows)
    return pvconst.calcSeries(
        Irows, Vrows, Isc_rows.mean(), Imax_rows.max()
    )

class PVmodule(object):
    """
    PVmodule - A Class for PV modules.

    :param cell_pos: cell position pattern
    :type cell_pos: dict
    :param pvcells: list of :class:`~pvmismatch.pvmismatch_lib.pvcell.PVcell`
    :type pvcells: list
    :param pvconst: An object with common parameters and constants.
    :type pvconst: :class:`~pvmismatch.pvmismatch_lib.pvconstants.PVconstants`
    :param Vbypass: bypass diode trigger voltage [V]
    :type Vbypass: float
    """
    def __init__(self, cell_pos=STD96, pvcells=None, pvconst=PVconstants(),
                 Vbypass=VBYPASS):
        # TODO: check cell position pattern
        self.cell_pos = cell_pos  #: cell position pattern dictionary
        self.numberCells = sum([len(c) for s in self.cell_pos for c in s])
        """number of cells in the module"""
        self.pvconst = pvconst  #: configuration constants
        self.Vbypass = Vbypass  #: [V] trigger voltage of bypass diode
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
        self.numSubStr = len(self.cell_pos)  #: number of substrings
        self.subStrCells = [len(_) for _ in self.cell_pos]  #: cells per substr
        # initialize members so PyLint doesn't get upset
        self.Imod, self.Vmod, self.Pmod, self.Vsubstr = self.calcMod()
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
                for pvc in self.pvcells:
                    pvc.Ee = Ee
            elif np.size(Ee) == self.numberCells:
                for pvc, Ee_idx in zip(self.pvcells, Ee):
                    pvc.Ee = Ee_idx
            else:
                raise Exception("Input irradiance value (Ee) for each cell!")
        else:
            Ncells = np.size(cells)
            if np.isscalar(Ee):
                for cell_idx in cells:
                    self.pvcells[cell_idx].Ee = Ee
            elif np.size(Ee) == Ncells:
                for cell_idx, Ee_idx in zip(cells, Ee):
                    self.pvcells[cell_idx].Ee = Ee_idx
            else:
                raise Exception("Input irradiance value (Ee) for each cell!")
        self.Imod, self.Vmod, self.Pmod, self.Vsubstr = self.calcMod()

    def calcMod(self):
        """
        Calculate module I-V curves.
        Returns (Imod, Vmod, Pmod) : tuple of numpy.ndarray of float
        """
        # iterate over substrings
        # TODO: benchmark speed difference append() vs preallocate space
        Isubstr, Vsubstr, Isc_substr, Imax_substr = [], [], [], []
        for substr in self.cell_pos:
            # check if cells are in series or any parallel circuits
            if all(r['circuit'] == 'series' for c in substr for r in c):
                idxs = [r['idx'] for c in substr for r in c]
                IatVrbd = np.asarray(
                    [np.interp(vrbd, v, i) for vrbd, v, i in
                     zip(self.VRBD[idxs], self.Vcell[idxs], self.Icell[idxs])]
                )
                Isub, Vsub = self.pvconst.calcSeries(
                    self.Icell[idxs], self.Vcell[idxs], self.Isc[idxs].mean(),
                    IatVrbd.max()
                )
            elif all(r['circuit'] == 'parallel' for c in substr for r in c):
                Irows, Vrows = [], []
                Isc_rows, Imax_rows = [], []
                for row in zip(*substr):
                    idxs = [c['idx'] for c in row]
                    Irow, Vrow = self.pvconst.calcParallel(
                        self.Icell[idxs], self.Vcell[idxs],
                        self.Voc[idxs].max(), self.VRBD.min()
                    )
                    Irows.append(Irow)
                    Vrows.append(Vrow)
                    Isc_rows.append(np.interp(0., Vrow, Irow))
                    Imax_rows.append(Irow.max())
                Irows, Vrows = np.asarray(Irows), np.asarray(Vrows)
                Isc_rows = np.asarray(Isc_rows)
                Imax_rows = np.asarray(Imax_rows)
                Isub, Vsub = self.pvconst.calcSeries(
                    Irows, Vrows, Isc_rows.mean(), Imax_rows.max()
                )
            else:
                IVall_cols = []
                prev_col = None
                IVprev_cols = []
                for col in substr:
                    IVcols = []
                    is_first = True
                    # combine series between crossties
                    for idxs in get_series_cells(col, prev_col):
                        if not idxs:
                            # first row should always be empty since it must be
                            # crosstied
                            is_first = False
                            continue
                        elif is_first:
                            # TODO: use pvmismatch exceptions
                            raise Exception(
                                "First row and last rows must be crosstied."
                            )
                        elif len(idxs) > 1:
                            IatVrbd = np.asarray(
                                [np.interp(vrbd, v, i) for vrbd, v, i in
                                 zip(self.VRBD[idxs], self.Vcell[idxs],
                                     self.Icell[idxs])]
                            )
                            Icol, Vcol = self.pvconst.calcSeries(
                                self.Icell[idxs], self.Vcell[idxs],
                                self.Isc[idxs].mean(), IatVrbd.max()
                            )
                        else:
                            Icol, Vcol = self.Icell[idxs], self.Vcell[idxs]
                        IVcols.append([Icol, Vcol])
                    # append IVcols and continue
                    IVprev_cols.append(IVcols)
                    if prev_col:
                        # if circuits are same in both columns then continue
                        if not all(icol['circuit'] == jcol['circuit']
                                   for icol, jcol in zip(prev_col, col)):
                            # combine parallel circuits
                            Iparallel, Vparallel = combine_parallel_circuits(
                                IVprev_cols, self.pvconst
                            )
                            IVall_cols.append([Iparallel, Vparallel])
                            # reset prev_col
                            prev_col = None
                            IVprev_cols = []
                            continue
                    # set prev_col and continue
                    prev_col = col
                # combine any remaining parallel circuits in substring
                if not IVall_cols:
                    # combine parallel circuits
                    Isub, Vsub = combine_parallel_circuits(
                        IVprev_cols, self.pvconst
                    )
                else:
                    Iparallel, Vparallel = zip(*IVall_cols)
                    Iparallel = np.asarray(Iparallel)
                    Vparallel = np.asarray(Vparallel)
                    Isub, Vsub = self.pvconst.calcParallel(
                        Iparallel, Vparallel, Vparallel.max(), Vparallel.min()
                    )
            bypassed = Vsub < self.Vbypass
            Vsub[bypassed] = self.Vbypass
            Isubstr.append(Isub)
            Vsubstr.append(Vsub)
            Isc_substr.append(np.interp(0., Vsub, Isub))
            Imax_substr.append(Isub.max())
        Isubstr, Vsubstr = np.asarray(Isubstr), np.asarray(Vsubstr)
        Isc_substr = np.asarray(Isc_substr)
        Imax_substr = np.asarray(Imax_substr)
        Imod, Vmod = self.pvconst.calcSeries(
            Isubstr, Vsubstr, Isc_substr.mean(), Imax_substr.max()
        )
        Pmod = Imod * Vmod
        return Imod, Vmod, Pmod, Vsubstr

    def plotCell(self):
        """
        Plot cell I-V curves.
        Returns cellPlot : matplotlib.pyplot figure
        """
        cellPlot = plt.figure()
        plt.subplot(2, 2, 1)
        plt.plot(self.Vcell.T, self.Icell.T)
        plt.title('Cell Reverse I-V Characteristics')
        plt.ylabel('Cell Current, I [A]')
        plt.xlim(self.VRBD.min() - 1, 0)
        plt.ylim(0, self.Isc.mean() + 10)
        plt.grid()
        plt.subplot(2, 2, 2)
        plt.plot(self.Vcell.T, self.Icell.T)
        plt.title('Cell Forward I-V Characteristics')
        plt.ylabel('Cell Current, I [A]')
        plt.xlim(0, self.Voc.max())
        plt.ylim(0, self.Isc.mean() + 1)
        plt.grid()
        plt.subplot(2, 2, 3)
        plt.plot(self.Vcell.T, self.Pcell.T)
        plt.title('Cell Reverse P-V Characteristics')
        plt.xlabel('Cell Voltage, V [V]')
        plt.ylabel('Cell Power, P [W]')
        plt.xlim(self.VRBD.min() - 1, 0)
        plt.ylim((self.Isc.mean() + 10) * (self.VRBD.min() - 1), -1)
        plt.grid()
        plt.subplot(2, 2, 4)
        plt.plot(self.Vcell.T, self.Pcell.T)
        plt.title('Cell Forward P-V Characteristics')
        plt.xlabel('Cell Voltage, V [V]')
        plt.ylabel('Cell Power, P [W]')
        plt.xlim(0, self.Voc.max())
        plt.ylim(0, (self.Isc.mean() + 1) * self.Voc.max())
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
        plt.ylim(ymin=0)
        plt.xlim(self.Vmod.min() - 1, self.Vmod.max() + 1)
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(self.Vmod, self.Pmod)
        plt.title('Module P-V Characteristics')
        plt.xlabel('Module Voltage, V [V]')
        plt.ylabel('Module Power, P [W]')
        plt.ylim(ymin=0)
        plt.xlim(self.Vmod.min() - 1, self.Vmod.max() + 1)
        plt.grid()
        return modPlot
