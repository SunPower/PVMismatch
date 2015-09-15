"""
Tests for pvmodules.
"""

from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule, TCT96, PCT96


def test_calc_mod():
    pvmod = PVmodule()
    ok_(isinstance(pvmod, PVmodule))
    return pvmod


def test_calc_TCT_mod():
    pvmod = PVmodule(cell_pos=TCT96)
    ok_(isinstance(pvmod, PVmodule))
    return pvmod


def test_calc_PCT_mod():
    pvmod = PVmodule(cell_pos=PCT96)
    ok_(isinstance(pvmod, PVmodule))
    return pvmod


if __name__ == "__main__":
    test_calc_mod()
    test_calc_TCT_mod()
