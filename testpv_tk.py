#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from pvmismatch_tk.pvapplication_tk import PVapplicaton
from Tkinter import Tk

if __name__ == "__main__":
    root = Tk()
    app = PVapplicaton(root)
    app.mainloop()
    # matplotlib must implement destroy in mainloop
