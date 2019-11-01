# PVMismatchXLSIO
Excel-Python Irradiance I/O tool for [PVMismatch](https://github.com/SunPower/PVMismatch).

# Features
* Creating a human-readable xls of the PV system layout from a PVMismatch PVsystem object with the PV cell indexes, irradiances and temperatures.
* Reading human-readable irradiance and temperature input from an xls file to PVMismatch.

![](example_workflow/IrradTemperatureInput.PNG "irradiance and temperature input in excel")
* Writing human-readable indication of bypass-diode activation and reverse-biased cells (assuming the system operates at MPP). Reverse biased cells are indicated with 1 (red), bypassed cells are indicated with 2 (blue).

![](example_workflow/BypassDiodeAndReverseBiasedCellsOutput.PNG "output in excel")


# Tutorial
Overview of usage:
![](example_workflow/xlsio_workflow_chart.PNG "workflow")

See example_workflow.ipynb jupyter notebook in the example_workflow folder.
To start it:

* clone or copy this repository to your computer
* open a terminal window and navigate to the example_workflow folder in the cloned repository
* type: jupyter notebook example_workflow.ipynb

Alternatively, you can open and run (from the same location) the example_workflow.py file.
