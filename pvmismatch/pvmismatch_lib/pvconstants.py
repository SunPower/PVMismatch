# -*- coding: utf-8 -*-
"""
This module contains configuration constants for PVMismatch, such as number of
points in IV curve to calculate, flag to use parallel processing and parallel
processing parameters. This module also contains some utility functions like
:func:`~pvmismatch.pvmismatch_lib.npinterpx()` are defined here too.
"""

# TODO: move this to pvmismatch_lib/__init__.py

import numpy as np
import scipy.constants

# Constants
NPTS = 101  # number of I-V points to calculate
MODSIZES = [24, 72, 96, 128]  # list of possible number of cells per module
SUBSTRSIZES = [[2] * 12, [24] * 3, [24, 48, 24], [32, 64, 32]]
NUMBERCELLS = MODSIZES[2]  # default is 96-cell module
NUMBERMODS = 10  # default number of modules
NUMBERSTRS = 10  # default number of strings

# Multiprocessing
PARALLEL = False  # <boolean> use multiprocessing
PROCS = None  # number of processes in pool, defaults to cpu_count()
MAXTASKSPERCHILD = 10  # number of tasks before worker exits to free memory
CHUNKSIZE = None  # size of each task sent to process and assign to workers


def npinterpx(x, xp, fp):
    """
    Numpy interpolation function with linear extrapolation.
    """
    y = np.interp(x, xp, fp)
    # extrapolate left
    left = x < xp[0]
    xleft = x[left]
    yleft = fp[0] + (xleft - xp[0]) / (xp[1] - xp[0]) * (fp[1] - fp[0])
    y[left] = yleft
    # extrapolate right
    right = x > xp[-1]
    xright = x[right]
    yright = fp[-1] + (xright - xp[-1]) / (xp[-2] - xp[-1]) * (fp[-2] - fp[-1])
    y[right] = yright
    return y


class PVconstants(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, npts=NPTS, parallel=PARALLEL, procs=PROCS,
                 maxtasksperchild=MAXTASKSPERCHILD, chunksize=CHUNKSIZE):
        # set number of points in IV curve(s)
        self.npts = npts  # number of points
        # point spacing from 0 to 1, used for Vcell, Vmod, Vsys and Istring
        # decrease point spacing as voltage approaches Voc by using logspace
        pts = (11. - np.logspace(np.log10(11.), 0., self.npts)) / 10.
        pts[0] = 0.  # first point must be exactly zero
        self.pts = pts.reshape(self.npts, 1)
        negpts = (11. - np.logspace(np.log10(11. - 1./float(self.npts)),
                                    0., self.npts)) / 10.
        negpts = negpts.reshape(self.npts, 1)
        self.Imod_negpts = 1 + 1./float(self.npts)/10. - negpts
        self.negpts = np.flipud(negpts)  # reverse the order
        # shift and concatenate pvconst.negpts and pvconst.pts
        # so that tight spacing is around MPP and RBD
        self.Imod_pts = 1 - np.flipud(self.pts)
        # multiprocessing
        self.parallel = parallel  # use multiprocessing if True
        self.procs = procs  # number of processes in pool
        self.maxtasksperchild = maxtasksperchild  # number of tasks per worker
        self.chunksize = chunksize  # size of tasks

    def update(self, *args, **kwargs):
        """
        Update user-defined constants.
        """
        kw = ['Rs', 'Rsh', 'Isat1_T0', 'Isat2', 'Aph', 'Isc0_T0', 'Tcell',
              'cellArea', 'Vbypass', 'aRBD', 'VRBD', 'nRBD', 'npts', 'Eg',
              'alpha_Isc']
        key = 0
        keys = []
        # set positional arguements (*args)
        for val in args:
            self.__setattr__(kw[key], float(val))
            key += 1
            keys.append(kw[key])
        # set optional arguments (*kwargs)
        for key in kwargs:
            if key in kw:
                self.__setattr__(key, float(kwargs[key]))
        # Check & update Isat1
        calc_Isat1 = 'Isat1_T0' in keys or 'Isat1_T0' in kwargs.keys()
        calc_Isat1 = calc_Isat1 or 'Tcell' in keys or 'Tcell' in kwargs.keys()
        calc_Isat1 = calc_Isat1 or 'Eg' in keys or 'Eg' in kwargs.keys()
        if calc_Isat1:
            self.Isat1 = self.calc_Isat1()  # [A] Isat1
        # Check & update Isc0
        calc_Isc0 = 'Isc0_T0' in keys or 'Isc0_T0' in kwargs.keys()
        calc_Isc0 = calc_Isc0 or 'Tcell' in keys or 'Tcell' in kwargs.keys()
        calc_Isc0 = (calc_Isc0 or
                       'alpha_Isc' in keys or 'alpha_Isc' in kwargs.keys())
        if calc_Isc0:
            self.Isc0 = self.calc_Isc0()  # [A] Isc0

    # TODO: try to override self.__setattr__  # IGNORE:W0511
    def calc_Isat1(self):
        """
        Diode one saturation current at Tcell.
        """
        _Tstar = self.Tcell ** 3 / self.T0 ** 3  # scaled temperature
        _inv_delta_T = 1 / self.T0 - 1 / self.Tcell  # [1/K]
        _expTstar = np.exp(self.Eg * self.q / self.k * _inv_delta_T)
        return self.Isat1_T0 * _Tstar * _expTstar  # [A] Isat1(Tcell)

    def calc_Isc0(self):
        """
        Short circuit current at Tcell
        """
        _delta_T = self.Tcell - self.T0  # [K] temperature difference
        return self.Isc0_T0 * (1 + self.alpha_Isc * _delta_T)  # [A] Isc0
