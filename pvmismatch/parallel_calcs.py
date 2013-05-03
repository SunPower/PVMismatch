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
    # can't use lambda, must be pickle-able, lamnda can't be pickled
    Istring = pool.map(calcIstring, pvsys.pvstrs, pvsys.pvconst.chunksize)
    Istring = np.array(Istring).squeeze()
    # expand Istring for every module in each string
    # convert Istring and pvmods into nice iterables
    Imodstr = Istring.repeat(pvsys.numberMods, axis=0).tolist()
    pvmods = np.array(pvsys.pvmods).reshape(pvsys.numberStrs *
                                            pvsys.numberMods, )
    Vstring = pool.map(interpMods, zip(pvmods, Imodstr),
                       pvsys.pvconst.chunksize)
    Vstring = np.array(Vstring).reshape(pvsys.numberStrs, pvsys.numberMods,
                                        2 * pvsys.pvconst.npts)
    Vstring = np.sum(Vstring, axis=1)
    Pstring = Istring * Vstring
    Vsys = Vsys.T.repeat(pvsys.numberStrs, axis=0).squeeze()
    update = zip(pvsys.pvstrs, Pstring, Istring, Vstring, Vsys)
    Isys = pool.map(updateInterp_pvstr, update, pvsys.pvconst.chunksize)
    pool.close()
    pool.join()
    return np.sum(np.array(Isys), axis=0).reshape(pvsys.pvconst.npts, 1)


def calcIstring(pvstr):
    # Imod is already set to the range from Vrbd to the minimum current
    zipped = zip(*[(pvmod.Imod[0], pvmod.Imod[-1], np.mean(pvmod.Ee)) for
                   pvmod in pvstr.pvmods])
    Isc = np.mean(zipped[2])
    Imax = (np.max(zipped[1]) - Isc) * pvstr.pvconst.Imod_pts + Isc  # max current
    Ineg = (np.min(zipped[0]) - Isc) * pvstr.pvconst.Imod_negpts + Isc  # min current
    Istring = np.concatenate((Ineg, Imax), axis=0)
    return Istring


def interpMods((pvmod, Istring)):
    xp = pvmod.Imod.squeeze()
    fp = pvmod.Vmod.squeeze()
    return npinterpx(np.array(Istring), xp, fp)


def updateInterp_pvstr((pvstr, P, I, V, Vsys)):
    pvstr.Pstring, pvstr.Istring, pvstr.Vstring = P, I, V
    xp = np.flipud(pvstr.Vstring.squeeze())
    fp = np.flipud(pvstr.Istring.squeeze())
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
                                zip(pvmod.Icell[:, cells],
                                    pvmod.Icell[:, cells]),
                                pvmod.pvconst.chunksize)
        Vsubstr[: substr] = np.sum(Vsubstrcells, axis=1)
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
