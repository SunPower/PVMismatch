#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Mar 22, 2013

@author: mmikofski
'''

from matplotlib import pyplot as plt
import time
import sys
from pvmismatch import PVsystem
from pvmismatch import PVconstants

if __name__ == "__main__":
    numMods = 10
    if len(sys.argv)>1:
        numMods = int(sys.argv[1])
    numStrs = 10
    if len(sys.argv)>2:
        numStrs = int(sys.argv[2])
    grid = 101
    if len(sys.argv)>3:
        grid = int(sys.argv[3])
    thread = False
    if len(sys.argv)>4:
        thread = sys.argv[4] == 'True'
    tasks = None
    if len(sys.argv)>5:
        if sys.argv[5] == 'None':
            tasks = None
        else:
            tasks = int(sys.argv[5])
    chunk = None
    if len(sys.argv)>6:
        if sys.argv[6] == 'None':
            chunk = None
        else:
            chunk = int(sys.argv[6])
    cpus = None
    if len(sys.argv)>7:
        cpus = int(sys.argv[7])
    print "%s started with the following:" % sys.argv[0]
    print "\tnumber of modules: %s" % numMods
    print "\tnumber of strings: %s" % numStrs
    print "\tnumber of grid points: %s" % grid
    print "\tmultithreading: %s" % thread
    print "\tnumber of tasks: %s" % tasks
    print "\tchuncksize: %s" % chunk
    print "\tCPU's: %s" % cpus
    time.clock()
    pvconst = PVconstants(npts=grid, parallel=thread, maxtasksperchild=tasks,
                          chunksize=chunk, procs=cpus)
    pvsys = PVsystem(pvconst=pvconst, numberMods=numMods, numberStrs=numStrs)
    print "elapsed time: %s [s]" % time.clock()
    print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                 pvsys.Vmp,
                                                                 pvsys.Pmp)
    print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
    print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                  pvsys.eff * 100.0)
    for n in range(numStrs):
        print "String #%s, elapsed time: %s [s]" % (n + 1, time.clock())
        for m in range(numMods):
            pvsys.pvstrs[n].pvmods[m].setSuns(0.95)
    print "elapsed time: %s [s]" % time.clock()
    (pvsys.Isys, pvsys.Vsys, pvsys.Psys) = pvsys.calcSystem()
    (pvsys.Imp, pvsys.Vmp, pvsys.Pmp,
     pvsys.Isc, pvsys.Voc, pvsys.FF, pvsys.eff) = pvsys.calcMPP_IscVocFFeff()
    # max power
    print "Imp: %10.4f [A], Vmp: %10.4f [V], Pmp: %10.4f [W]" % (pvsys.Imp,
                                                                 pvsys.Vmp,
                                                                 pvsys.Pmp)
    print "Isc: %10.4f [A], Voc: %10.4f [V]" % (pvsys.Isc, pvsys.Voc)
    print "FF:  %10.4f [%%], eff: %10.4f [%%]" % (pvsys.FF * 100.0,
                                                  pvsys.eff * 100.0)
    print "elapsed time: %s [s]" % time.clock()
    #pvsys.plotSys()
    #plt.show()