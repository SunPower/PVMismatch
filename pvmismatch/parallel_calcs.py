# -*- coding: utf-8 -*-

"""
Created on Tue Mar 26 13:49:04 2013

@author: mmikofski
"""

from functools import partial
from multiprocessing import current_process, Pool, cpu_count
from pvmismatch.pvconstants import npinterpx
from pvmismatch.pvexceptions import PVparallel_calcError
import numpy as np


def parallel_calcSystem(pvsys, Vsys):
    """
    Embarrassingly parallel calculations.
    """    # protect main thread
    if current_process().name != 'MainProcess':
        raise PVparallel_calcError(__name__)
    # pool overhead is high, create once and reuse processes
    # if procs is None, set it cpu_count - 2, so 2 cores are free
    procs = pvsys.pvconst.procs
    if not procs:
        procs = cpu_count() - 2
    pool = Pool(processes=procs,
                maxtasksperchild=pvsys.pvconst.maxtasksperchild)
    # if chunksize is None, then divide tasks evenly between all procs
    chunksize = pvsys.pvconst.chunksize
    if not chunksize:
        chunksize = (pvsys.numberStrs * pvsys.numberMods) / procs
    # limit data pickled and sent to process to reduce overhead
    # flatten pvmods to 1-D
    pvmods = np.reshape(pvsys.pvmods, (pvsys.numberStrs * pvsys.numberMods, ))
    # extract Imod[0], Imod[-1] and Ee, reorganize back into strings of modules
    Istring_args = np.array([(pvmod.Imod[0], pvmod.Imod[-1],
                              np.mean(pvmod.Ee, dtype=float)) for pvmod in
                             pvmods], dtype=float).reshape(pvsys.numberStrs,
                                                           pvsys.numberMods, 3)
    # index-0: strings, index-1: modules, index-2: (Imax, Imin, Eavg)
    Istring_args = np.concatenate((np.min(Istring_args[:, :, 0], 1,
                                          keepdims=True),
                                   np.max(Istring_args[:, :, 1], 1,
                                          keepdims=True),
                                   (np.mean(Istring_args[:, :, 2], 1,
                                            dtype=float, keepdims=True) *
                                    pvsys.pvconst.Isc0)), 1)
    # only use pool if more than one string
    if pvsys.numberStrs == 1:
        # transpose from (<npts>, 1) to (1, <npts>) to match pool.map
        Istring = calcIstring(Istring_args.squeeze(), pvsys.pvconst.Imod_pts,
                              pvsys.pvconst.Imod_negpts).T
    else:
        partial_calcIstring = partial(calcIstring,
                                      Imod_pts=pvsys.pvconst.Imod_pts,
                                      Imod_negpts=pvsys.pvconst.Imod_negpts)
        Istring = pool.map(partial_calcIstring, Istring_args, chunksize)
        # squeeze take array-like, removes singleton dimensions
        # converts (<numberStrs>, <npts>, 1) to (<numberStrs>, <npts>)
        Istring = np.squeeze(Istring)
    # only use pool if more than one module
    if pvsys.numberStrs * pvsys.numberMods == 1:
        Vstring = interpMods((pvsys.pvmods[0][0], Istring))
    else:
        # expand Istring for every module in each string
        # repeat is smart - it repeats the each row <repeats> times,
        # so each string is kept together [[str1-mod1],...,[str2-mod1],...]
        Imodstr = Istring.repeat(pvsys.numberMods, axis=0)
        # reshape modules to align with Istring, reshape takes array-like
        # and it concatenates from outside in - EG: [[row 1]+[row2]+...]
        # the opposite of MATLAB; use 1-D to return iterable of pvmod's,
        # instead of 2-D which returns iterable of array(pvmod)'s
        pvmods = np.reshape(pvsys.pvmods, (pvsys.numberStrs *
                                           pvsys.numberMods, ))
        Vstring = pool.map(interpMods, zip(pvmods, Imodstr),
                           chunksize)
        # reshape Vstring to reorganize mods in each string
        # IE (<numberStrs>, <numberMods>, <npts>)
        Vstring = np.reshape(Vstring, (pvsys.numberStrs, pvsys.numberMods,
                                       2 * pvsys.pvconst.npts))
        # add up voltages from each mod to get Vstring
        # NOTE: str: 0th dim, mod: 1st dim, npts: 2nd dim 
        Vstring = np.sum(Vstring, axis=1)
    Pstring = Istring * Vstring
    for (pvstr, P, I, V) in zip(pvsys.pvstrs, Pstring, Istring, Vstring):
        pvstr.Pstring, pvstr.Istring, pvstr.Vstring = P, I, V
    # only use pool if more than one string
    if pvsys.numberStrs == 1:
        Isys = interpString((Vstring, Istring), Vsys)
    else:
        partial_interpString = partial(interpString, Vsys=Vsys)
        update = zip(Vstring, Istring)
        Isys = pool.map(partial_interpString, update,
                        chunksize)
        Isys = np.sum(Isys, axis=0)
    pool.close()
    pool.join()
    # np.sum takes array-like, Isys is already in (<numberStrs>, <npts>, 1)
    # summation along 0th dim reduces shape to (<npts>, 1)
    return Isys


def calcIstring(Istring_args, Imod_pts, Imod_negpts):
    """
    Calculate Istring appropriate to interpolate Vmod.
    :param args: min Imod, max Imod and mean Ee for all modules in each string.
    :returns: Istring
    :rtype: {float, ndarray (PVconstants.npts 1)}
    """
    Isc = Istring_args[2]
    Imax = (Istring_args[1] - Isc) * Imod_pts + Isc
    Ineg = (Istring_args[0] - Isc) * Imod_negpts + Isc
    return np.concatenate((Ineg, Imax), axis=0)


def interpMods((pvmod, Istring)):
    """
    Interpolate Vmod from Istring.
    :param pvmod: A PVmodule class instance.
    :type pvstr: :class:`PVmodule`
    :returns: Vmod at Istring
    :rtype: {float, ndarray (1 PVconstants.npts)}
    """
    xp = pvmod.Imod.flatten()
    fp = pvmod.Vmod.flatten()
    return npinterpx(Istring, xp, fp)


def interpString((Vstring, Istring), Vsys):
    """
    Interpolate Istring from Vsys.
    :param pvstr: A PVstring class instance.
    :type pvstr: :class:`PVstring`
    :returns: Istring at Vsys
    :rtype: {float, ndarray (PVconstants.npts, 1)}
    """
    xp = np.flipud(Vstring.flatten())
    fp = np.flipud(Istring.flatten())
    return npinterpx(Vsys, xp, fp)


def parallel_calcMod(pvmod):
    # protect main thread
    if current_process().name != 'MainProcess':
        raise PVparallel_calcError(__name__)
    # pool overhead is high, create once and reuse processes
    pool = Pool(processes=pvmod.pvconst.procs,
                maxtasksperchild=pvmod.pvconst.maxtasksperchild)
    partial_calcIatVrbd = partial(calcIatVrbd, VRBD=pvmod.pvconst.VRBD)
    IatVrbd = pool.map(partial_calcIatVrbd, zip(pvmod.Vcell.T, pvmod.Icell.T),
                       pvmod.pvconst.chunksize)
    Isc = np.mean(pvmod.Ee) * pvmod.pvconst.Isc0
    Imax = (np.max(IatVrbd) - Isc) * pvmod.pvconst.Imod_pts + Isc # max current
    Imin = np.min(pvmod.Icell)
    Imin = Imin if Imin < 0 else 0
    Ineg = (Imin - Isc) * pvmod.pvconst.Imod_negpts + Isc  # min current
    Imod = np.concatenate((Ineg, Imax), axis=0)  # interpolation range
    Vsubstr = np.zeros((2 * pvmod.pvconst.npts, 3))
    start = np.cumsum(pvmod.subStrCells) - pvmod.subStrCells
    stop = np.cumsum(pvmod.subStrCells)
    partial_interpVsubstrcells = partial(interpVsubstrcells,Imod=Imod)
    for substr in range(pvmod.numSubStr):
        cells = range(start[substr], stop[substr])
        Vsubstrcells = pool.map(partial_interpVsubstrcells,
                                zip(pvmod.Icell[:, cells].T,
                                    pvmod.Vcell[:, cells].T),
                                pvmod.pvconst.chunksize)
        Vsubstrcells = np.sum(Vsubstrcells, axis=0)
        Vsubstr[:, substr] = Vsubstrcells.flatten()
    bypassed = Vsubstr < pvmod.pvconst.Vbypass
    Vsubstr[bypassed] = pvmod.pvconst.Vbypass
    Vmod = np.sum(Vsubstr, 1).reshape(2 * pvmod.pvconst.npts, 1)
    Pmod = Imod * Vmod
    pool.close()
    pool.join()
    return (Imod, Vmod, Pmod, Vsubstr)


def calcIatVrbd((Vcell, Icell), VRBD):
    return np.interp(VRBD, Vcell, Icell)


def interpVsubstrcells((Icell, Vcell), Imod):
    xp = np.flipud(Icell)
    fp = np.flipud(Vcell)
    return npinterpx(Imod, xp, fp)


def parallel_calcString():
    pass
#     pool.map()
