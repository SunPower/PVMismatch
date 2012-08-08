#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from pvmismatch_tk.pvapplication_tk import PVapplicaton
from Tkinter import Tk
import sys
import re

def showHelpError(argvs):
    help(Tk.geometry)
    errMsg = 'Invalid geometry format.\n'
    errMsg = errMsg+'"{}"\n'.format(argvs)
    errMsg = errMsg+'is not valid. See "wm_geometry help" above.'
    raise Exception(errMsg)

if __name__ == "__main__":
    nargv = len(sys.argv)  # number of user arguments
    argvs = sys.argv[1:]  # will be empty if only sys.argv[0]
    if argvs:
        argv1 = sys.argv[1]
        # test if input is 'WxH' or 'WxH+/-X+/-Y'
        if nargv == 2: # and type(argv1) is str:
            dims = re.findall('\d+x\d+[+-]\d+[+-]\d+', argv1)
            if not dims:
                dims = re.findall('\d+x\d+', argv1)
            if argv1 == 'home':
                dims = ['837x655']
            elif not dims or len(dims) > 1 or len(dims[0]) != len(argv1):
                showHelpError(argvs)
            dims = dims[0]
        # test if input is (W, H)
        elif nargv in [3, 5]:
            try:
                argvs = [int(argv) for argv in argvs]
            except ValueError:
                showHelpError(argvs)
            if nargv == 3:
                dims = "{}x{}".format(*argvs)
            if nargv == 5:
                dims = "{}x{}{:+d}{:+d}".format(*argvs)
        else:
            showHelpError(argvs)
    else:
        dims = None
    print "dimensions: {}".format(dims)
    root = Tk()
    app = PVapplicaton(root)
    root.geometry(dims)
    app.mainloop()
    # matplotlib must implement destroy in mainloop
