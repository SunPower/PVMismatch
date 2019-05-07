"""
This script uses default Tiled module configuration and cell parameters to
calculate performance and generate IV and PV curves.
"""

from pvmismatch import *
import numpy as np
from matplotlib import pyplot as plt

if __name__ == "__main__":
    
    # Model parameters
    NPTS=5000  # Because of the high cell breakdown voltage, NPTS must be >1000
    
    # Cell parameters
    RS = 0.0181123  # [ohm] series resistance
    RSH = 58.082  # [ohm] shunt resistance
    ISAT1_T0 = 2.9885E-11  # [A] diode one saturation current
    ISAT2_T0 = 1.6622E-07  # [A] diode two saturation current
    ISC0_T0 = 1.437  # [A] reference short circuit current
    ARBD = 9.0E-4  # reverse breakdown coefficient 1
    BRBD = -0.056  # reverse breakdown coefficient 2
    VRBD_ = -25.1  # [V] reverse breakdown voltage
    NRBD = 4.0  # reverse breakdown exponent
    EG = 1.166  # [eV] band gap of cSi
    ALPHA_ISC = 0.0003551  # [1/K] short circuit current temperature coefficient
    TCELL = 298.15  # [K] cell temperature
    CELLAREA = np.float64(38.064)  # [cm^2] cell area used for efficiency calculation
    
    # Module parameters
    VBYPASS = np.float64(-0.885)  # [V] trigger voltage of bypass diode
    NUMBERCOLS = 6  # number of hypercells per module
    
    # System parameters
    NUMBERMODS = 1  # number of modules per string
    NUMBERSTRS = 1  # number of strings in parallel
    
    # System definition
    tiledCell = pvcell.PVcell(Rs=RS, Rsh=RSH, Isat1_T0=ISAT1_T0, Isat2_T0=ISAT2_T0,
                    Isc0_T0=ISC0_T0, aRBD=ARBD, VRBD=VRBD_, bRBD=BRBD, 
                    nRBD=NRBD, Eg=EG, alpha_Isc=ALPHA_ISC,
                    Tcell=TCELL)
    tiledModule = pvmodule.PVmodule(cell_pos=pvmodule.PCT492, pvcells=tiledCell,
                    Vbypass=VBYPASS, cellArea=CELLAREA)  # Tiled module with partial cross-ties
    tiledSystem = pvsystem.PVsystem(pvconst=pvconstants.PVconstants(npts=NPTS),
                    pvmods=tiledModule, numberStrs=NUMBERSTRS, numberMods=NUMBERMODS)
    
    print('Imp = ' + str(tiledSystem.Imp) + ' A')
    print('Vmp = ' + str(tiledSystem.Vmp) + ' V')
    print('Pmp = ' + str(tiledSystem.Pmp) + ' W')
    print('Isc = ' + str(tiledSystem.Isc) + ' A')
    print('Voc = ' + str(tiledSystem.Voc) + ' V')
    print('FF = ' + str(100*tiledSystem.FF) + ' %')
    print('Efficiency = ' + str(100*tiledSystem.eff) + ' %')
    figure = tiledSystem.plotSys()
    plt.show()
