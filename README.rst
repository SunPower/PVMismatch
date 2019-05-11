PVMismatch
==========

An explicit IV & PV curve trace calculator for PV system circuits

Model chain 
    Cell > Cell string > Module > String > System
    
Key Model inputs 
    Cell technology characteristics 
    
    Effective Irradiance (suns) 
    
    Temperature (cell temperature)
    
    Bypass device configuration
    
    Cell string layout



|Build Status|

Installation
------------

PVMismatch is on `PyPI <https://pypi.python.org/pypi/pvmismatch>`__. Install it
with `pip <https://pip.pypa.io/en/stable/>`__:

::

    $ pip install pvmismatch

Requirements
------------

PVMismatch requires NumPy, SciPy and matplotlib. These packages are available
from PyPI, `Christoph Gohlke <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`__
and Anaconda. You must install them prior to using PVMismatch.

Usage
-----

Please see the `documenation <http://sunpower.github.io/PVMismatch/>`__ for
tutorials and API. Bugs and feature requests can be reported on
`GitHub <https://github.com/SunPower/PVMismatch/issues>`__. The change
history is also on `GitHub <https://github.com/SunPower/releases/>`__.

.. |Build Status| image:: https://travis-ci.org/SunPower/PVMismatch.svg?branch=master
   :target: https://travis-ci.org/SunPower/PVMismatch

Other Projects that use PVMismatch
----------------------------------
System level mismatch loss calculator using PVMismatch tool (STC and Annual energy loss)
https://github.com/SunPower/MismatchLossStudy 

Citing PVMismatch
----------------------------------
We appreciate your use of PVMismatch, and ask that you appropriately cite the software in exchange for its open-source publication. 

Mark Mikofski, Bennet Meyers, Chetan Chaudhari (2018). “PVMismatch Project: https://github.com/SunPower/PVMismatch". SunPower Corporation, Richmond, CA.
