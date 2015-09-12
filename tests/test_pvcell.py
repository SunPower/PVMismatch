from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvcell import PVcell


def test_pvcell_basic():
    pvc = PVcell()
    ok_(pvc)
    I183 = pvc.Icell[183]
    pvc.Tcell = 323
    pvc.Ee = 0.65
    ok_(pvc.Icell[183] != I183)
