#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Apr 29, 2013

@author: mmikofski
'''

from pvmismatch.pvconstants import PVconstants
from pvmismatch.pvsystem import PVsystem
from matplotlib import pyplot as plt

if __name__ == '__main__':
    pvconst = PVconstants(npts=101, parallel=False)  # increase number of points to calculate
    pvsys = PVsystem(pvconst=pvconst, numberStrs=1, numberMods=8)
    print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                 pvsys.Vmp,
                                                                 pvsys.Pmp)
    print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
    print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                  pvsys.eff * 100.0)
    print "==================== Shade module #1 by 90%. ===================="
    pvstr = pvsys.pvstrs[0]
    pvmodShade90 = pvstr.pvmods[0]
    pvmodShade90.setSuns(0.1)
    (pvsys.Isys, pvsys.Vsys, pvsys.Psys) = pvsys.calcSystem()
    (pvsys.Imp, pvsys.Vmp, pvsys.Pmp,
     pvsys.Isc, pvsys.Voc, pvsys.FF, pvsys.eff) = pvsys.calcMPP_IscVocFFeff()
    print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                 pvsys.Vmp,
                                                                 pvsys.Pmp)
    print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
    print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                  pvsys.eff * 100.0)
    pvmodShade90.plotCell()
    pvmodShade90.plotMod()
    pvstr.plotStr()
    plt.show()
    