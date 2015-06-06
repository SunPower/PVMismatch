#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Mar 22, 2013

@author: mmikofski
'''

from pvmismatch import PVconstants

if __name__ == "__main__":
    pvconst = PVconstants()
    print pvconst.Tcell, pvconst.Isat1, pvconst.Isc0
    pvconst.update(Tcell=353.15)
    print pvconst.Tcell, pvconst.Isat1, pvconst.Isc0
    pvconst.update(Tcell=298.15)
    print pvconst.Tcell, pvconst.Isat1, pvconst.Isc0
