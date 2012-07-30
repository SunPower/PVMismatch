# -*- coding: utf-8 -*-
"""
Created on Thu Jun 07 09:44:08 2012

@author: mmikofski
)
"""

#from pvmismatch.pvmodule import PVmodule
#from pvmismatch.pvstring import PVstring
from pvmismatch.pvsystem import PVsystem
import sys
import os
import random
import shutil
import numpy as np


def testPV():
    return PVsystem()

if __name__ == "__main__":
    testPVdir = 'testPV'
    if os.path.isdir(testPVdir):
        print "*** WARNING! Previous 'testPV' directory will be deleted. ***"
        print
        try:
            shutil.rmtree(testPVdir)
        except OSError as e:
            print ("*** ERROR! Please close open pdf file. ***")
            print
            raise e
    os.mkdir(testPVdir)
    print "Creating PVsystem"
    pvsys = testPV()
    Pmp0 = np.max(pvsys.Psys)
    print "max power is {0}[W]".format(Pmp0)
    (cell, mod, string) = (0, 0, 0)
    for testNum in range(10):
        # cell test
        print "Plot IV curve for cells in",
        print "module #{0}, string #{1}".format(mod + 1, string + 1)
        figname = 'fig{0}_cells_mod{1}_str{2}.pdf'.format(testNum,
                                                          mod + 1,
                                                          string + 1)
        figname = os.path.join(testPVdir, figname)
        pvsys.pvstrs[string].pvmods[mod].plotCell().savefig(figname)
        # module test
        print "Plot IV curve for",
        print "module #{0} in string #{1}".format(mod + 1, string + 1)
        figname = 'fig{0}_mod{1}_str{2}.pdf'.format(testNum,
                                                    mod + 1,
                                                    string + 1)
        figname = os.path.join(testPVdir, figname)
        pvsys.pvstrs[string].pvmods[mod].plotMod().savefig(figname)
        # string test
        print "Plot IV curve for string #{}".format(string + 1)
        figname = 'fig{0}_str{1}.pdf'.format(testNum, string + 1)
        figname = os.path.join(testPVdir, figname)
        pvsys.pvstrs[string].plotStr().savefig(figname)
        # system test
        print "Plot system IV curve"
        figname = 'fig{0}_sys.pdf'.format(testNum)
        figname = os.path.join(testPVdir, figname)
        pvsys.plotSys().savefig(figname)
        # irradiance test
        cell = random.randint(1, pvsys.pvstrs[0].pvmods[0].numberCells)
        mod = random.randint(1, pvsys.pvstrs[0].numberMods)
        string = random.randint(1, pvsys.numberStrs)
        suns = random.random()
        print "Set suns in cell #{0}".format(cell),
        print "in module #{0} in string #{1}".format(mod, string),
        print "to {0}".format(suns)
        (cell, mod, string) = (cell - 1, mod - 1, string - 1)
        pvsys.pvstrs[string].pvmods[mod].setSuns(suns, cell)
        print
        print "... update calculations ..."
        (pvsys.Isys, pvsys.Vsys, pvsys.Psys) = pvsys.calcSystem()
        # max power
        Pmp = np.max(pvsys.Psys)
        print "{0}% max power degradation".format(Pmp / Pmp0)
        print

    print "Test complete."
    if sys.platform is 'win32':
        os.startfile(figname)  # @UndefinedVariable # pylint: disable=E1101
