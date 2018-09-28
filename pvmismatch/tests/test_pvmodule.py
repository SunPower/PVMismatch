"""
Tests for pvmodules.
"""
import pytest
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule, TCT492, PCT492
from pvmismatch.pvmismatch_lib.pvcell import PVcell
import numpy as np
from copy import copy

def test_calc_mod():
    pvmod = PVmodule()
    assert (isinstance(pvmod, PVmodule))
    return pvmod

def test_calc_tct_mod():
    pvmod = PVmodule(cell_pos=TCT492)
    isc = np.interp(np.float64(0), pvmod.Vmod, pvmod.Imod)
    voc = np.interp(np.float64(0), np.flipud(pvmod.Imod), np.flipud(pvmod.Vmod))
    assert (np.isclose(isc, 37.8335982026))
    assert (np.isclose(voc, 55.2798357318))
    return pvmod

def test_calc_pct_mod():
    pvmod = PVmodule(cell_pos=PCT492)
    isc = np.interp(np.float64(0), pvmod.Vmod, pvmod.Imod)
    voc = np.interp(np.float64(0), np.flipud(pvmod.Imod), np.flipud(pvmod.Vmod))
    assert (np.isclose(isc, 37.8335982026))
    assert (np.isclose(voc, 55.2798357318))
    return pvmod

def test_calc_pct_bridges():
    pct492_bridges = copy(PCT492)
    pct492_bridges[0][0][2]['crosstie'] = True
    pct492_bridges[0][2][2]['crosstie'] = True
    pct492_bridges[0][4][2]['crosstie'] = True
    pvmod = PVmodule(cell_pos=pct492_bridges)
    return pvmod

def check_same_pvconst_and_lengths(pvmod):
    assert len(pvmod.pvcells) == 96
    for p in pvmod.pvcells:
        assert p.pvconst is pvmod.pvconst

def test_pvmodule_with_pvcells_list():
    pvcells = [PVcell()] * 96
    pvmod = PVmodule(pvcells=pvcells)
    check_same_pvconst_and_lengths(pvmod)

def test_pvmodule_with_pvcells_obj():
    pvcells = PVcell()
    pvmod = PVmodule(pvcells=pvcells)
    check_same_pvconst_and_lengths(pvmod)

def test_pvmodule_with_no_pvcells():
    pvmod = PVmodule()
    check_same_pvconst_and_lengths(pvmod)

def test_bypass_diode_configurations():
    # No bypass diodes
    pvm = PVmodule(Vbypass = [None, None, None])
    assert (np.isclose(pvm.Vmod.min(), -530.6169665707829))
        
    # only one cell string has a bypass diode
    pvm = PVmodule(Vbypass = [None, None,-0.5])
    assert (np.isclose(pvm.Vmod.min(), -398.46272492808714))
    
    # two bypass diodes (middle removed)
    pvm = PVmodule(Vbypass = [-0.5, None,-0.5])
    assert (np.isclose(pvm.Vmod.min(), -266.30848328539145))

    # all bypass diodes - same values
    pvm = PVmodule(Vbypass = -0.2)
    assert (np.isclose(pvm.Vmod.min(), -0.6))

    # one bypass diode across the module
    pvm = PVmodule(Vbypass = [-0.7])
    assert (np.isclose(pvm.Vmod.min(), -0.7))

    # default case    
    pvm = PVmodule()
    assert (np.isclose(pvm.Vmod.min(), pvm.Vbypass * 3))

if __name__ == "__main__":
    test_calc_mod()
    test_calc_tct_mod()
    test_calc_pct_mod()
    test_calc_pct_bridges()
