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


def test_pvcell_setattr_recalcs_IV():
    pvc = PVcell()
    I183 = pvc.Icell[183]
    pvc.Tcell = 323
    pvc.Ee = 0.65
    ok_(pvc.Icell[183] != I183)


def test_pvcell_calcIcell():
    pvc = PVcell()
    ok_(np.isclose(pvc.Icell[123], pvc.calcIcell(pvc.Vcell[123])))
    ok_(np.isclose(pvc.Icell[153], pvc.calcIcell(pvc.Vcell[153])))
    ok_(np.isclose(pvc.Icell[183], pvc.calcIcell(pvc.Vcell[183])))


def test_pvcell_calcVcell():
    pvc = PVcell()
    ok_(np.isclose(pvc.Vcell[123], pvc.calcVcell(pvc.Icell[123]), 1e-4))
    ok_(np.isclose(pvc.Vcell[153], pvc.calcVcell(pvc.Icell[153])))
    ok_(np.isclose(pvc.Vcell[183], pvc.calcVcell(pvc.Icell[183])))


def test_calc_series():
    pvconst = PVconstants()
    pvcells = []
    pvcells.append(PVcell(pvconst=pvconst, Tcell=323))
    pvcells.append(PVcell(pvconst=pvconst, Ee=0.75, Tcell=313))
    pvcells.append(PVcell(pvconst=pvconst, Ee=0.55, Tcell=303))
    IatVrbd = np.asarray([np.interp(pvc.VRBD, pvc.Vcell.flat, pvc.Icell.flat)
                          for pvc in pvcells])
    Icells = np.asarray([pvc.Icell.flatten() for pvc in pvcells])
    Vcells = np.asarray([pvc.Vcell.flatten() for pvc in pvcells])
    Isc = np.asarray([pvc.Isc for pvc in pvcells])
    i, v = pvconst.calcSeries(Icells, Vcells, Isc.mean(), IatVrbd.max())
    iv = np.loadtxt(os.path.join(BASE_DIR, 'calc_series_test_iv.dat'))
    ok_(np.all(i == iv[0]))
    ok_(np.all(v == iv[1]))
    return i, v


if __name__ == "__main__":
    test_calc_series()
