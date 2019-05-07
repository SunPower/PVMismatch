#!/usr/bin/env python

'''
Created on Mar 29, 2013

This script allows the user to dynamically investigate the IV and PV
characteristics of a single module. The user chooses the modules size--72 or 96
cells. A GUI is then generated that allows the user to change the size, location,
and irradiance level of a single "shade rectangle". Outputs include cell,
substring, and module level IV and PV curves as well as a module diagram showing
the shade location, any reverse biased cells, and any active diodes.

@author: bmeyers
'''
# ==============================================================================
# Importing standard libraries
# ==============================================================================

from __future__ import (
    absolute_import, division, unicode_literals, print_function)
import json
from functools import partial
from copy import deepcopy
import os
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider
from matplotlib.widgets import Button
from past.builtins import raw_input, xrange

# ==============================================================================
# Import PVmismatch items
# ==============================================================================

try:
    from pvmismatch import PVsystem, PVmodule, PVcell, PVconstants
    from pvmismatch.pvmismatch_lib.pvmodule import STD72, STD96, STD128
except ImportError:
    print("PVMismatch not found on path! Please use 'pip install -e path/to/pvmismatch'")
    print("or 'export PYTHONPATH=path/to/pvmismatch:$PYTHONPATH' first.")
    import sys
    sys.exit(-1)

# ==============================================================================
# Define Classes and Functions
# ==============================================================================

def modheight(numberCells):
    if numberCells % 12 == 0:
        modHeight = 12
    else:
        modHeight = 16
    return modHeight


class ShadeObj(object):
    """
    A Class for creating a rectangular shade object. Accounts for the fact that
    the cells are ordered sequentially in PVMismatch according to their
    electrical connections, but a user often wants to think about the layout of
    shade on a real module.
    The cell stringing layout of an example 96-cell module is as follows:
    11    12    35    36    59    60    83    84
    10    13    34    37    58    61    82    85
    9     14    33    38    57    62    81    86
    8     15    32    39    56    63    80    87
    7     16    31    40    55    64    79    88
    6     17    30    41    54    65    78    89
    5     18    29    42    53    66    77    90
    4     19    28    43    52    67    76    91
    3     20    27    44    51    68    75    92
    2     21    26    45    50    69    74    93
    1     22    25    46    49    70    73    94
    0     23    24    47    48    71    72    95
    So, shd_x=4 and shd_y=6 corresponds to cell 42
    """

    def __init__(self, pershade=90, shd_width=1, shd_height=1, shd_x=4,
                 shd_y=6, numberCells=96):
        modHeight = modheight(numberCells)
        module = np.empty([numberCells // modHeight, modHeight], dtype=int)
        for n in range(numberCells // modHeight):
            if n % 2 == 0:
                module[n] = np.arange(n * modHeight, (n + 1) * modHeight, 1)
            else:
                module[n] = np.arange((n + 1) * modHeight - 1,
                                      n * modHeight - 1, -1)
        module = module.T

        self.numberCells = numberCells
        self.modHeight = modHeight
        self.pershade = pershade
        self.sw = shd_width
        self.sh = shd_height
        self.sx = shd_x
        self.sy = shd_y
        self.nx = np.arange(shd_x, shd_x + shd_width, 1)
        self.ny = np.arange(shd_y, shd_y + shd_height, 1)
        self.nx, self.ny = np.meshgrid(self.nx, self.ny)
        self.shadecells = []
        for i in self.nx[0]:
            for j in self.ny.T[0]:
                self.shadecells.append(module[int(j - 1), int(i - 1)])

    def plot(self):
        x1 = self.numberCells / self.modHeight + 1
        y1 = self.modHeight + 1
        x = np.arange(1, x1, 1)
        y = np.arange(1, y1, 1)
        x, y = np.meshgrid(x, y)
        plt.Figure()
        plt.scatter(x, y, s=.5*1000, c='w', marker='s')
        plt.scatter(self.nx, self.ny, s=.5*1000, c='k', marker='s', alpha=self.pershade / 100.)
        plt.show()


def plotting_calcs(pvmod, ivp=None):
    if ivp is None:
        ivp = IVP()
    numberCells = pvmod.numberCells
    pvcells = pvmod.pvcells
    ivp.pvcells = pvcells
    calcmod1 = pvmod.calcMod()
    ivp.Imod = calcmod1[0].squeeze()
    ivp.Vmod = calcmod1[1].squeeze()
    ivp.Pmod = calcmod1[2].squeeze()
    ivp.Isubstr = calcmod1[3].squeeze()
    ivp.Vsubstr = calcmod1[4].squeeze()
    ind = ivp.Pmod.argmax()
    ivp.Imp = ivp.Imod[ind]
    ivp.Vmp = ivp.Vmod[ind]
    ivp.Pmp = ivp.Pmod[ind]
    ivp.Icell = pvmod.Icell.T
    ivp.Vcell = pvmod.Vcell.T
    ivp.Pcell = pvmod.Pcell.T
    ivp.Voc = pvmod.Voc
    ivp.VRBD = pvcells[0].VRBD
    # Create coordinates of cells that have active diodes
    ivp.activediode = []
    if numberCells == 72:   # a 72 cell module
        ad_x = [1, 3, 5]
    else:                               # a 96 or 128 cell module
        ad_x = [1, 3, 7]
    if numberCells % 12 == 0:
        ivp.modHeight = 12
    else:
        ivp.modHeight = 16
    interp_funcs = [interp1d(ivp.Isubstr[i], ivp.Vsubstr[i]) for i in xrange(3)]
    substring_Vmps = [f(ivp.Imp) for f in interp_funcs]
    for n, ss_Vmp in enumerate(substring_Vmps):
        if ss_Vmp < 0:
            diodobj = ShadeObj(pershade=100,
                               shd_width=pvmod.subStrCells[n],
                               shd_height=ivp.modHeight,
                               shd_x=ad_x[n], shd_y=1,
                               numberCells=numberCells)
            ivp.activediode.append(diodobj)
    # Create coordinates of cells that are reverse biased
    reversebias = [n for n in range(len(ivp.Icell.T))
                   if -np.interp(-ivp.Imp, -ivp.Icell.T[n], -ivp.Vcell.T[n]) < 0]
    boolindx = np.array(reversebias)
    module = np.empty([pvmod.numberCells // ivp.modHeight, ivp.modHeight], dtype=int)
    for n in range(pvmod.numberCells // ivp.modHeight):
        if n % 2 == 0:
            module[n] = np.arange(n * ivp.modHeight, (n + 1) * ivp.modHeight, 1)
        else:
            module[n] = np.arange((n + 1) * ivp.modHeight - 1,
                                  n * ivp.modHeight - 1, -1)
    ivp.rb_y, ivp.rb_x = [], []
    for i in boolindx:
        y1, x1 = np.where(module == i)
        ivp.rb_x.append(y1.flatten()[0] + 1)
        ivp.rb_y.append(x1.flatten()[0] + 1)
    return ivp


class IVP(object):
    """A class for holding module, cell, and substring data"""
    def __init__(self, Imod=None, Vmod=None, Pmod=None, Vsubstr=None, Isubstr=None, Imp=None,
                 Vmp=None, Pmp=None, Icell=None, Vcell=None, Pcell=None, pvcells=None,
                 Voc=None, VRBD=None, shade=None, activediode=None, rb_x=None, rb_y=None,
                 shade_index=None, modHeight=None):
        self.Imod = Imod
        self.Vmod = Vmod
        self.Pmod = Pmod
        self.Vsubstr = Vsubstr
        self.Isubstr = Isubstr
        self.Imp = Imp
        self.Vmp = Vmp
        self.Pmp = Pmp
        self.Icell = Icell
        self.Vcell = Vcell
        self.Pcell = Pcell
        self.pvcells = pvcells
        self.Voc = Voc
        self.VRBD = VRBD
        self.shade = shade
        self.activediode = activediode
        self.rb_x = rb_x
        self.rb_y = rb_y
        self.shade_index = shade_index
        self.modHeight = modHeight


class PlotObjs(object):
    """A class for holding line and scatter objects for plotting"""
    def __init__(self, lcellIVR=None, lcellIVF=None, lcellPVR=None,
                 lcellPVF=None, lmodIV=None, lmodPV=None, lsubsIV=None,
                 scatter=list(range(4)),
                 text1=None, lines=list(range(6))):
        self.lcellIVR = lcellIVR
        self.lcellIVF = lcellIVF
        self.lcellPVR = lcellPVR
        self.lcellPVF = lcellPVF
        self.lmodIV = lmodIV
        self.lmodPV = lmodPV
        self.lsubsIV = lsubsIV
        self.scatter = scatter
        self.text1 = text1
        self.lines = lines


def construct_plot_area(numcells, modHeight):
    cellPlot = plt.figure(figsize=(22, 6))
    gs = gridspec.GridSpec(2, 5)
    gs.update(left=0.06, right=0.96, wspace=0.25)
    ax00 = cellPlot.add_subplot(gs[0, 0])
    ax00.set_title('Cell Reverse I-V Characteristics')
    ax00.set_ylabel('Cell Current, I [A]')
    ax00.grid()
    ax01 = cellPlot.add_subplot(gs[0, 1])
    ax01.set_title('Cell Forward I-V Characteristics')
    ax01.set_ylabel('Cell Current, I [A]')
    ax01.grid()
    ax10 = cellPlot.add_subplot(gs[1, 0])
    ax10.set_title('Cell Reverse P-V Characteristics')
    ax10.set_xlabel('Cell Voltage, V [V]')
    ax10.set_ylabel('Cell Power, P [W]')
    ax10.grid()
    ax11 = cellPlot.add_subplot(gs[1, 1])
    ax11.set_title('Cell Forward P-V Characteristics')
    ax11.set_xlabel('Cell Voltage, V [V]')
    ax11.set_ylabel('Cell Power, P [W]')
    ax11.grid()
    ax02 = cellPlot.add_subplot(gs[0, 2])
    ax02.set_title('Module I-V Characteristics')
    ax02.set_ylabel('Module Current, I [A]')
    ax02.grid()
    ax12 = cellPlot.add_subplot(gs[1, 2])
    ax12.set_title('Module P-V Characteristics')
    ax12.set_xlabel('Module Voltage, V [V]')
    ax12.set_ylabel('Module Power, P [W]')
    ax12.grid()
    ax03 = cellPlot.add_subplot(gs[0, 3])
    ax03.set_title('Cell String I-V Characteristics')
    ax03.set_xlabel('Cell String Voltage, V [V]')
    ax03.set_ylabel('String Current, I [A]')
    ax03.grid()
    ax_4 = cellPlot.add_subplot(gs[:, 4])
    ax_4.set_title('Shade Diagram')
    ax_4.set_xlim(0.5, 8.5)
    ax_4.set_ylim(0.5, modHeight + 0.5)
    ax_4.set_aspect('equal')
    x = np.arange(1, numcells / modHeight + 1, 1)
    y = np.arange(1, modHeight + 1, 1)
    x, y = np.meshgrid(x, y)
    output = {'cellPlot': cellPlot, 'gs': gs, 'ax00': ax00, 'ax01': ax01, 'ax10': ax10, 'ax11': ax11, 'ax02': ax02,
              'ax12': ax12, 'ax03': ax03, 'ax_4': ax_4, 'x': x, 'y': y}
    return output


def pvsys_defs_user_input(npts=101, user_set_temp=False, tcell=298.15):
    """
    Prompt a user to input array definitions from the command line. Returns all
    info necessary to create a PVsystem instance
    """
    modsizeinput = int(raw_input("Module Size? (1=72c, 2=96c, 3=128c): "))
    while modsizeinput != 1 and modsizeinput != 2 and modsizeinput != 3:
        modsizeinput = input("Please input 1, 2, or 3, please. ")
    if modsizeinput == 1:
        cellpos = STD72
        modHeight = 12
        numCells = 72
    elif modsizeinput == 2:
        cellpos = STD96
        modHeight = 12
        numCells = 96
    elif modsizeinput == 3:
        cellpos = STD128
        modHeight = 16
        numCells = 128
    tcell = int(raw_input("Cell temperature (deg C)? "))
    tcell = tcell + 273.15
    pvcelldict = {'Tcell': tcell, 'pvconst': PVconstants(npts=npts)}
    pvmoddict = {'cell_pos': cellpos, 'Vbypass': -0.5, 'pvconst': PVconstants(npts=npts)}
    pvcell = PVcell(**pvcelldict)
    pvmod = PVmodule(pvcells=pvcell, **pvmoddict)
    pvsys = PVsystem(pvmods=pvmod, numberStrs=1, numberMods=1, pvconst=pvmod.pvconst)
    return pvsys, modHeight, numCells



def all_calc(ivp, i_ps, i_sw, i_sh, i_sx, i_sy):
    """Calculate cell and module parameters"""
    if i_sx + i_sw > (numcells / 12 + 1):
        i_sw = (numcells / modHeight + 1) - i_sx
    if i_sy + i_sh > modHeight + 1:
        i_sh = (modHeight + 1) - i_sy
    if len(ivp.shade) != 0:
        ivp.shade.pop()
    ivp.shade.append(ShadeObj(pershade=i_ps, shd_width=i_sw, shd_height=i_sh,
                              shd_x=i_sx, shd_y=i_sy,
                              numberCells=pvmod1.numberCells))
    pvmod1.setSuns(1.0)
    for shd in ivp.shade:
        pvmod1.setSuns(1 - (shd.pershade / 100.), shd.shadecells)
    _ = plotting_calcs(pvmod1, ivp=ivp)


def plot_init(ivp, plotobjs, ax00, ax01, ax10, ax11, ax02, ax12, ax03, ax_4, x, y):
    # Create plot objects
    plotobjs.lcellIVR = list(ax00.plot(ivp.Vcell, ivp.Icell))
    plotobjs.lcellIVF = list(ax01.plot(ivp.Vcell, ivp.Icell))
    plotobjs.lcellPVR = list(ax10.plot(ivp.Vcell, ivp.Pcell))
    plotobjs.lcellPVF = list(ax11.plot(ivp.Vcell, ivp.Pcell))
    plotobjs.lmodIV, = ax02.plot(ivp.Vmod, ivp.Imod)
    plotobjs.lmodPV, = ax12.plot(ivp.Vmod, ivp.Pmod)
    plotobjs.lsubsIV = list(ax03.plot(ivp.Vsubstr[0], ivp.Isubstr[0], ivp.Vsubstr[1],
                                      ivp.Isubstr[1], ivp.Vsubstr[2], ivp.Isubstr[2]))
    # Create line objects
    plotobjs.lines[0] = ax00.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[1] = ax01.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[2] = ax02.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[3] = ax02.axvline(x=ivp.Vmp, color='r')
    plotobjs.lines[4] = ax12.axvline(x=ivp.Vmp, color='r')
    plotobjs.lines[5] = ax03.axhline(y=ivp.Imp, color='r')
    # Create objects for diagram
    if ivp.rb_x:
        plotobjs.scatter[0] = ax_4.scatter(ivp.rb_x, ivp.rb_y, s=.5*800, c='r',
                                           marker='s')
    plotobjs.scatter[1] = []
    for ad in ivp.activediode:
        plotobjs.scatter[1].append(ax_4.scatter(ad.nx, ad.ny, s=.5*850, c='b',
                                                marker='s'))
    plotobjs.scatter[2] = ax_4.scatter(x, y, s=.5*500, c='w', marker='s', edgecolor='black')
    plotobjs.text1 = []
    for shd in ivp.shade:
        plotobjs.scatter[3] = ax_4.scatter(shd.nx, shd.ny, s=.5*500, c='k',
                                           marker='s',
                                           alpha=shd.pershade / 100.)
        for a in shd.nx[0]:
            for b in shd.ny.T[0]:
                plotobjs.text1.append(ax_4.text(a - 0.25, b - 0.25,
                                                int(shd.pershade), color='r'))
#   Set limits
    ax00.set_xlim(ivp.VRBD - 1, 0)
    ax00.set_ylim(0, ivp.pvcells[0].Isc0_T0 + 10)
    ax01.set_xlim(0, np.max(ivp.Voc))
    ax01.set_ylim(0, ivp.pvcells[0].Isc0_T0 + 1)
    ax10.set_xlim(ivp.VRBD - 1, 0)
    ax10.set_ylim((ivp.pvcells[0].Isc0_T0 + 10) * (ivp.VRBD - 1), -1)
    ax11.set_xlim(0, np.max(ivp.Voc))
    ax11.set_ylim(0, (ivp.pvcells[0].Isc0_T0 + 1) * np.max(ivp.Voc))
    ax02.set_ylim(0, ivp.pvcells[0].Isc0_T0 + 1)
    ax02.set_xlim(0, np.max(ivp.Vmod) * 1.25)
    ax12.set_ylim(0, np.max(ivp.Pmod) * 1.25)
    ax12.set_xlim(0, np.max(ivp.Vmod) * 1.25)
    ax03.set_ylim(0, ivp.pvcells[0].Isc0_T0 + 1)
    ax03.set_xlim(0, np.max(ivp.Vsubstr) * 1.0)


def plot_update(ivp, plotobjs, ax00, ax01, ax10, ax11, ax02, ax12, ax03, ax_4, x, y):
    # Update plot objects
    for i in range(len(plotobjs.lcellIVR)):
        plotobjs.lcellIVR[i].set_data(ivp.Vcell.T[i], ivp.Icell.T[i])
        plotobjs.lcellIVF[i].set_data(ivp.Vcell.T[i], ivp.Icell.T[i])
        plotobjs.lcellPVR[i].set_data(ivp.Vcell.T[i], ivp.Pcell.T[i])
        plotobjs.lcellPVF[i].set_data(ivp.Vcell.T[i], ivp.Pcell.T[i])
    plotobjs.lmodIV.set_data(ivp.Vmod, ivp.Imod)
    plotobjs.lmodPV.set_data(ivp.Vmod, ivp.Pmod)
    for i in range(len(plotobjs.lsubsIV)):
        plotobjs.lsubsIV[i].set_data(ivp.Vsubstr[i], ivp.Isubstr[i])
    # Update line objects
    for i in range(6):
        plotobjs.lines[i].remove()
    plotobjs.lines[0] = ax00.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[1] = ax01.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[2] = ax02.axhline(y=ivp.Imp, color='r')
    plotobjs.lines[3] = ax02.axvline(x=ivp.Vmp, color='r')
    plotobjs.lines[4] = ax12.axvline(x=ivp.Vmp, color='r')
    plotobjs.lines[5] = ax03.axhline(y=ivp.Imp, color='r')
#     Update scatter objects
    for i in range(4):
        if plotobjs.scatter[i]:
            if i == 1:
                for scatt in plotobjs.scatter[i]:
                    scatt.remove()
            else:
                plotobjs.scatter[i].remove()
    for text in plotobjs.text1:
        text.remove()
    if ivp.rb_x:
        plotobjs.scatter[0] = ax_4.scatter(ivp.rb_x, ivp.rb_y, s=.5*800, c='r',
                                           marker='s')
    else:
        plotobjs.scatter[0] = None
    plotobjs.scatter[1] = []
    for ad in ivp.activediode:
        plotobjs.scatter[1].append(ax_4.scatter(ad.nx, ad.ny, s=.5*850, c='b',
                                                marker='s'))
    plotobjs.scatter[2] = ax_4.scatter(x, y, s=.5*500, c='w', marker='s', edgecolor='black')
    plotobjs.text1 = []
    for shd in ivp.shade:
        plotobjs.scatter[3] = ax_4.scatter(shd.nx, shd.ny, s=.5*500, c='k',
                                           marker='s',
                                           alpha=shd.pershade / 100.)
        for a in shd.nx[0]:
            for b in shd.ny.T[0]:
                plotobjs.text1.append(ax_4.text(a - 0.25, b - 0.25,
                                                int(shd.pershade), color='r'))


def full_update(val, output=None, ivp0=None, plotobjs=None):
    ps = s_ps.val
    sw = round(s_sw.val)
    sh = round(s_sh.val)
    sy = round(s_sy.val)
    sx = round(s_sx.val)
    all_calc(ivp0, ps, sw, sh, sx, sy)
    plot_update(ivp0, plotobjs, output['ax00'], output['ax01'], output['ax10'], output['ax11'], output['ax02'],
                output['ax12'], output['ax03'], output['ax_4'], output['x'], output['y'])
    plt.draw()
    t1 = (sw * sh, s_ps.val, ivp0.Pmp, 100 * ivp0.Pmp / Pmp0)
    print('{0:^6} {1:^6,.2f} {2:^6,.2f} {3:^7,.2f}'.format(*t1))


def set_the_shade(val):
    ivp0.shade.insert(0, ivp0.shade[-1])


def save_the_shade(val):
    this_dir = os.getcwd()
    save_dir = os.path.join(this_dir, 'JSONshade')
    os.makedirs(save_dir, exist_ok=True)
    dicts = []
    for shd in ivp0.shade:
        dicts.append({'ps': shd.pershade, 'sw': shd.sw, 'sh': shd.sh,
                      'sy': shd.sy, 'sx': shd.sx,
                      'numberCells': pvmod1.numberCells})
    filename = raw_input("File name? ")
    filename = os.path.join(save_dir, filename + '.json')
    with open(filename, 'w') as fo:
        json.dump(dicts, fo, sort_keys=True, indent=2)


def clear_last_full(val, update=None):
    if len(ivp0.shade) != 1:
        ivp0.shade.pop(-2)
    update(val)


if __name__ == "__main__":
    pvsys, modHeight, numcells = pvsys_defs_user_input(npts=201)
    output = construct_plot_area(numcells, modHeight)
    pvmod1 = pvsys.pvstrs[0].pvmods[0]
    pvmod_noshade = deepcopy(pvmod1)
    calcmod_noshade = pvmod_noshade.calcMod()
    Pmod_noshade = calcmod_noshade[2].squeeze()
    Pmp0 = Pmod_noshade.max()
    ivp0 = IVP()
    plotobjs = PlotObjs()
    update = partial(full_update, output=output, ivp0=ivp0, plotobjs=plotobjs)
    ClearLast = partial(clear_last_full, update=update)
    print("Pmp0: {}".format(Pmp0))
    print("")
    print('{0:6} {1:^6} {2:^6} {3:^7}'.format('#Cells', '%Shade', 'Pmp', '%ofPmp0'))
    print('----------------------------')
    ps0 = 90
    sw0 = 1
    sh0 = 1
    sy0 = 1
    sx0 = 1
    ivp0.shade = []
    all_calc(ivp0, ps0, sw0, sh0, sx0, sy0)
    plot_init(ivp0, plotobjs, output['ax00'], output['ax01'], output['ax10'], output['ax11'], output['ax02'],
              output['ax12'], output['ax03'], output['ax_4'], output['x'], output['y'])
    plt.draw()

    cellPlot = output['cellPlot']
    ax_ps = cellPlot.add_axes([0.64, 0.38, 0.12, .04])
    ax_sw = cellPlot.add_axes([0.64, 0.33, 0.12, .04])
    ax_sh = cellPlot.add_axes([0.64, 0.28, 0.12, .04])
    ax_sy = cellPlot.add_axes([0.64, 0.23, 0.12, .04])
    ax_sx = cellPlot.add_axes([0.64, 0.18, 0.12, .04])
    ax_button_setshade = cellPlot.add_axes([0.63, 0.10, 0.06, 0.06])
    ax_button_saveshade = cellPlot.add_axes([0.71, 0.10, 0.06, 0.06])
    ax_button_clearlast = cellPlot.add_axes([0.67, 0.03, 0.06, 0.06])
    s_ps = Slider(ax_ps, 'Shade%', 0, 100, valinit=ps0)
    s_sw = Slider(ax_sw, 'Width', 1, numcells / modHeight, valinit=sw0,
                  valfmt='%0.0f')
    s_sh = Slider(ax_sh, 'Height', 1, modHeight, valinit=sh0, valfmt='%0.0f')
    s_sy = Slider(ax_sy, 'Row Start', 1, modHeight, valinit=sw0,
                  valfmt='%0.0f')
    s_sx = Slider(ax_sx, 'Col Start', 1, numcells / modHeight, valinit=sh0,
                  valfmt='%0.0f')
    b_setshade = Button(ax_button_setshade, "Set Shade")
    b_saveshade = Button(ax_button_saveshade, "Save Shade")
    b_clearlast = Button(ax_button_clearlast, "Clear Last")
    s_ps.on_changed(update)
    s_sw.on_changed(update)
    s_sh.on_changed(update)
    s_sy.on_changed(update)
    s_sx.on_changed(update)
    b_setshade.on_clicked(set_the_shade)
    b_saveshade.on_clicked(save_the_shade)
    b_clearlast.on_clicked(ClearLast)

plt.show()
