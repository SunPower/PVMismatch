"""
Tests for pvmodules.
"""

from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule, TCT96, PCT96
import numpy as np
from copy import copy


def test_calc_mod():
    pvmod = PVmodule()
    ok_(isinstance(pvmod, PVmodule))
    return pvmod


def test_calc_tct_mod():
    pvmod = PVmodule(cell_pos=TCT96)
    isc = np.interp(np.float64(0), pvmod.Vmod, pvmod.Imod)
    voc = np.interp(np.float64(0), np.flipud(pvmod.Imod), np.flipud(pvmod.Vmod))
    ok_(np.isclose(isc, 50.444797602637614))
    ok_(np.isclose(voc, 8.089732058317182))
    return pvmod


def test_calc_pct_mod():
    pvmod = PVmodule(cell_pos=PCT96)
    isc = np.interp(np.float64(0), pvmod.Vmod, pvmod.Imod)
    voc = np.interp(np.float64(0), np.flipud(pvmod.Imod), np.flipud(pvmod.Vmod))
    ok_(np.isclose(isc, 50.444797602637614))
    ok_(np.isclose(voc, 8.089732058317182))
    return pvmod


def test_calc_pct_bridges():
    pct96_bridges = copy(PCT96)
    pct96_bridges[0][0][2]['circuit'] = 'parallel'
    pct96_bridges[0][2][2]['circuit'] = 'parallel'
    pct96_bridges[0][4][2]['circuit'] = 'parallel'
    pct96_bridges[0][6][2]['circuit'] = 'parallel'
    pvmod = PVmodule(cell_pos=pct96_bridges)
    return pvmod

if __name__ == "__main__":
    test_calc_mod()
    test_calc_tct_mod()
    test_calc_pct_mod()
    test_calc_pct_bridges()
