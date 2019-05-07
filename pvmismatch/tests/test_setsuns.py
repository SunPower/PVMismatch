"""
Test for setSuns method.

Bennet Meyers 10/10/16
"""

import numpy as np
from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvsystem import PVsystem
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def test_basic():
    pvsys = PVsystem()
    pvsys.setSuns(.75)
    ok_(np.isclose(pvsys.Pmp, 23901.66450809984))


def test_dictionary():
    pvsys = PVsystem()
    Ee = {1: {3: {'cells': np.arange(30), 'Ee': [.25] * 30}}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 31610.641289630337))


def test_set_mod_1():
    pvsys = PVsystem()
    Ee = {1: {3: [.2], 0: [.1]}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29555.687509091586))


def test_set_mod_2():
    pvsys = PVsystem()
    Ee = {1: {3: .2, 0: .1}}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29555.687509091586))
    # 1001 points linear: [ 29579.12191565]


def test_set_str_1():
    pvsys = PVsystem()
    Ee = {1: [.1]}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29131.92967897601))
    # 1001 points linear: [ 29141.73034719]


def test_set_str_2():
    pvsys = PVsystem()
    Ee = {1: .1}
    pvsys.setSuns(Ee)
    ok_(np.isclose(pvsys.Pmp, 29131.92967897601))
    # 1001 points linear: [ 29141.73034719]


def test_gh34_35():
    pvsys = PVsystem()
    # display unique id numbers
    LOGGER.debug('\n*** unique id numbers ***')
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    # test strings references same object
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    # modules references same object
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    # cells reference same object
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]

    # test set suns on just string #2
    pvsys.setSuns({2: 0.88})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    # test other string not changed
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    # test all modules in string #2 changed
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    # test strings references same object
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    # modules references same object
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    # cells reference same object
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvmods[2][0].pvcells[0] == pvsys.pvmods[2][2].pvcells[2]

    # test set suns on just module #4 in string #2
    pvsys.setSuns({2: {4: 0.75}})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[4].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[4].Ee == 0.75).all()
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]

    # set just cells #0 and #2 in module #4 in string #2
    pvsys.setSuns({2: {4: {'Ee': 0.66, 'cells': [0, 2]}}})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[4].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Ee == 0.66
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Ee == 0.75
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Ee == 0.66
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]

    # set cells 3 and 4 to one irradiance and 5 to another. should only make two new cell objects
    pvsys.setSuns({2: {4: {'Ee': (0.33, 0.99, 0.33), 'cells': (3, 4, 5)}}})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[4].Ee == 1.0).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Ee == 0.66
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Ee == 0.75
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Ee == 0.66
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Ee == 0.99
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]

    # set all of a string with a single value, two ways. make sure no unnecessary modules are created
    pvsys.setSuns({1: 0.5})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 0.5).all()
    assert (pvsys.pvstrs[1].pvmods[4].Ee == 0.5).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Ee == 0.66
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Ee == 0.75
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Ee == 0.66
    assert pvsys.pvstrs[0] != pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] != pvsys.pvmods[1][1]
    assert pvsys.pvmods[1][2].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Ee == 0.99
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]
    assert pvsys.pvstrs[1].pvmods[0] == pvsys.pvstrs[1].pvmods[2]

    pvsys.setSuns({1: [0.6]})
    assert (pvsys.pvstrs[0].pvmods[0].Ee == 1.0).all()
    assert (pvsys.pvstrs[1].pvmods[1].Ee == 0.6).all()
    assert (pvsys.pvstrs[1].pvmods[4].Ee == 0.6).all()
    assert (pvsys.pvstrs[2].pvmods[0].Ee == 0.88).all()
    assert (pvsys.pvstrs[2].pvmods[2].Ee == 0.88).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Ee == 0.66
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Ee == 0.75
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Ee == 0.66
    assert pvsys.pvstrs[0] != pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] != pvsys.pvmods[1][1]
    assert pvsys.pvmods[1][2].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Ee == 0.99
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Ee == 0.33
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]
    assert pvsys.pvstrs[1].pvmods[0] == pvsys.pvstrs[1].pvmods[2]
