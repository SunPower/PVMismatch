# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:16:42 2020

@author: cwhanse
"""

# add capability to import from parent directory
import sys, os
sys.path.insert(1, os.path.join(os.path.abspath('.'), '..'))

import pvmismatch as pvm
import numpy as np
import pvlib
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d

# Setting PV system layout cell and module parameters
v_bypass = np.float64(-0.5)  # [V] trigger voltage of bypass diode
cell_area = np.float64(246.49)  # [cm^2] cell area
Isc0_T0 = 9.68 # [A] reference short circuit current
# set columns per substring, ncol, and number of substrings, nsub, as [ncol]*nsub
ncols_per_substr=[2]*3
nrows=10 # number of cell rows in the module
# total number of series-connected cells in a substring is nrows * 
# [ncol]*nsub is nsub bypass diodes each in parallel with ncol*nrow series-connected cells
VBYPASS = np.float64(-0.5)
MODULE_BYPASS = None

num_substrings = len(ncols_per_substr)
cells_per_substring = [[k + p*nrows*s for k in range(nrows * s)] for p, s in
                        enumerate(ncols_per_substr)]

pvconst = pvm.pvconstants.PVconstants(npts=1000)

# Building PV modules and system
pv_mod_pattern = pvm.pvmodule.standard_cellpos_pat(nrows=nrows,
                                                   ncols_per_substr=ncols_per_substr)
pv_mod = pvm.pvmodule.PVmodule(cell_pos=pv_mod_pattern, pvcells=None,
                               pvconst=pvconst, Vbypass=v_bypass, cellArea=cell_area)

for c in pv_mod.pvcells:
    c.update(diode_model = 'pvsyst', aRBD=0.0, bRBD=0.0, Isc0_T0 = Isc0_T0) # updating short circuit currents


# Set mismatch by different irradiance conditions
# one cell at bottom row of each substring is shaded
low_irrad_cells = [9, 29, 49]
low_irrad = [0.7, 0.5, 0.3]

hi_irrad_cells = list(range(0, len(pv_mod.pvcells)))
for c in low_irrad_cells:
    hi_irrad_cells.remove(c)

pv_mod.setSuns(cells=hi_irrad_cells, Ee=[1]*len(hi_irrad_cells))
pv_mod.setSuns(cells=low_irrad_cells, Ee=low_irrad)


idxs = [r['idx'] for c in pv_mod.cell_pos[0] for r in c]

Icells = []
Vcells = []
for idx in idxs:
    Icells.append(pv_mod.pvcells[idx].Icell)
    Vcells.append(pv_mod.pvcells[idx].Vcell)
Icells = np.asarray(Icells).squeeze()
Vcells = np.asarray(Vcells).squeeze()


# parallel calculation using pvlib
# first verify IV curves for each cell
tol = 5e-14

result = {}

cells_to_check = low_irrad_cells.copy()
cells_to_check.append(hi_irrad_cells[0])
for i in cells_to_check:
    icell = pvlib.pvsystem.i_from_v(resistance_shunt=pv_mod.pvcells[i].Rsh,
                                    resistance_series=pv_mod.pvcells[i].Rs,
                                    nNsVth=pv_mod.pvcells[i].N1*pv_mod.pvcells[i].Vt,
                                    voltage=pv_mod.pvcells[i].Vcell.flatten(),
                                    saturation_current=pv_mod.pvcells[i].Isat1,
                                    photocurrent=pv_mod.pvcells[i].Igen)
    # save that for later
    result[i] = (pv_mod.pvcells[i].Vcell.flatten(), icell)
    if np.max(np.abs(icell - pv_mod.pvcells[i].Icell.flatten())) < tol:
        print('Cell {} current matches'.format(i))
    else:
        print('Cell {} current does not match'.format(i))

for i in cells_to_check:
    plt.figure()
    plt.plot(result[i][0], result[i][1], 'k.')
    plt.title('IV curve for cell {}'.format(c))
    plt.show()

# now create the substring IV curves

full_sun_v = result[0][0]
full_sun_i = result[0][1]

substring_result = {}
for s, cell_list in enumerate(cells_per_substring):
    all_i = np.array(full_sun_i)
    for idx in cell_list:
        if idx in low_irrad_cells:
            all_i = np.append(all_i, result[idx][1])
    all_i = np.flipud(np.sort(all_i))
    all_v = np.zeros_like(all_i)
    for idx in cell_list:
        if idx in low_irrad_cells:
            i = result[idx][1]
            v = result[idx][0]
        else:
            i = full_sun_i
            v = full_sun_v
        f_interp = interp1d(np.flipud(i), np.flipud(v), kind='linear',
                            fill_value='extrapolate')
        all_v += f_interp(all_i)
    if VBYPASS:
        all_v = all_v.clip(min=VBYPASS)
    substring_result[s] = (all_v, all_i)

for s in substring_result:
    plt.figure()
    plt.plot(substring_result[s][0], substring_result[s][1], 'r.')
    plt.plot(pv_mod.Vsubstr[s], pv_mod.Isubstr[s], 'k.')
    plt.title('IV curve for substring {}'.format(s))
    plt.legend(['pvlib', 'PVMismatch'])
    plt.show()

# assemble module IV curve

module_i = np.array([])
for s in substring_result.keys():
    module_i = np.append(module_i, substring_result[s][1])
module_i = np.flipud(np.sort(module_i))

module_v = np.zeros_like(module_i)
for s in substring_result:
    f_interp = interp1d(np.flipud(substring_result[s][1]),
                        np.flipud(substring_result[s][0]), kind='linear',
                        fill_value='extrapolate')
    module_v += f_interp(module_i)

if MODULE_BYPASS:
    module_v = module_v.clip(min=VBYPASS)

plt.figure()
plt.plot(module_v, module_i, 'r.')
plt.plot(pv_mod.Vmod, pv_mod.Imod, 'k.')
plt.title('IV curve for module')
plt.legend(['pvlib', 'PVMismatch'])
plt.show()
