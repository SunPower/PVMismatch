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
