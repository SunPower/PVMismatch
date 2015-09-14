# -*- coding: utf-8 -*-
"""
This module contains configuration constants for PVMismatch, such as number of
points in IV curve to calculate, flag to use parallel processing and parallel
processing parameters. This module also contains some utility functions like
:func:`~pvmismatch.pvmismatch_lib.pvconstants.npinterpx()` are defined here too.
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

    Parameters
    ----------
    x : array_like
        The x-coordinates of the interpolated values.

    xp : 1-D sequence of floats
        The x-coordinates of the data points, must be increasing.

    fp : 1-D sequence of floats
        The y-coordinates of the data points, same length as `xp`.

    Returns
    -------
    y : {float, ndarray}
        The interpolated values, same shape as `x`.

    Raises
    ------
    ValueError
        If `xp` and `fp` have different length
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

    :param npts: number of points in IV curve
    :type npts: int
    :param parallel: use parallel processing flag
    :type parallel: bool
    :param procs: number of processes for parallel
    :type procs: int
    :param maxtaskperchild: number of task before worker dies
    :type maxtaskperchild: int
    :param chunksize: amount of data per task
    :type chunksize: int
    """

    # hard constants
    k = scipy.constants.k  #: [kJ/mole/K] Boltzmann constant
    q = scipy.constants.e  #: [Coloumbs] elementary charge
    E0 = 1000.  #: [W/m^2] irradiance of 1 sun
    T0 = 298.15  #: [K] reference temperature

    def __init__(self, npts=NPTS, parallel=PARALLEL, procs=PROCS,
                 maxtasksperchild=MAXTASKSPERCHILD, chunksize=CHUNKSIZE):
        # set number of points in IV curve(s)
        self.npts = npts  #: number of points in IV curves
        # point spacing from 0 to 1, used for Vcell, Vmod, Vsys and Istring
        # decrease point spacing as voltage approaches Voc by using logspace
        pts = (11. - np.logspace(np.log10(11.), 0., self.npts)) / 10.
        pts[0] = 0.  # first point must be exactly zero
        self.pts = pts.reshape(self.npts, 1)
        """array of points with decreasing spacing from 0 to 1"""
        negpts = (11. - np.logspace(np.log10(11. - 1. / np.float64(self.npts)),
                                    0., self.npts)) / 10.
        negpts = negpts.reshape(self.npts, 1)
        self.Imod_negpts = 1 + 1. / np.float64(self.npts) / 10. - negpts
        """array of points with decreasing spacing from 1 to just less than but
        not including zero"""
        self.negpts = np.flipud(negpts)  # reverse the order
        """array of points with increasing spacing from 1 to just less than but
        not including zero"""
        # shift and concatenate pvconst.negpts and pvconst.pts
        # so that tight spacing is around MPP and RBD
        self.Imod_pts = 1 - np.flipud(self.pts)
        """array of points with increasing spacing from 0 to 1"""
        # multiprocessing
        self.parallel = parallel  #: use multiprocessing if True
        self.procs = procs  #: number of processes in pool
        self.maxtasksperchild = maxtasksperchild  #: number of tasks per worker
        self.chunksize = chunksize  #: size of tasks

    def __str__(self):
        return '<PVconstants(npts=%d, parallel=%s)>' % (self.npts, self.parallel)

    def __repr__(self):
        return str(self)

    def calcSeries(self, I, V, meanIsc, Imax):
        """
        Calculate IV curve for cells and substrings in series.
        :param I: cell or substring currents [A]
        :param V: cell or substring voltages [V]
        :param meanIsc: average short circuit currenta [A]
        :param Imax: maximum current [A]
        :return: current [A] and voltage [V] of series
        """
        # make sure all inputs are numpy arrays, but don't make extra copies
        I = np.asarray(I)  # currents [A]
        V = np.asarray(V)  # voltages [V]
        meanIsc = np.asarray(meanIsc)  # mean Isc [A]
        Imax = np.asarray(Imax)  # max current [A]
        # create array of currents optimally spaced from mean Isc to  max VRBD
        Ireverse = (Imax - meanIsc) * self.Imod_pts + meanIsc
        Imin = np.minimum(I.min(), 0.)  # minimum cell current, at most zero
        # range of currents in forward bias from min current to mean Isc
        Iforward = (Imin - meanIsc) * self.Imod_negpts + meanIsc
        # create range for interpolation from forward to reverse bias
        Itot = np.concatenate((Iforward, Ireverse), axis=0).flatten()
        Vtot = np.zeros((2 * self.npts,))
        # add up all series cell voltages
        for i, v in zip(I, V):
            # interp requires x, y to be sorted by x in increasing order
            Vtot += npinterpx(Itot, np.flipud(i), np.flipud(v))
        # TODO: flip again on the way out so that voltage is always increasing
        return Itot, Vtot

    def calcParallel(self):
        pass


def Vdiode(Icell, Vcell, Rs):
    return Vcell + Icell * Rs


def Idiode(Isat, Vdiode, Vt, n):
    return Isat * (np.exp(Vdiode / n / Vt) - 1)


def Ishunt(Vdiode, Rsh):
    return Vdiode / Rsh


def Igen(Aph, Ee, Isc0):
    return Aph * Ee * Isc0
