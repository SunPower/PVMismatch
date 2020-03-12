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


# Setting PV system layout cell and module parameters
v_bypass = np.float64(-0.5)  # [V] trigger voltage of bypass diode
cell_area = np.float64(246.49)  # [cm^2] cell area
Isc0_T0 = 9.68 # [A] reference short circuit current
ncols_per_substr=[2]*3 # 3 bypass diodes each in parallel with 2 series connected cell-columns
nrows=10 # number of cell rows in the module

pvconst = pvm.pvconstants.PVconstants(npts=1000)

# Building PV modules and system
pv_mod_pattern = pvm.pvmodule.standard_cellpos_pat(nrows=nrows,
                                                   ncols_per_substr=ncols_per_substr)
pv_mod = pvm.pvmodule.PVmodule(cell_pos=pv_mod_pattern, pvcells=None,
                               pvconst=pvconst, Vbypass=v_bypass, cellArea=cell_area)

for c in pv_mod.pvcells:
    c.update(diode_model = 'pvsyst', aRBD=0.0, bRBD=0.0, Isc0_T0 = Isc0_T0) # updating short circuit currents


# Set mismatch by different irradiance conditions
# bottom 2 rows of cells are shaded
low_irrad = 0.5

low_irrad_cells = [8, 9, 19, 18]
hi_irrad_cells = list(range(0, len(pv_mod.pvcells)))
for c in low_irrad_cells:
    hi_irrad_cells.remove(c)

pv_mod.setSuns(cells=hi_irrad_cells, Ee=[1]*len(hi_irrad_cells))
pv_mod.setSuns(cells=low_irrad_cells, Ee=[low_irrad]*len(low_irrad_cells))


# remove negative voltage and current
# =============================================================================
# u = (pv_mod.Vmod>=0.) & (pv_mod.Imod>=0.)
# 
# plt.figure()
# plt.plot(pv_mod.Vmod[u], pv_mod.Imod[u], 'r.')
# plt.title('Module IV curve')
# plt.show()
# 
# uu = (pv_mod.Vmod > 30) & (pv_mod.Imod>=0.)  # focus on segment towards Voc
# 
# plt.figure()
# plt.plot(pv_mod.Vmod[uu], pv_mod.Imod[uu], 'b.')
# plt.title('Module IV curve - Voc end')
# plt.show()
# =============================================================================

# =============================================================================
# # plot IV curve for string with shaded cells
# plt.figure()
# plt.plot(pv_mod.Vsubstr[0], pv_mod.Isubstr[0], 'k.')
# plt.title('IV curve for substring with mismatched cells')
# plt.show()
# 
# 
# plt.figure()
# for idx in range(0, 59):
# #    v = (pv_mod.pvcells[idx].Vcell>=0.) & (pv_mod.pvcells[idx].Icell>=0.)
# #    plt.plot(pv_mod.pvcells[idx].Vcell[v], pv_mod.pvcells[idx].Icell[v])
#     plt.plot(pv_mod.pvcells[idx].Vcell, pv_mod.pvcells[idx].Icell)
# plt.title('IV curves for each cell')
# plt.show()
# =============================================================================

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

for i in [0, 9]:
    icell = pvlib.pvsystem.i_from_v(resistance_shunt=pv_mod.pvcells[i].Rsh,
                                    resistance_series=pv_mod.pvcells[i].Rs,
                                    nNsVth=pv_mod.pvcells[i].N1*pv_mod.pvcells[i].Vt,
                                    voltage=pv_mod.pvcells[i].Vcell.flatten(),
                                    saturation_current=pv_mod.pvcells[i].Isat1,
                                    photocurrent=pv_mod.pvcells[i].Igen)
    # save that for later
    result[i] = (pv_mod.pvcells[i].Vcell.flatten(), icell)
    if np.max(np.abs(icell - Icells[i, :].flatten())) < tol:
        print('Cell {} current matches'.format(i))
    else:
        print('Cell {} current does not match'.format(i))

# now create the substring IV curve
full_sun_v = result[0][0]
full_sun_i = result[0][1]

low_sun_v = result[9][0]
low_sun_i = result[9][1]

all_i = np.flipud(np.sort(np.append(full_sun_i, low_sun_i)))
full_sun_v_ext = np.interp(all_i, np.flipud(full_sun_i), np.flipud(full_sun_v))
low_sun_v_ext = np.interp(all_i, np.flipud(low_sun_i), np.flipud(low_sun_v))
all_v = full_sun_v_ext * 18 + low_sun_v_ext * 2

plt.figure()
plt.plot(low_sun_v_ext, all_i)
plt.plot(full_sun_v_ext, all_i)
plt.title('Cell-level IV curves from pvlib')
plt.legend(['low sun', 'full sun'])
plt.show()

plt.figure()
plt.plot(all_v, all_i, 'r.')
plt.plot(pv_mod.Vsubstr[0], pv_mod.Isubstr[0], 'k.')
plt.title('Substring IV curves')
plt.legend(['pvlib', 'PVMismatch'])
plt.show()
