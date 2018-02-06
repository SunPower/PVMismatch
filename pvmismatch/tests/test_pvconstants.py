from pvmismatch import *


def test_pvconst_npts_setter():
    """Test pvconst property and setter methods"""
    pvconst = pvconstants.PVconstants()
    assert pvconst.npts == pvconstants.NPTS
    assert len(pvconst.pts) == pvconst.npts
    assert pvconst.pts[0] == 0
    assert pvconst.pts[-1] == 1
    assert len(pvconst.negpts) == pvconst.npts
    assert pvconst.negpts[0] == 1
    assert pvconst.negpts[-1] > 0
    pvconst.npts = 1001
    assert pvconst.npts == 1001
    assert len(pvconst.pts) == pvconst.npts
    assert pvconst.pts[0] == 0
    assert pvconst.pts[-1] == 1
    assert len(pvconst.negpts) == pvconst.npts
    assert pvconst.negpts[0] == 1
    assert pvconst.negpts[-1] > 0
