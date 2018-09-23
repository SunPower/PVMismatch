.. PVMismatch documentation master file, created by
   sphinx-quickstart on Thu Dec 05 12:49:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PVMismatch's documentation!
======================================

Version: |version| (|release|)


Announcements
-------------
Thanks to Bennet Meyers you should see huge memory and speed improvements since
new cell, module and string objects are only created when they are needed to
differentiate cells by irradiance or temperature. However this can lead to
unexpected behavior when changing other cell properties without first making a
copy of the original cell.


Contents:
---------

.. toctree::
   :maxdepth: 2

   tutorials/quickstart
   api/api
   api/pvconstants
   api/pvcell
   api/pvmodule
   api/pvstring
   api/pvsystem
   api/contrib


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

