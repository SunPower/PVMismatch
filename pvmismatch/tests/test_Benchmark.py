#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Thu Jun 07 09:44:08 2012

@author: mmikofski
"""

import numpy as np
import os
import sys
from pvmismatch import PVconstants
from pvmismatch import PVsystem

NPTS = 1001
BENCHMARK = False

if __name__ == "__main__":
    if len(sys.argv)>= 2:
        if sys.argv[1] in ['False', 'None', '', '0']:
            print "No data will be saved."
        else:  
            BENCHMARK = "benchmark_" + sys.argv[1]
            print "Saving data to %s." % BENCHMARK
    else:
        print "No data will be saved."
    if len(sys.argv) >= 3:
        try:
            PVconstants().__getattribute__('parallel')
        except Exception as e: #pylint: disable=C0103
            print "This branch does **not** support multi-threading."
            raise(e)
        pvconst = PVconstants(npts=NPTS, #pylint: disable=C0103
                              parallel=(sys.argv[2] in ['True', 'Yes', '1']))
        print "Multithreading: %s." % sys.argv[2]
    else:
        pvconst = PVconstants(npts=NPTS, parallel=False)
    IcellData = np.zeros([NPTS * 2, 4])
    VcellData = np.zeros([NPTS * 2, 4])
    ImodData = np.zeros([NPTS * 2, 4])
    VmodData = np.zeros([NPTS * 2, 4])
    IstringData = np.zeros([NPTS * 2, 4])
    VstringData = np.zeros([NPTS * 2, 4])
    IsysData = np.zeros([NPTS, 4])
    VsysData = np.zeros([NPTS, 4])
    pvsys = PVsystem(pvconst=pvconst)
    print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                 pvsys.Vmp,
                                                                 pvsys.Pmp)
    print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
    print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                  pvsys.eff * 100.0)
    IcellData[:, 0] = pvsys.pvstrs[0].pvmods[0].Icell[:, 0]
    VcellData[:, 0] = pvsys.pvstrs[0].pvmods[0].Vcell[:, 0].squeeze()
    ImodData[:, 0] = pvsys.pvstrs[0].pvmods[0].Imod.squeeze() #pylint: disable=E1103,C0301
    VmodData[:, 0] = pvsys.pvstrs[0].pvmods[0].Vmod.squeeze() #pylint: disable=E1103,C0301
    IstringData[:, 0] = pvsys.pvstrs[0].Istring.squeeze()
    VstringData[:, 0] = pvsys.pvstrs[0].Vstring.squeeze()
    IsysData[:, 0] = pvsys.Isys.squeeze()
    VsysData[:, 0] = pvsys.Vsys.squeeze()
    for testNum in range(3):
        # irradiance test
        print "Set suns in cell #{0}".format(testNum),
        print "in module #{0} in string #{1}".format(testNum, testNum),
        suns = float(testNum)/10.0
        print "to {0}".format(suns)
        pvsys.pvstrs[testNum].pvmods[testNum].setSuns(suns, testNum)
        print "... update calculations ..."
        (pvsys.Isys, pvsys.Vsys, pvsys.Psys) = pvsys.calcSystem()
        (pvsys.Imp, pvsys.Vmp, pvsys.Pmp, pvsys.Isc, pvsys.Voc, pvsys.FF,
         pvsys.eff) = pvsys.calcMPP_IscVocFFeff()
        # max power
        print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                     pvsys.Vmp,
                                                                     pvsys.Pmp)
        print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
        print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                      pvsys.eff * 100.0)
        print "======================" + str(testNum) + "======================"
        IcellData[:, testNum + 1] = \
            pvsys.pvstrs[testNum].pvmods[testNum].Icell[:, testNum]
        VcellData[:, testNum + 1] = \
            pvsys.pvstrs[testNum].pvmods[testNum].Vcell[:, testNum].squeeze()
        ImodData[:, testNum + 1] = \
            pvsys.pvstrs[testNum].pvmods[testNum].Imod.squeeze()
        VmodData[:, testNum + 1] = \
            pvsys.pvstrs[testNum].pvmods[testNum].Vmod.squeeze()
        IstringData[:, testNum + 1] = pvsys.pvstrs[testNum].Istring.squeeze()
        VstringData[:, testNum + 1] = pvsys.pvstrs[testNum].Vstring.squeeze()
        IsysData[:, testNum + 1] = pvsys.Isys.squeeze()
        VsysData[:, testNum + 1] = pvsys.Vsys.squeeze()

    print "Test complete."
    if BENCHMARK:
        os.mkdir(BENCHMARK)
        np.savetxt(os.path.join(BENCHMARK, 'ICellData.csv'), IcellData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'VCellData.csv'), VcellData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'ImodData.csv'), ImodData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'VmodData.csv'), VmodData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'IstringData.csv'), IstringData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'VstringData.csv'), VstringData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'IsysData.csv'), IsysData,
                   delimiter=',')
        np.savetxt(os.path.join(BENCHMARK, 'VsysData.csv'), VsysData,
                   delimiter=',')
        print "Data saved."
