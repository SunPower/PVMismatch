# -*- coding: utf-8 -*-

"""
Created on Tue Mar 26 13:49:04 2013

@author: mmikofski
"""

from functools import partial
import numpy as np
from multiprocessing import current_process, Pool, cpu_count
from pvmismatch.pvmismatch_lib.pvconstants import npinterpx
from pvmismatch.pvmismatch_lib.pvexceptions import PVparallel_calcError


def parallel_calcSystem(pvsys, Vsys):
    """
    Embarrassingly parallel calculations.
    """

    # protect main thread
    if current_process().name != 'MainProcess':
        raise PVparallel_calcError(__name__)
    # pool overhead is high, create once and reuse processes
    # if procs is None, set it cpu_count - 2, so 2 cores are free
    procs = pvsys.pvconst.procs
    if not procs:
        procs = max(cpu_count() - 2, 1)
    pool = Pool(processes=procs,
                maxtasksperchild=pvsys.pvconst.maxtasksperchild)
    # if chunksize is None, then divide tasks evenly between all procs
    tot_mods = pvsys.numberStrs * pvsys.numberMods
    chunksize = pvsys.pvconst.chunksize
    if not chunksize:
        chunksize = max(tot_mods / procs, 1)
    # limit data pickled and sent to process to reduce overhead
    # flatten pvmods to 1-D
    pvmods = np.reshape(pvsys.pvmods, (tot_mods, ))
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
        Istring = np.squeeze(pool.map(partial_calcIstring, Istring_args,
                                      chunksize))
        # squeeze take array-like, removes singleton dimensions
        # converts (<numberStrs>, <npts>, 1) to (<numberStrs>, <npts>)
    # only use pool if more than one module
    if tot_mods == 1:
        Vstring = interpMods(np.squeeze([pvsys.pvmods[0][0].Imod.T,
                                         pvsys.pvmods[0][0].Vmod.T, Istring]))
    else:
        # expand Istring for every module in each string
        # repeat is smart - it repeats the each row <repeats> times,
        # so each string is kept together [[str1-mod1],...,[str2-mod1],...]
        Imodstr = Istring.repeat(pvsys.numberMods,
                                 axis=0).reshape(tot_mods, 1,
                                                 2 * pvsys.pvconst.npts)
        IVmods = np.array([(pvmod.Imod, pvmod.Vmod) for pvmod in pvmods],
                          dtype=float).reshape(tot_mods, 2,
                                               2 * pvsys.pvconst.npts)
        Vstring_args = np.append(IVmods, Imodstr, 1)
        Vstring = np.sum(np.reshape(pool.map(interpMods, Vstring_args,
                                             chunksize),
                                    (pvsys.numberStrs, pvsys.numberMods,
                                     2 * pvsys.pvconst.npts)), axis=1)
        # reshape Vstring to reorganize mods in each string
        # IE (<numberStrs>, <numberMods>, <npts>)
        # add up voltages from each mod to get Vstring
        # NOTE: str: 0th dim, mod: 1st dim, npts: 2nd dim
    Pstring = Istring * Vstring
    for (pvstr, P, I, V) in zip(pvsys.pvstrs, Pstring, Istring, Vstring):
        pvstr.Pstring, pvstr.Istring, pvstr.Vstring = P, I, V
    # only use pool if more than one string
    if pvsys.numberStrs == 1:
        Isys = interpString((Vstring, Istring), Vsys)
    else:
        partial_interpString = partial(interpString, Vsys=Vsys)
        Isys = pool.map(partial_interpString, zip(Vstring, Istring),
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


def interpMods(Vstring_arg):
    """
    Interpolate Vmod from Istring.
    :param pvmod: A PVmodule class instance.
    :type pvstr: :class:`PVmodule`
    :returns: Vmod at Istring
    :rtype: {float, ndarray (1 PVconstants.npts)}
    """
    xp = Vstring_arg[0].flatten()
    fp = Vstring_arg[1].flatten()
    return npinterpx(Vstring_arg[2], xp, fp)


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

    procs = pvmod.pvconst.procs
    if not procs:
        procs = max(cpu_count() - 2, 1)
    pool = Pool(processes=procs,
                maxtasksperchild=pvmod.pvconst.maxtasksperchild)
    # if chunksize is None, then divide tasks evenly between all procs
    chunksize = pvmod.pvconst.chunksize
    if not chunksize:
        chunksize = max(pvmod.numberCells / procs, 1)
    # create partial funcion with VRBD constant
    partial_calcIatVrbd = partial(calcIatVrbd, VRBD=pvmod.pvconst.VRBD)
    # calculate I at VRBD for every cell
    IatVrbd = pool.map(partial_calcIatVrbd, zip(pvmod.Vcell.T, pvmod.Icell.T),
                       chunksize)
    Isc = np.mean(pvmod.Ee) * pvmod.pvconst.Isc0
    Imax = (np.max(IatVrbd) - Isc) * pvmod.pvconst.Imod_pts + Isc  # Imax
    Imin = np.min(pvmod.Icell)
    Imin = Imin if Imin < 0 else 0
    Ineg = (Imin - Isc) * pvmod.pvconst.Imod_negpts + Isc  # min current
    Imod = np.concatenate((Ineg, Imax), axis=0)  # interpolation range
    Vsubstr = np.zeros((2 * pvmod.pvconst.npts, 3))
    start = np.cumsum(pvmod.subStrCells) - pvmod.subStrCells
    stop = np.cumsum(pvmod.subStrCells)
    # partial with Imod constant
    partial_interpVsubstrcells = partial(interpVsubstrcells, Imod=Imod)
    # interpolate cell voltages
    Vsubstrcells = np.squeeze(pool.map(partial_interpVsubstrcells,
                              zip(pvmod.Icell.T, pvmod.Vcell.T), chunksize))
    # loop over substrings
    for substr in range(pvmod.numSubStr):
        cells = range(start[substr], stop[substr])
        # calculate substring voltages
        Vsubstr[:, substr] = np.sum(Vsubstrcells[cells][:], axis=0).flatten()
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
