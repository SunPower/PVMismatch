#! python
# -*- coding: utf-8 -*-

"""
Created on Jul 29, 2012

@author: marko
"""
from pvmismatch.pvmismatch_tk.pvapplication_tk import PVapplicaton
from Tkinter import Tk
import sys
import re


def showHelpError(argvs_):
    help(Tk.geometry)
    errMsg = 'Invalid geometry format.\n'
    errMsg = errMsg + '"{}"\n'.format(argvs_)
    errMsg = errMsg + 'is not valid. See "wm_geometry help" above.'
    raise Exception(errMsg)

if __name__ == "__main__":
    nargv = len(sys.argv)  # number of user arguments
    argvs = sys.argv[1:]  # will be empty if only sys.argv[0]
    if argvs:
        argv1 = sys.argv[1]
        # test if input is 'home','reset','WxH+/-X+/-Y' or 'WxH'
        if nargv == 2:  # and type(argv1) is str:
            # try any custom geometry e.g. ('home', 'reset')
            if argv1 == 'home':
                dims = '835x655'  # custom setting for my home laptop
            elif argv1 in ["", 'reset']:
                dims = ""  # reset the geometry
            else:
                # try regular expressions for 'WxH+/-X+/-Y' or 'WxH'
                dims = re.findall('\d+x\d+[+-]\d+[+-]\d+', argv1)
                # dims will be empty if nothing found
                if not dims:
                    dims = re.findall('\d+x\d+', argv1)
                # still nothing, or too much, or extra crap
                if not dims or len(dims) > 1 or len(dims[0]) != len(argv1):
                    showHelpError(argvs)
                # found it, get string from list, should be only one
                else:
                    dims = dims[0]
        # test if input is (W, H)
        elif nargv in [3, 5]:
            try:
                argvs = [int(argv) for argv in argvs]
            except ValueError:
                showHelpError(argvs)
            if nargv == 3:
                dims = "{}x{}".format(*argvs)  # IGNORE:W0142
            if nargv == 5:
                dims = "{}x{}{:+d}{:+d}".format(*argvs)  # IGNORE:W0142
        else:
            showHelpError(argvs)
    else:
        dims = None
    if dims is not None:
        dim_reset_or_dims = lambda dims: (not dims) * 'reset' + dims
        print "dimensions: {}".format(dim_reset_or_dims(dims))
    root = Tk()
    app = PVapplicaton(root)
    root.geometry(dims)
    app.mainloop()
    # matplotlib must implement destroy in mainloop
