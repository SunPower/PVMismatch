# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from pvmismatch_tk.pvapplication_tk import PVapplicaton
from Tkinter import Tk
root = Tk()
app = PVapplicaton(root)
app.mainloop()
# please destroy me or I'll continue to run in background
root.detroy()
