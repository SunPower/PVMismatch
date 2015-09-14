"""
Test pvcells.
"""

from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvcell import PVcell
import numpy as np


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
