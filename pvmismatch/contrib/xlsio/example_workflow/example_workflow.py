import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pvmismatch.pvmismatch_lib import pvcell, pvconstants, pvmodule, pvstring, pvsystem
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir, 'xlsio')))
from xlsio import *
# PVMismatch is developed by Mark Mikofski, Bennet Meyers and Chetan Chaudhari at SunPower Corporation, Richmond, CA.
# PVMismatch Project: https://github.com/SunPower/PVMismatch

# setting PV system layout cell and module parameters
str_len = 6 # number of modules in a string
str_num = 3 # number of (parallel connected) strings in the array
v_bypass = np.float64(-0.5)  # [V] trigger voltage of bypass diode
cell_area = np.float64(246.49)  # [cm^2] cell area
Isc0_T0 = 9.68 # [A] reference short circuit current
ncols_per_substr=[2]*3 # 3 bypass diodes with 2 series connected cell-columns each
nrows=10 # number of cell rows in the module
# building PV modules and system
pv_mod_pattern = pvmodule.standard_cellpos_pat(nrows=nrows, ncols_per_substr=ncols_per_substr)
pv_mod = pvmodule.PVmodule(cell_pos=pv_mod_pattern, pvcells=None, pvconst=None, Vbypass=v_bypass, cellArea=cell_area)
pv_cells = pv_mod.pvcells
for c in pv_cells:
    c.update(Isc0_T0 = Isc0_T0) # updating short circuit currents
pv_str = pvstring.PVstring(numberMods=str_len, pvmods=[pv_mod]*str_len)
pv_sys = pvsystem.PVsystem(numberStrs=str_num, pvstrs=[pv_str]*str_num, numberMods=[str_len]*str_num, pvmods=[pv_mod]*str_len)

# create a human-readable xls of the pv system layout with the PV cell indexes, irradiances and temperatures
output_xls_name='ExcelLayoutFromPVMM.xlsx' # this is the module and system layout in xls
pvmm_system_layout_to_xls(output_xls_name, pv_sys, nrows)
print('PV power with 1 suns on all cells: ', pv_sys.calcSystem()[2].max(), ' [W]')
plot = pv_sys.plotSys()
plt.show(block=False)

# Set now the desired irradiance input in the xls files with some xls editor

# after a human has changed the irradiance values for the system in the xls and saved it with a different name we can read the new irradiance back to python anc calculate PV power again
for i in list(range(1,6)):
    input_xls_name='ExcelLayoutFromPVMM_input{}.xlsx'.format(i) # this is the xls where we have set the new irradiances
    pvmm_set_suns_from_xls(input_xls_name, pv_sys, str_num, str_len, nrows)
    print('PV power with irradiances read in from {}: '.format(input_xls_name), pv_sys.calcSystem()[2].max(), ' [W]')
    pv_sys.plotSys()
    plt.show(block=False)
