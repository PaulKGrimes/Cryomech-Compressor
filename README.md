# Cryomech-Compressor
Python module for communicating with a Cryomech Helium Compressor over Modbus

Requires PyModbus <= 2.5.3 at this time.

Version: v0.1.1.

This Python module adds two command line programs to the Python environment that can read the status and control the comressor and inverter - `compressor` and `inverter`.  Use the `-h` flag for help on using these progras

This code has been tested with a Cryomech CP289i compressor with inverter, using ethernet communication to the compressor and a ethernet to RS-485 adapter with the inverter.
