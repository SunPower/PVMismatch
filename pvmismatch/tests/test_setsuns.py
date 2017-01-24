"""
Test for setSuns method.

Bennet Meyers 10/10/16
"""

import numpy as np
from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvsystem import PVsystem


def test_basic():
    pvsys = PVsystem()
    pvsys.setSuns(.75)
    ok_(np.isclose(pvsys.Pmp, 23907.936630685774))


def test_dictionary():
    pvsys = PVsystem()
    Ee = {1: {3: {'cells': np.arange(30), 'Ee': [.25] * 30}}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 31618.1813179655))


def test_set_mod_1():
    pvsys = PVsystem()
    Ee = {1: {3: [.2], 0: [.1]}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29566.303088387336))


def test_set_mod_2():
    pvsys = PVsystem()
    Ee = {1: {3: .2, 0: .1}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29566.303088387336))


def test_set_str_1():
    pvsys = PVsystem()
    Ee = {1: [.1]}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29136.544447716446))


def test_set_str_2():
    pvsys = PVsystem()
    Ee = {1: .1}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29136.544447716446))


def test_gh34_35():
    pvsys = PVsystem()
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    pvsys.setSuns({2: 0.88})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvmods[2][0].pvcells[0] == pvsys.pvmods[2][2].pvcells[2]
    pvsys.setSuns({2: {4: 0.75}})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[4].Ee == 0.75).all()
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    pvsys.setSuns({2: {4: {'Ee': 0.66, 'cells': [0, 2]}}})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Ee == 0.66
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Ee == 0.75
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Ee == 0.66
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]

