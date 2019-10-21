import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pvmismatch.pvmismatch_lib import (pvcell, pvconstants, pvmodule,
                                       pvstring, pvsystem)

from pvmismatch.contrib import xlsio

# Setting PV system layout cell and module parameters
str_len = 6 # number of modules in a string
str_num = 3 # number of (parallel connected) strings in the array
v_bypass = np.float64(-0.5)  # [V] trigger voltage of bypass diode
cell_area = np.float64(246.49)  # [cm^2] cell area
Isc0_T0 = 9.68 # [A] reference short circuit current
ncols_per_substr=[2]*3 # 3 bypass diodes with 2 series connected cell-columns
nrows=10 # number of cell rows in the module
# Building PV modules and system
pv_mod_pattern = pvmodule.standard_cellpos_pat(nrows=nrows,
                                            ncols_per_substr=ncols_per_substr)
pv_mod = pvmodule.PVmodule(cell_pos=pv_mod_pattern, pvcells=None,
                           pvconst=None, Vbypass=v_bypass, cellArea=cell_area)
pv_cells = pv_mod.pvcells
for c in pv_cells:
    c.update(Isc0_T0 = Isc0_T0) # updating short circuit currents
pv_mod.setSuns(cells=list(range(0, len(pv_cells))), Ee=[1]*len(pv_cells))
pv_str = pvstring.PVstring(numberMods=str_len, pvmods=[pv_mod]*str_len)
pv_sys = pvsystem.PVsystem(numberStrs=str_num, pvstrs=[pv_str]*str_num,
                           numberMods=[str_len]*str_num,
                           pvmods=[pv_mod]*str_len)

# Create a human-readable xls of the pv system layout with the PV cell indexes
# irradiances and temperatures
output_xls_name=r'ExcelLayoutFromPVMM.xlsx' # the mod. & sys. layout in xls
xlsio.system_layout_to_xls(output_xls_name, pv_sys, write_bpd_act=False)
print('PV power with 1 suns: ', pv_sys.calcSystem()[2].max(), ' [W]')
plot = pv_sys.plotSys()
plt.show(block=False)

# Set now the desired irradiance input in the xls files with some xls editor

# After a human has changed the irradiance values for the system in the xls
# and saved it with a different name, we can read the new irradiance back to
# python anc calculate PV power again. Then we update the xls files with the
# bypass diode activation patterns, as this can only be done after the system
# is calculated.

for i in list(range(1,7)):
    input_xls_name=r'ExcelLayoutFromPVMM_input{}.xlsx'.format(i)
    xlsio.set_input_from_xls(input_xls_name, pv_sys, str_num, str_len)
    print('PV power with irradiances read in from {}: '.format(input_xls_name),
          pv_sys.calcSystem()[2].max(), ' [W]')
    # updating the input excel with the bypass diode activation
    xlsio.system_layout_to_xls(output_xls_name=input_xls_name, pv_sys=pv_sys,
                               write_bpd_act=True)
    pv_sys.plotSys()
    plt.show(block=False)
