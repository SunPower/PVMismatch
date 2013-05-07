# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:49:04 2013

@author: mmikofski
"""

from functools import partial
from multiprocessing import current_process, Pool
from pvmismatch.pvconstants import npinterpx
from pvmismatch.pvexceptions import PVparallel_calcError
import numpy as np


def parallel_calcSystem(pvsys, Vsys):
    # protect main thread
    if current_process().name != 'MainProcess':
        raise PVparallel_calcError(__name__)
    # pool overhead is high, create once and reuse processes
    pool = Pool(processes=pvsys.pvconst.procs,
                maxtasksperchild=pvsys.pvconst.maxtasksperchild)
    # reduce data pickled and sent to process to reduce overhead
    pvmods = np.reshape(pvsys.pvmods, (pvsys.numberStrs * pvsys.numberMods, ))
    zipped = [(pvmod.Imod, pvmod.Vmod, pvmod.Ee) for pvmod in pvmods]
    partial_calcIsys = partial(calcIsys, Vsys=Vsys)
    # TODO: figure out intelligent chunksize
    if not chunksize:
        chunksize = len(zipped)/multiprocessing.cpu_count
    Isys = pool.map(calcIsys, zipped, pvsys.pvconst,chunksize)
    # only use pool if more than one string
    if pvsys.numberStrs == 1:
        # transpose from (<npts>, 1) to (1, <npts>) to match pool.map
        Istring = calcIstring(pvsys.pvstrs[0]).T
    else:
        Istring = pool.map(calcIstring, pvsys.pvstrs, pvsys.pvconst.chunksize)
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
                           pvsys.pvconst.chunksize)
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
                        pvsys.pvconst.chunksize)
        Isys = np.sum(Isys, axis=0)
    pool.close()
    pool.join()
    # np.sum takes array-like, Isys is already in (<numberStrs>, <npts>, 1)
    # summation along 0th dim reduces shape to (<npts>, 1)
    return Isys


def calcIsys(zipped,Vsys):
    """
    Embarrassingly parallel calculation.
    """
    unzipped = zip(*zipped)
    Imod = unzipped[0]
    Vmod = unzipped[1]
    Ee = unzipped[2]
    Isc = np.mean(zipped[2])
    Imax = (np.max(zipped[1]) - Isc) * pvstr.pvconst.Imod_pts + Isc  # max current
    Ineg = (np.min(zipped[0]) - Isc) * pvstr.pvconst.Imod_negpts + Isc  # min current
    Istring = np.concatenate((Ineg, Imax), axis=0)


def calcIstring(pvstr):
    """
    Calculate Istring appropriate to interpolate Vmod.
    :param pvstr: A PVstring class instance.
    :type pvstr: :class:`PVstring`
    :returns: Istring
    :rtype: {float, ndarray (PVconstants.npts 1)}
    """
    # Imod is already set to the range from Vrbd to the minimum current
    zipped = zip(*[(pvmod.Imod[0], pvmod.Imod[-1], np.mean(pvmod.Ee)) for
                   pvmod in pvstr.pvmods])
    Isc = np.mean(zipped[2])
    Imax = (np.max(zipped[1]) - Isc) * pvstr.pvconst.Imod_pts + Isc  # max current
    Ineg = (np.min(zipped[0]) - Isc) * pvstr.pvconst.Imod_negpts + Isc  # min current
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
