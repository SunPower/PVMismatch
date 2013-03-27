# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:49:04 2013

@author: mmikofski
"""

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
                                            pvsys.numberMods, ).tolist()
    Vstring = pool.map(interpMods, zip(pvmods, Imodstr))
    Vstring = np.array(Vstring).reshape(pvsys.numberStrs, pvsys.numberMods)
    Vstring = np.sum(Vstring)
    Pstring = Istring * Vstring
    update = zip(pvsys.pvstrs, Pstring, Istring, Vstring, Vsys)
    return pool.map(updateInterp_pvstr, update, pvsys.pvconst.chunksize)


def calcIstring(pvstr):
    # scale with max irradiance, so that Ee > 1 is not a problem
    Ee = [pvmod.Ee for pvmod in pvstr.pvmods]
    Imax = np.max(Ee) * pvstr.pvconst.Isc0
    Istring = Imax * pvstr.pvconst.pts
    Ineg = -Imax * pvstr.pvconst.negpts
    Istring = np.concatenate((Ineg, Istring), axis=0)
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


def parallel_calcString():
    pass
#     pool.map()


def parallel_calcMod():
    pass
#     pool.map()


def parallel_setSuns():
    pass
#     pool.map()
