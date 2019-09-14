from pvmismatch import *
import os
import numpy as np


BASEDIR = os.path.dirname(__file__)


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


def test_minimum_current_close_to_max_voc_gh110():
    """
    Tests that minimum current in ``calcSeries`` is reasonably close to the
    maximum open circuit current of all cells in module. This came up in GitHub
    issue 110 that the resolution of the plots, and hence the underlying data,
    at high cell temperature was too coarse.
    """
    pvsys = pvsystem.PVsystem()
    pvsys.setTemps(388)
    expected = np.loadtxt(os.path.join(BASEDIR, 'gh110.dat'))
    calculated = np.concatenate(
        [[pvsys.Isys], [pvsys.Vsys], [pvsys.Psys]], axis=0).T
    assert np.allclose(expected, calculated)
    return calculated


if __name__ == '__main__':
    calculated = test_minimum_current_close_to_max_voc_gh110()
    np.savetxt(os.path.join(BASEDIR, 'gh110.dat'), calculated)