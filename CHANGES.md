CHANGES
=======

v2.2 Indian Icecream
--------------------
* Fixes #21 - created a contrib folder for examples
* Fixes #25 - add quadratic parameter `bRBD` to model soft breakdown
* Fixes #20 - change hard coded cell position patterns to realistic examples of
TCT and PCT modules.

v2.1 Himalayan Ham
------------------
* fixes #17

v2.0 Himalayan Honey
--------------------
* fixes issues #11, #12, #13 and #14
* create partial and total crosstied modules
* separate pvcells from pvconstants so that every cell properties can change
* add documentation and testing
* removes `parallel_calcs.py` module

v1.6 German Goulash
-------------------
* Fix setup to install all packages together by creating main project package.
* Renamed `pvmismatch` to `pvmismatch_lib`
* Move all packages inside new `pvmismatch` top level package
* Also move package data and documentation into new top level package
* **Note: Any imports that use `pvmismatch.pvconstants`, `pvmismatch.pvmodule`,
`pvmismatch.pvstring` or `pvmismatch.pvsystem` will no longer work.**
* Instead use `from pvmismatch import pvconstants`, `from pvmismatch import
pvmodule`, `from pvmismatch import pvstring` or `from pvmismatch import
pvsystem`
* For convenience you can use `from pvmismatch import *` to import all four
main modules
* Constructors are also exposed to top level package, for example can use
  `from pvmismatch import PVsystem`

v1.5 French Falafel
-------------------
* bug fixes
* corrects pt spacing for module current
* simplifies Istring calc
* multithreading of some pvsys and pvstring calcs
* TODO multithread calcMod if possible
* benchmarked vs older code
* pretty up & optimize code

v1.4.1 European Eclair
----------------------
* bug fix PVconstants use self.npts, not NPTS!
* remove commented legacy code

v1.4 European Eggplant
----------------------
* Isc0 is also temp dependent but rename Isc0 to Isc0_T0
and Isat1 to Isat1_T0
* add alpha_Isc input arg to PVconstants
* cast all pvconst inputs to float to avoid integer errors
* fix advCnf to use Isc0_T0 and Isat1_T0
* in PVconstants.update() check for Isat1, Isc0, Eg,
alpha_Isc and Tcell
* add calc_Isat1 and calc_Isc0 functions

v1.3.1 Danish Delicatessen
--------------------------
* Isat1 temperature dependence
* add Eg, band gap energy
* set default npts to 101, let user specify to constructor
* change pts to be logspace

v1.3 Danish Donuts
------------------
* pvmismatch_tk has advanced configuration button to set nearly all
diode model parameters
* pvmodules, pvstring and pvsystem all use deepcopy to make cheap copies
of modules, instead of looping over and constructing every module
individually - huge time savings
* bug fixes: be 163/123 increase range of Imod & Istr for Ee > 1 sun, be
163/9e9 temp dep, be 163/069 hook up all widgets on main screen
* move validation const & messages to json files
* add pvexceptions
* add waitbox during long actions and startup
* numerous improvements

v1.2 Canadian Cheese
--------------------
* main app page completely refactored
* matplotlib graph of system IV curve on main page
* only set strings, modules/string & cells/module
* all validation limits to integers and max value
* string button
* scale connected to I, V & P entry output
* TODO: entry widegt should be 2 way with scale
* TODO: scale and entry widgets should move cursor on plot
*	see cursor example on matplotlib
* TODO: use asynchronous thread to show progress bar during calculations
* TODO: still need to hook up other buttons
* TODO: other screens
* TODO: advanced settings button
* TODO: temp dependent Isat's and R's

v1.1 Belgian Banana
-------------------
* Tkinter front end
* input all variables, some validation
* reset, load, save, quit
* separate buttons to view results
* TODO: make results buttons work
* TODO: connect to pvmismatch
* TODO: validaton actually limits to correct ranges
* TODO: validation allows deletions and insertions

v1.0 Appalachian Apple
----------------------
* 2-diode model
* avalanche reverse bias and breakdown characteristics
* composed of pvmodule, pvstring and pvsystem
* testscript creates output in testPV folder
* bypass diodes simply represented by trigger voltage
* extrapolation used out of range, could pose problems
* noJac temperature, ie assumed explicit
* TODO: add max power function, return I,V,P
* TODO: create user interface
* TODO: register event so update is automatic
* TODO: test bypass diodes, extrapolation and other corner cases