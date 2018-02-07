"""
Test for setTemps method.

Bennet Meyers 2/2/17
"""

import numpy as np
from nose.tools import ok_
from pvmismatch.pvmismatch_lib.pvsystem import PVsystem
from pvmismatch.pvmismatch_lib.pvcell import PVcell
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def test_settemp():
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
    pvsys.setTemps({2: 373})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    # test other string not changed
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 298.15).all()
    # test all modules in string #2 changed
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    # test strings references same object
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    # modules references same object
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    # cells reference same object
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvmods[2][0].pvcells[0] == pvsys.pvmods[2][2].pvcells[2]

    # test set suns on just module #4 in string #2
    pvsys.setTemps({2: {4: 300}})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[4].Tcell == 298.15).all()
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[4].Tcell == 300).all()
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]

    # set just cells #0 and #2 in module #4 in string #2
    pvsys.setTemps({2: {4: {'Tc': 290, 'cells': [0, 2]}}})
    # display unique id numbers
    LOGGER.debug('pvstrs:\n%r', set(pvsys.pvstrs))
    LOGGER.debug('pvmods:\n%r', set([x for y in pvsys.pvmods for x in y]))
    LOGGER.debug(
        'pvcells:\n%r',
        {hex(int(id(z))): z for y in pvsys.pvmods for x in y for z in x.pvcells}
    )
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[4].Tcell == 298.15).all()
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Tcell == 290
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Tcell == 300
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Tcell == 290
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]

    # set cells 3 and 4 to one irradiance and 5 to another. should only make two new cell objects
    pvsys.setTemps({2: {4: {'Tc': (310, 320, 310), 'cells': (3, 4, 5)}}})
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[4].Tcell == 298.15).all()
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Tcell == 290
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Tcell == 300
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Tcell == 290
    assert pvsys.pvstrs[0] == pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] == pvsys.pvmods[1][1]
    assert pvsys.pvmods[0][0].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Tcell == 320
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]

    # set all of a string with a single value, two ways. make sure no unnecessary modules are created
    pvsys.setTemps({1: 350})
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 350).all()
    assert (pvsys.pvstrs[1].pvmods[4].Tcell == 350).all()
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Tcell == 290
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Tcell == 300
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Tcell == 290
    assert pvsys.pvstrs[0] != pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] != pvsys.pvmods[1][1]
    assert pvsys.pvmods[1][2].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Tcell == 320
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]
    assert pvsys.pvstrs[1].pvmods[0] == pvsys.pvstrs[1].pvmods[2]

    pvsys.setTemps({1: [360]})
    assert (pvsys.pvstrs[0].pvmods[0].Tcell == 298.15).all()
    assert (pvsys.pvstrs[1].pvmods[1].Tcell == 360).all()
    assert (pvsys.pvstrs[1].pvmods[4].Tcell == 360).all()
    assert (pvsys.pvstrs[2].pvmods[0].Tcell == 373).all()
    assert (pvsys.pvstrs[2].pvmods[2].Tcell == 373).all()
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0].Tcell == 290
    assert pvsys.pvstrs[2].pvmods[4].pvcells[1].Tcell == 300
    assert pvsys.pvstrs[2].pvmods[4].pvcells[2].Tcell == 290
    assert pvsys.pvstrs[0] != pvsys.pvstrs[1]
    assert pvsys.pvmods[0][0] != pvsys.pvmods[1][1]
    assert pvsys.pvmods[1][2].pvcells[0] == pvsys.pvmods[1][1].pvcells[1]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[0] == pvsys.pvstrs[2].pvmods[4].pvcells[2]
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[4].Tcell == 320
    assert pvsys.pvstrs[2].pvmods[4].pvcells[5].Tcell == 310
    assert pvsys.pvstrs[2].pvmods[4].pvcells[3] == pvsys.pvstrs[2].pvmods[4].pvcells[5]
    assert pvsys.pvstrs[1].pvmods[0] == pvsys.pvstrs[1].pvmods[2]

def test_settemp_cell():
    """
    Test setTemp method for a wide range of temperatures. 
    Test added after implementing Isat2 as Isat2(Tcell)
    """
    pvc = PVcell()
    Pmp_arr = []
    Vmp_arr = []
    Voc_arr = []
    Isc_arr = []
    
    temps = [-85, -60, -40, -25, 0, 25, 40, 60, 85]
    for t in temps:
        pvc.Tcell = float(t) + 273.15
        Pmp_arr.append(pvc.Pcell.max())
        Vmp_arr.append(pvc.Vcell[pvc.Pcell.argmax()])
        Voc_arr.append(pvc.calcVcell(0))
        Isc_arr.append(pvc.Isc)
        
    assert(np.all(np.gradient(np.squeeze(Vmp_arr)) < 0))
    assert(np.all(np.gradient(np.squeeze(Voc_arr)) < 0))
    assert(np.all(np.gradient(Isc_arr) > 0))
        
