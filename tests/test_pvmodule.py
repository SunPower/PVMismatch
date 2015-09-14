"""
Tests for pvmodules.
"""

import os
import numpy as np
from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule

BASE_DIR = os.path.dirname(__file__)


def test_calc_series():
    pvmod = PVmodule()
    ok_(isinstance(pvmod, PVmodule))
    i, v = pvmod.pvconst.calcSeries(pvmod.Icell, pvmod.Vcell, pvmod.Isc,
                                    pvmod.VRBD)
    iv = np.loadtxt(os.path.join(BASE_DIR, 'calc_series_test_iv.dat'))
    ok_(np.all(i == iv[0]))
    ok_(np.all(v == iv[1]))
    return i, v


if __name__ == "__main__":
    test_calc_series()
