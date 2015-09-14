"""
Tests for pvmodules.
"""

from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule


def test_calc_mod():
    pvmod = PVmodule()
    ok_(isinstance(pvmod, PVmodule))
    return pvmod


if __name__ == "__main__":
    test_calc_mod()
