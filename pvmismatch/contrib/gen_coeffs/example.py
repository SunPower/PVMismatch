"""
Generate coefficients example.
"""

from pvmismatch.contrib import gen_coeffs
from pvmismatch import *
from matplotlib import pyplot as plt
import numpy as np

# read module from PVLIB dictionary of SAPM modules
PROD_NAME = 'SunPower_SPR_E20_435'
NS = gen_coeffs.PVMODULES[PROD_NAME]['Cells_in_Series']  # number of series cells
NP = gen_coeffs.PVMODULES[PROD_NAME]['Parallel_Strings']  # number of parallel substrings
ISC0 = gen_coeffs.PVMODULES[PROD_NAME]['Isco']  # short circuit current [A]
VOC0 = gen_coeffs.PVMODULES[PROD_NAME]['Voco']  # open circuit voltage [A]
IMP0 = gen_coeffs.PVMODULES[PROD_NAME]['Impo']  # max power current [A]
VMP0 = gen_coeffs.PVMODULES[PROD_NAME]['Vmpo']  # max power voltage [V]
AISC = gen_coeffs.PVMODULES[PROD_NAME]['Aisc']  # short circuit current tempco [1/K]
PMP0 = IMP0 * VMP0
TC, IRR = gen_coeffs.TEST_MAT
T0, E0 = 25.0, 1000.0

iec61853 = gen_coeffs.gen_iec_61853_from_sapm(gen_coeffs.PVMODULES[PROD_NAME])
iec61853['i_mp'] = iec61853['p_mp'] / iec61853['v_mp']
#isc0, alpha_isc = gen_coeffs.gen_sapm(iec61853)
x, sol = gen_coeffs.gen_two_diode(ISC0, VOC0, IMP0, VMP0, NS, NP, T0)
#x, sol = gen_coeffs.gen_two_diode(
#    iec61853['i_sc'], iec61853['v_oc'], iec61853['i_mp'],
#    iec61853['v_mp'], NS, NP, tc=TC, method='lm',
#    x0=(2.25e-11, 1.5e-6, 0.004, 10.0)
#)
isat1, isat2, rs, rsh = x

pvc = pvcell.PVcell(
    Rs=rs, Rsh=rsh, Isat1_T0=isat1, Isat2=isat2,
    Isc0_T0=ISC0/NP, alpha_Isc=AISC
)
f1 = plt.figure()

for m, _tc in enumerate(gen_coeffs.TC_C):
    pvc.Tcell = _tc + 273.15
    plt.subplot(2, 2, m+1)
    plt.xlim([0, 0.8])
    plt.ylim([0, 8])
    res_norm = 0
    for n, _irr in enumerate(gen_coeffs.IRR_W_M2):
        pvc.Ee = _irr / 1000.0
        plt.plot(pvc.Vcell, pvc.Icell, '-', pvc.Vcell, pvc.Pcell, ':')
        plt.plot(
            iec61853['v_mp'][n][m]/NS, iec61853['i_mp'][n][m]/NP, 'x',
            iec61853['v_oc'][n][m]/NS, 0.0, 'x',
            0.0, iec61853['i_sc'][n][m]/NP, 'x',
            iec61853['v_mp'][n][m]/NS, iec61853['p_mp'][n][m]/NS/NP, 'o',
        )
        res_norm += (
            pvc.calcIcell(iec61853['v_mp'][n][m]/NS)
            - iec61853['i_mp'][n][m]/NP
        )**2 / (iec61853['i_mp'][n][m]/NP)**2
        res_norm += (
            pvc.calcVcell(iec61853['i_mp'][n][m]/NP)
            - iec61853['v_mp'][n][m]/NS
        )**2 / (iec61853['v_mp'][n][m]/NS)**2
        res_norm += (
            pvc.calcVcell(0.0) - iec61853['v_oc'][n][m]/NS
        )**2 / (iec61853['v_oc'][n][m]/NS)**2
        res_norm += (
            pvc.calcIcell(0.0) - iec61853['i_sc'][n][m]/NP
        )**2 / (iec61853['i_sc'][n][m]/NP)**2
        rel_diff = (pvc.Pcell.max()*NS*NP - iec61853['p_mp'][n][m]) / PMP0
        plt.annotate('$\Delta_{rel}$ = %.2g%%' % (rel_diff*100),
                     (0.65, iec61853['p_mp'][n][m]/NS/NP))
    plt.annotate('norm of residuals = %g' % np.sqrt(res_norm / (7*4)),
                 (0.5, 7.5))
    plt.grid(True)
    plt.title(
        'PVMismatch Generated Coefficients for %s at Tc = %g' % (PROD_NAME, _tc)
    )
    plt.xlabel('voltage')
    plt.ylabel('current [A]')
    plt.xlabel('voltage [V]')
f1.show()
