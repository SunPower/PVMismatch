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
    pool = Pool(processes=pvsys.pvconst.procs,
                maxtasksperchild=pvsys.pvconst.maxtasksperchild)
    # TODO: figure out intelligent chunksize
    chunksize = pvsys.pvconst.chunksize
    if not chunksize:
        chunksize = (len(pvsys.numberStrs * pvsys.numberMods) / cpu_count)
    # reduce data pickled and sent to process to reduce overhead
    pvmods = np.reshape(pvsys.pvmods, (pvsys.numberStrs * pvsys.numberMods, ))
    zipped = [(pvmod.Imod, pvmod.Vmod, pvmod.Ee) for pvmod in pvmods]
    # Imods, Vmods, Ees = zip(*zipped)
    # Imod_extrema = [(Imod[0], Imod[-1]) for Imod in Imods]
    # Ee_mean = [np.mean(Ee) for Ee in Ees]
    Istring_args = np.reshape([(Imod[0], Imod[-1],
                                np.mean(Ee)) for (Imod, _, Ee) in zipped],
                              (pvsys.numberStrs, pvsys.numberMods, 3))
    Istring_args = np.append(np.max(Istring_args[:, :, :2], 1),
                        [np.mean(Istring_args[:, :, -1], 1) *
                         pvsys.pvconst.Isc0], 0).T
    # only use pool if more than one string
    if pvsys.numberStrs == 1:
        # transpose from (<npts>, 1) to (1, <npts>) to match pool.map
        Istring = calcIstring(Istring_args, pvsys.pvconst.Imod_pts,
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


def calcIstring(args, Imod_pts, Imod_negpts):
    """
    Calculate Istring appropriate to interpolate Vmod.
    :param args: A tuple of Imod[0], Imod[-1] and np.mean(Ee) from each module.
    :returns: Istring
    :rtype: {float, ndarray (PVconstants.npts 1)}
    """
    # Imod is already set to the range from Vrbd to the minimum current
    unzipped = zip(*args)
    Isc = np.mean(unzipped[2]) * self.pvconst.Isc0
    Imax = (np.max(unzipped[1]) - Isc) * pvstr.pvconst.Imod_pts + Isc  # max current
    Ineg = (np.min(unzipped[0]) - Isc) * pvstr.pvconst.Imod_negpts + Isc  # min current
    Istring = np.concatenate((Ineg, Imax), axis=0)
    return Istring


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
