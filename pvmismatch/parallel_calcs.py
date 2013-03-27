# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:49:04 2013

@author: mmikofski
"""

from multiprocessing import current_process, Pool
from pvmismatch.pvconstants import npinterpx
from pvmismatch.pvexceptions import PVparallel_calcError
import numpy as np


def parallel_calcSystem(pvsys):
    # protect main thread
    if current_process().name != 'MainProcess':
        raise PVparallel_calcError(__name__)
    pool = Pool(processes=pvsys.pvconst.procs,
                maxtasksperchild=pvsys.pvconst.maxtasksperchild)
    calcMaxEe_map = pool.map(calcMaxEe, pvsys.pvstrs, pvsys.pvconst.chunksize)
    (maxEe, proc) = zip(*calcMaxEe_map)
    Imax = np.array(maxEe) * pvsys.pvconst.Isc0
    Istring = Imax.reshape(1, pvsys.numberStrs,1) * pvstr.pvconst.pts
    Ineg = np.linspace(-Imax, -1 / float(pvstr.pvconst.npts),
                       pvstr.pvconst.npts).reshape(pvstr.pvconst.npts, 1)
    Istring = np.concatenate((Ineg, Istring), axis=0)
    Vstring = np.zeros((2 * pvsys.pvconst.npts, pvsys.numberStrs))
    
    
    imap_unordered_it, elaps_time = startpool(calcSystem, pvsys.pvstrs)


def parallel_calcString(pvsys):
    startpool()


def parallel_calcMod(pvsys):
    startpool()


def parallel_setSuns(pvsys):
    startpool()


def calcMaxEe(pvstr):
    # scale with max irradiance, so that Ee > 1 is not a problem
    maxEe = np.max([pvmod.Ee for pvmod in pvstr.pvmods])
    return (maxEe, current_process().name)


def calcSystem(pvsys):
    Isys = np.zeros((pvsys.pvconst.npts, 1))
    Vmax = np.max([pvstr.Vstring for pvstr in pvsys.pvstrs])
    Vsys = Vmax * pvsys.pvconst.pts
    if pvsys.pvconst.parallel:
        Isys = parallel_calcSystem(pvsys)
    else:
        for pvstr in pvsys.pvstrs:
            (pvstr.Istring,
             pvstr.Vstring,
             pvstr.Pstring) = pvstr.calcString()
            xp = np.flipud(pvstr.Vstring.squeeze())
            fp = np.flipud(pvstr.Istring.squeeze())
            Isys += npinterpx(Vsys, xp, fp)
    Psys = Isys * Vsys
    return (Isys, Vsys, Psys)


def calcString(pvstr):
    # scale with max irradiance, so that Ee > 1 is not a problem
    Ee = [pvmod.Ee for pvmod in pvstr.pvmods]
    Imax = np.max(Ee) * pvstr.pvconst.Isc0
    Istring = Imax * pvstr.pvconst.pts
    Ineg = np.linspace(-Imax, -1 / float(pvstr.pvconst.npts),
                       pvstr.pvconst.npts).reshape(pvstr.pvconst.npts, 1)
    Istring = np.concatenate((Ineg, Istring), axis=0)
    Vstring = np.zeros((2 * pvstr.pvconst.npts, 1))
    for mod in pvstr.pvmods:
        xp = mod.Imod.squeeze()
        fp = mod.Vmod.squeeze()
        Vstring += npinterpx(Istring, xp, fp)
    Pstring = Istring * Vstring
    return (Istring, Vstring, Pstring)
