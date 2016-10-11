"""
Test pvcells.
"""

from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvcell import PVcell
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)


def test_pvcell_basic():
    """
    test that pvcell returns a :class:`~pvmismatch.pvmismatch_lib.pvcell.PVcell`
    object.
    """
    pvc = PVcell()
    ok_(isinstance(pvc, PVcell))


def test_pvcell_setattr_recalc():
    pvc = PVcell()
    i183 = pvc.Icell[183]
    pvc.Tcell = 323
    pvc.Ee = 0.65
    ok_(pvc.Icell[183] != i183)


def test_pvcell_calc_icell():
    pvc = PVcell()
    ok_(np.isclose(pvc.Icell[123], pvc.calcIcell(pvc.Vcell[123])))
    ok_(np.isclose(pvc.Icell[153], pvc.calcIcell(pvc.Vcell[153])))
    ok_(np.isclose(pvc.Icell[183], pvc.calcIcell(pvc.Vcell[183])))


def test_pvcell_calc_vcell():
    pvc = PVcell()
    ok_(np.isclose(pvc.Vcell[123], pvc.calcVcell(pvc.Icell[123]), 1e-4))
    ok_(np.isclose(pvc.Vcell[153], pvc.calcVcell(pvc.Icell[153])))
    ok_(np.isclose(pvc.Vcell[183], pvc.calcVcell(pvc.Icell[183])))


def test_calc_series():
    pvconst = PVconstants()
    pvcells = [
        PVcell(pvconst=pvconst, Tcell=323),
        PVcell(pvconst=pvconst, Ee=0.75, Tcell=313),
        PVcell(pvconst=pvconst, Ee=0.55, Tcell=303)
    ]
    i_at_vrbd = np.asarray([np.interp(pvc.VRBD, pvc.Vcell.flat, pvc.Icell.flat)
                            for pvc in pvcells])
    icells = np.asarray([pvc.Icell.flatten() for pvc in pvcells])
    vcells = np.asarray([pvc.Vcell.flatten() for pvc in pvcells])
    isc = np.asarray([pvc.Isc for pvc in pvcells])
    i, v = pvconst.calcSeries(icells, vcells, isc.mean(), i_at_vrbd.max())
    iv = np.loadtxt(os.path.join(BASE_DIR, 'calc_series_test_iv.dat'))
    # noinspection PyTypeChecker
    ok_(np.allclose(i, iv[0]))
    # noinspection PyTypeChecker
    ok_(np.allclose(v, iv[1], rtol=1e-4))
    return i, v


def test_pvcell_calc_rbd():
    pvc1 = PVcell(bRBD=0.)
    ok_(isinstance(pvc1, PVcell))
    pvc2 = PVcell(bRBD=-0.056)
    ok_(isinstance(pvc2, PVcell))

        
if __name__ == "__main__":
    test_calc_series()
