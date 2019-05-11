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

import os
import importlib

# try to import Dulwich or create dummies
try:
    from dulwich.contrib.release_robot import get_current_version
    from dulwich.repo import NotGitRepository
except ImportError:
    NotGitRepository = NotImplementedError

    def get_current_version(*args, **kwargs):
        raise NotGitRepository

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

# Dulwich Release Robot
BASEDIR = os.path.dirname(__file__)  # this directory
PROJDIR = os.path.dirname(BASEDIR)
VER_FILE = 'version'  # name of file to store version
# use release robot to try to get current Git tag
try:
    GIT_TAG = get_current_version(PROJDIR)
except NotGitRepository:
    GIT_TAG = None
# check version file
try:
    version = importlib.import_module('%s.%s' % (__name__, VER_FILE))
except ImportError:
    VERSION = None
else:
    VERSION = version.VERSION
# update version file if it differs from Git tag
if GIT_TAG is not None and VERSION != GIT_TAG:
    with open(os.path.join(BASEDIR, VER_FILE + '.py'), 'w') as vf:
        vf.write('VERSION = "%s"\n' % GIT_TAG)
else:
    GIT_TAG = VERSION  # if Git tag is none use version file
VERSION = GIT_TAG  # version

__author__ = 'Mark Mikofski'
__email__ = u'mark.mikofski@sunpowercorp.com'
__url__ = u'https://github.com/SunPower/PVMismatch'
__version__ = VERSION
__release__ = 'Nepal Negroni'
__all__ = ['pvconstants', 'pvcell', 'pvmodule', 'pvstring', 'pvsystem']
