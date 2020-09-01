__version__ = '0.0.0'

from time import sleep
from pymodbus.client.sync import ModbusTcpClient

default_IP = "192.168.0.105"


class Compressor(object):
    """Class for communicating with the wSMA Compressor controller.

    The Compressor object wraps a pymodbus.ModbusTcpClient instance which
    communicates with the Compressor Digital Panel over TCP/IP.
    """
    #: int: address of the controller's operating state register.
    #       values are one of:
    #           0: Idling - ready to start
    #           2: Starting
    #           3: Running
    #           5: Stopping
    #           6: Error lockout
    #           7: Error
    #           8: Helium cool down
    #           9: Power related error
    #           15: Recovered from error
    _operating_state_addr = 30001

    #: int: address of the controller's energized state register.
    #       values are one of:
    #           0: Off
    #           1: On
    _energized_addr = 30002

    #: int: address of the controller's warning register.
    #       values are an OR of:
    #           0: No warnings
    #           -1: Coolant IN (Temp) running High
    #           -2: Coolant IN (Temp) running Low
    #           -4: Coolant OUT (Temp) running High
    #           -8: Coolant OUT (Temp) running High
    #           -16: Oil (Temp) running High
    #           -32: Oil (Temp) running Low
    #           -64: Helium (Temp) running High
    #           -128: Helium (Temp) running Low
    #           -256: Low Pressure running High
    #           -512: Low Pressure running Low
    #           -1024: High Pressure running High
    #           -2048: High Pressure running Low
    #           -4096: Delta Pressure running High
    #           -8192: Delta Pressure running Low
    #           -131072: Static Pressure running High
    #           -262144: Static Pressure running Low
    #           -524288: Cold head motor stall
    _warning_addr = 30003

    #: int: address of the controller's alarm/error register.
    #       values are an OR of:
    #           0: No errors
    #           -1: Coolant IN (Temp) running High
    #           -2: Coolant IN (Temp) running Low
    #           -4: Coolant OUT (Temp) running High
    #           -8: Coolant OUT (Temp) running High
    #           -16: Oil (Temp) running High
    #           -32: Oil (Temp) running Low
    #           -64: Helium (Temp) running High
    #           -128: Helium (Temp) running Low
    #           -256: Low Pressure running High
    #           -512: Low Pressure running Low
    #           -1024: High Pressure running High
    #           -2048: High Pressure running Low
    #           -4096: Delta Pressure running High
    #           -8192: Delta Pressure running Low
    #           -16384: Motor Current Low
    #           -32768: Three Phase Error
    #           -65536: Power Supply Error
    #           -131072: Static Pressure running High
    #           -262144: Static Pressure running Low
    #           -524288: Cold head motor stall
    _error_addr = 30005

    #: int: address of the controller's Coolant In Temp(erature) register
    #       values is a 32 bit floating point, in units given by Temp Unit register
    _coolant_in_addr = 30007

    #: int: address of the controller's Coolant Out Temp(erature) register
    #       values is a 32 bit floating point, in units given by Temp Unit register
    _coolant_out_addr = 30009

    #: int: address of the controller's Oil Temp(erature) register
    #       values is a 32 bit floating point, in units given by Temp Unit register
    _oil_temp_addr = 30011

    #: int: address of the controller's Helium Temp(erature) register
    #       values is a 32 bit floating point, in units given by Temp Unit register
    _helium_temp_addr = 30013

    #: int: address of the controller's Low Pressure register
    #       values is a 32 bit floating point, in units given by Pressure Unit register
    _low_press_addr = 30015

    #: int: address of the controller's Low Pressure Average register
    #       values is a 32 bit floating point, in units given by Pressure Unit register
    _low_press_avg_addr = 30017

    #: int: address of the controller's High Pressure register
    #       values is a 32 bit floating point, in units given by Pressure Unit register
    _high_press_addr = 30019

    #: int: address of the controller's High Pressure Average register
    #       values is a 32 bit floating point, in units given by Pressure Unit register
    _high_press_avg_addr = 30021

    #: int: address of the controller's Delta Pressure Average register
    #       values is a 32 bit floating point, in units given by Pressure Unit register
    _delta_press_avg_addr = 30023

    #: int: address of the controller's Motor Current register
    #       value is a 32 bit floating point, in Amps
    #       Value is known to be garbage on CP286i - use value from inverter
    _motor_current_addr = 30025

    #: int: address of the controller's Hours of Operation register
    #       value is a 32 bit floating point, in hours.
    _hours_addr = 300027

    #: int: address of the controller's Pressure Scale register
    #       value is a 16 bit int
    #       values are:
    #           0: PSI
    #           1: Bar
    #           2: KPA
    _press_unit_addr = 30029

    #: int: address of the controller's Temperature Scale register
    #       values are 16 bit ints:
    #           0: Farenheit
    #           1: Celsius
    #           2: Kelvin
    _temp_unit_addr = 30030

    #: int: address of the controller's Enable/Disable register
    #       values are 16 bit ints:
    #           0x00FF: turn the compressor OFF
    #           0x0001: turn the compressor ON
    _enable_addr = 40001

    def __init__(self, ip_address=default_IP):
        """Create a Compressor object for communication with one Compressor Digital Panel controller.

        Opens a Modbus TCP connection to the Compressor Digital Panel controller at `ip_address`, and reads the
        current state.

        Args:
            ip_address (str): IP Address of the controller to communicate with
        """
        #: (:obj:`ModbusTcpClient`): Client for communicating with the controller
        self._client = ModbusTcpClient(ip_address)

        #: int: Current state of the compressor
        #       values are one of:
        #           0: Idling - ready to start
        #           2: Starting
        #           3: Running
        #           5: Stopping
        #           6: Error lockout
        #           7: Error
        #           8: Helium cool down
        #           9: Power related error
        #           15: Recovered from error
        self._state = self.get_state()

        #: int: Current power state of the compressor
        #       values are one of:
        #           0: Off
        #           1: On
        self._enabled = self.get_enabled()

        #: int: Current warning state of the compressor
        #       values are an OR of:
        #           0: No warnings
        #           -1: Coolant IN (Temp) running High
        #           -2: Coolant IN (Temp) running Low
        #           -4: Coolant OUT (Temp) running High
        #           -8: Coolant OUT (Temp) running High
        #           -16: Oil (Temp) running High
        #           -32: Oil (Temp) running Low
        #           -64: Helium (Temp) running High
        #           -128: Helium (Temp) running Low
        #           -256: Low Pressure running High
        #           -512: Low Pressure running Low
        #           -1024: High Pressure running High
        #           -2048: High Pressure running Low
        #           -4096: Delta Pressure running High
        #           -8192: Delta Pressure running Low
        #           -131072: Static Pressure running High
        #           -262144: Static Pressure running Low
        #           -524288: Cold head motor stall
        self._warnings = self.get_warnings()

        #: int: Current Error state of the compressor
        #       values are an OR of:
        #           0: No warnings
        #           -1: Coolant IN (Temp) running High
        #           -2: Coolant IN (Temp) running Low
        #           -4: Coolant OUT (Temp) running High
        #           -8: Coolant OUT (Temp) running High
        #           -16: Oil (Temp) running High
        #           -32: Oil (Temp) running Low
        #           -64: Helium (Temp) running High
        #           -128: Helium (Temp) running Low
        #           -256: Low Pressure running High
        #           -512: Low Pressure running Low
        #           -1024: High Pressure running High
        #           -2048: High Pressure running Low
        #           -4096: Delta Pressure running High
        #           -8192: Delta Pressure running Low
        #           -16384: Motor Current Low
        #           -32768: Three Phase Error
        #           -65536: Power Supply Error
        #           -131072: Static Pressure running High
        #           -262144: Static Pressure running Low
        #           -524288: Cold head motor stall
        self._errors = self.get_errors()

        # float: Coolant IN temperature in self._temp_units
        self._coolant_in = self.get_coolant_in_temp()

        # float: Coolant OUT temperature in self._temp_units
        self._coolant_out = self.get_coolant_out_temp()

        # float: Oil temperature in self._temp_units
        self._oil_temp = self.get_oil_temp()

        # float: Helium temperature in self._temp_units
        self._helium_temp = self.get_helium_temp()

        # float: Low pressure in self._press_units
        self._low_press = self.get_low_press()

        # float: Low pressure average in self._press_units
        self._low_press_avg = self.get_low_press_avg()

        # float: High pressure in self._press_units
        self._high_press = self.get_high_press()

        # float: High pressure average in self._press_units
        self._high_press_avg = self.get_high_press_avg()

        # float: Delta pressure average in self._press_units
        self._delta_press_avg = self.get_delta_press_avg()

        # float: Motor current in Amps - ! Known to be garbage on CP286i
        self._motor_current = self.get_motor_current()

        # float: Hours of Operation
        self._hours = self.get_hours()

        # int: Pressure unit
        #       values are:
        #           0: PSI
        #           1: Bar
        #           2: KPA
        self._press_unit = self.get_press_unit()

        # int: Temperature unit
        #       values are:
        #           0: Farenheit
        #           1: Celsius
        #           2: Kelvin
        self._temp_unit = self.get_temp_unit()

        # int: how long to wait before checking that compressor enable/disable
        #       command worked
        self._enable_delay


    @property
    def state(self):
        """int: State of the compressor.
            values are one of:
                    0: Idling - ready to start
                    2: Starting
                    3: Running
                    5: Stopping
                    6: Error lockout
                    7: Error
                    8: Helium cool down
                    9: Power related error
                    15: Recovered from error"""
        return self._state

    @property
    def enabled(self):
        """int: Enable state of the compressor.
            values are one of:
                0: Off
                1: On"""
        return self._enabled

    @property
    def warnings(self):
        """int: Warning state of the compressor.
            values are an OR of:
                0: No warnings
                -1: Coolant IN (Temp) running High
                -2: Coolant IN (Temp) running Low
                -4: Coolant OUT (Temp) running High
                -8: Coolant OUT (Temp) running High
                -16: Oil (Temp) running High
                -32: Oil (Temp) running Low
                -64: Helium (Temp) running High
                -128: Helium (Temp) running Low
                -256: Low Pressure running High
                -512: Low Pressure running Low
                -1024: High Pressure running High
                -2048: High Pressure running Low
                -4096: Delta Pressure running High
                -8192: Delta Pressure running Low
                -131072: Static Pressure running High
                -262144: Static Pressure running Low
                -524288: Cold head motor stall
        """
        return self._warnings

    @property
    def errors(self):
        """int: Warning state of the compressor.
            values are an OR of:
                0: No errors
                -1: Coolant IN (Temp) running High
                -2: Coolant IN (Temp) running Low
                -4: Coolant OUT (Temp) running High
                -8: Coolant OUT (Temp) running High
                -16: Oil (Temp) running High
                -32: Oil (Temp) running Low
                -64: Helium (Temp) running High
                -128: Helium (Temp) running Low
                -256: Low Pressure running High
                -512: Low Pressure running Low
                -1024: High Pressure running High
                -2048: High Pressure running Low
                -4096: Delta Pressure running High
                -8192: Delta Pressure running Low
                -16384: Motor Current Low
                -32768: Three Phase Error
                -65536: Power Supply Error
                -131072: Static Pressure running High
                -262144: Static Pressure running Low
                -524288: Cold head motor stall
        """
        return self._errors

    @property
    def coolant_in(self):
        """float: Coolant IN temperature in self.temp_units"""
        return self._coolant_in

    @property
    def coolant_out(self):
        """float: Coolant OUT temperature in self.temp_units"""
        return self._coolant_out


    def get_state(self):
        """Read the current state of the compressor.

        Returns:
            int: current state of the compressor."""
        r = self._client.read_input_registers(self._state_addr)
        if r.isError():
            raise RuntimeError("Could not get current state")
        else:
            self._state = r.registers[0]
            return self.state

    def get_enabled(self):
        """Read the current Enable state of the compressor.

        Returns:
            int: current Enable state of the compressor."""
        r = self._client.read_input_registers(self._enabled_addr)
        if r.isError():
            raise RuntimeError("Could not get current state")
        else:
            return r.registers[0]

    def get_warnings(self):
        """Read the current warnings from the compressor.

        Returns:
            int: warning state of the compressor."""
        r = self._client.read_input_registers(self._warning_addr)
        if r.isError():
            raise RuntimeError("Could not get warnings.")
        else:
            self._warnings = r.registers[0]
            return r.registers[0]

    def get_errors(self):
        """Read the current errors from the compressor.

        Returns:
            int: error state of the compressor."""
        r = self._client.read_input_registers(self._error_addr)
        if r.isError():
            raise RuntimeError("Could not get Errors.")
        else:
            self._errors = r.registers[0]
            return r.registers[0]


    def on(self):
        """Turn the compressor on."""
        w = self._client.write_registers(self._enable_addr, 0x0001)
        if w.isError():
            raise RuntimeError("Could not command compressor to turn on")
        else:
            sleep(self._enable_delay)
            enabled = self.get_enabled()
            if enabled != 1:
                error = self.get_errors()
                raise RuntimeError("Compressor did not turn on. Compressor Error Code {}".format(error))

    def off(self):
        """Turn the compressor off."""
        w = self._client.write_registers(self._enable_addr, 0x00FF)
        if w.isError():
            raise RuntimeError("Could not command compressor to turn off")
        else:
            sleep(self._enable_delay)
            enabled = self.get_enabled()
            if enabled != 0:
                raise RuntimeError("Compressor did not turn off")


class DummyCompressor(Compressor):
    """A dummy compressor that just stores information without attempting
    any communication, for testing purposes"""
    def __init__(self, ip_address="0.0.0.0"):
        """Create a DummyCompressor object for testing purposes.

        Args:
            ip_address (str): IP Address of the controller to communicate with
        """
        pass
