# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:43:04 2020

@author: cwhanse
"""

import numpy as np
import matplotlib.pyplot as plt

rsh = 600
rs = 0.25
iph = 9.7
io = 2.3e-11
a = 1.5


def g1(v, i, iph, io, rsh, rs, a):
    X = (v + i * rs)/ a
    c1 = rsh / (rsh + rs)
    a1 = (v + iph * rs + io * rs) / a
    a2 = io * rs / a
    return c1 * (a1 - a2 * np.exp(X))


def dg1(v, i, iph, io, rsh, rs, a):
    X = (v + i * rs)/ a
    c1 = rsh / (rsh + rs)
    a2 = io * rs / a
    return - a2 / c1 * np.exp(X)


def g2(v, i, iph, io, rsh, rs, a):
    X = (v + i * rs)/ a
    c1 = 1 + rs / rsh
    a1 = (v + iph * rs + io * rs) / a
    a2 = io * rs / a
    return np.log(a1 - c1 * X) - np.log(a2)


def dg2(v, i, iph, io, rsh, rs, a):
    X = (v + i * rs)/ a
    c1 = 1 + rs / rsh
    a1 = (v + iph * rs + io * rs) / a
    return -c1 / (a1 - c1 * X)


y1 = g1(Vmod, Imod, iph, io, rsh, rs, a)
y2 = g2(Vmod, Imod, iph, io, rsh, rs, a)

dy1 = dg1(Vmod, Imod, iph, io, rsh, rs, a)
dy2 = dg2(Vmod, Imod, iph, io, rsh, rs, a)

plt.plot(Vmod, y1, Vmod, y2)
plt.show()
plt.plot(Vmod, dy1, Vmod, dy2)
plt.show()
