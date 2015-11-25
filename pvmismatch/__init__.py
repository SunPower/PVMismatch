# -*- coding: utf-8 -*-
"""
This is the PVMismatch Package. It contains :mod:`~pvmismatch.pvmismatch_lib`
and :mod:`~pvmismatch.pvmismatch_tk`.

:mod:`~pvmismatch.pvmismatch_lib`
=================================
This package contains the basic library modules, methods, classes and
attributes to model PV system mismatch.

.. note::
   The main library classes and modules are exposed through this package for
   convenience.

   For example::

       >>> from pvmismatch import PVcell  # imports the PVcell class
       >>> # import pvconstants, pvcell, pvmodule, pvstring and pvsystem
       >>> from pvmismatch import *

:mod:`~pvmismatch.pvmismatch_tk`
================================
This package contains an application that can be run using
:mod:`pvmismatch.pv_tk`.
"""

# import pvmismatch_lib modules so to match old API
import pvmismatch.pvmismatch_lib.pvconstants as pvconstants
import pvmismatch.pvmismatch_lib.pvcell as pvcell
import pvmismatch.pvmismatch_lib.pvmodule as pvmodule
import pvmismatch.pvmismatch_lib.pvstring as pvstring
import pvmismatch.pvmismatch_lib.pvsystem as pvsystem
import pvmismatch.pvmismatch_lib.pvexceptions as pvexceptions

# expose constructors to package's top level
PVconstants = pvconstants.PVconstants
PVcell = pvcell.PVcell
PVmodule = pvmodule.PVmodule
PVstring = pvstring.PVstring
PVsystem = pvsystem.PVsystem

__author__ = 'mmikofski'
__version__ = '2.2rc2'
__release__ = 'Indian Icecream'
__all__ = ['pvconstants', 'pvcell', 'pvmodule', 'pvstring', 'pvsystem']
