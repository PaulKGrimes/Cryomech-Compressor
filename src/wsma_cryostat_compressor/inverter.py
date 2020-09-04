__version__ = '0.1.1'

from time import sleep
import asyncio
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

default_port = "COM3"


class Inverter(object):
    """Class for communicating with the wSMA Compressor controller.

    The Compressor object wraps a pymodbus.ModbusTcpClient instance which
    communicates with the Compressor Digital Panel over TCP/IP.
    """
    #: int: address of the inverter's frequency holding register.
    _frequency_addr = 0x0001

    #: int: address of the inverter's output current monitor input register
    _current_addr = 0x1002

    #: int: address of the inverter's output voltage monitor input register
    _voltage_addr = 0x1011

    #: int: address of the inverter's output power monitor inpur register
    _power_addr = 0x1012

    #: int: unit address
    _unit_addr = 0x01

    def __init__(self, port=default_port):
        """Create an inverter object for communication with the inverter.

        Args:
            port: str: the RS485 port to talk on.
        """
        # set up the communications, however that works
        self._client = ModbusClient(port)

        #: str: serial port for the inverter.
        self._port = port

        #: int: the frequency of the inverter, in units of 0.01 Hz.
        self._frequency = 0

        #: int: the output current of the inverter in units of 0.1 A.
        self._current = 0

        #: int: the output voltage of the inverter in units of 0.1 V.
        self._voltage = 0

        #: int: the output power of the inverter in units of 0.1 kW.
        self._power = 0

        #: float: time to wait for frequency setting to be updated.
        self._set_delay = 1.0

        # Get the data from the inverter
        self.update()

    @property
    def frequency(self):
        """float: The frequency of the inverter in Hz.

        Read only - set the frequency via the set_frequency method."""
        return self._frequency * 0.01

    @property
    def current(self):
        """float: The output current of the inverter in Amps."""
        return self._current * 0.1

    @property
    def voltage(self):
        """float: The output voltage of the inverter in Volts."""
        return self._voltage * 0.1

    @property
    def power(self):
        """float: The output power of the inverter in kW."""
        return self._power * 0.1

    @property
    def port(self):
        """str: The port connected to the inverter."""
        return "{}, unit {}".format(self._port, self._unit_addr)

    def update(self):
        """Get updated values for all monitor values from the inverter"""
        self._get_frequency()
        self._get_current()
        self._get_voltage()
        self._get_power()

    def __repr__(self):
        """Brief description of the object."""
        return "wsma_cryostat_compressor.inverter.Inverter on serial port {}.".format(self._port)

    def __str__(self):
        """Print the stored state of the inverter."""
        if self.verbose:
            return self.status
        else:
            return "\n".join(("Inverter",
                              "Port      : {}".format(self.port),
                              "Frequency : {} Hz".format(self.frequency)))

    @property
    def status(self):
        """str: Detailed status of the inverter"""
        return "\n".join(("Inverter",
                          "Port      : {}".format(self.port),
                          "Frequency : {} Hz".format(self.frequency),
                          "Power     : {} kW".format(self.power),
                          "Current   : {} A".format(self.current),
                          "Voltage   : {} V".format(self.voltage)))

    def print_status(self):
        """Print all of the stored status"""
        print(self.status)

    def get_status(self):
        """Update the current state and print it"""
        self.update()
        self.print_status()

    def _get_frequency(self):
        """Get the current frequency from the inverter"""
        r = self._client.read_register(self._frequency_addr, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(r.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result = decoder.decode_16bit_int()
        self._frequency = result

    def _get_current(self):
        """Get the output current from the inverter"""
        r = self._client.read_register(self._current_addr, 1)
        self._current = r.registers[0]

    def _get_voltage(self):
        """Get the output voltage from the inverter"""
        r = self._client.read_register(self._voltage_addr, 1)
        self._voltage = r.registers[0]

    def _get_power(self):
        """Get the output power from the inverter"""
        r = self._client.read_register(self._power_addr, 1)
        self._power = r.registers[0]

    def _set_frequency(self, freq):
        """Set the output frequency of the inverter.

        Args:
            freq: int: Frequency to set in units of 0.01 Hz"""
        # munge frequency into two bytes
        self._client.write_register(self._frequency_addr, bytes)
        time.sleep(self._set_delay)
        self._get_frequency()

    def get_frequency(self):
        """Get current frequency from the inverter and return the value.

        Returns:
            float: Frequency in Hz."""
        self._get_frequency()
        return self.frequency

    def set_frequency(self, freq):
        """Set the inverter frequency.

        Args:
            freq: float: Inverter frequency in Hz."""
        f = int(freq * 100)
        if f > 7000 or f < 4000:
            raise ValueError("Cannot set inverter frequency outside the range of 40-70 Hz")
        else:
            self._set_frequency(f)

        return self.frequency

    def get_current(self):
        """Get the output current from the inverter and return the value.

        Returns:
            float: Current in Amps."""
        self._get_current()
        return self.current

    def get_voltage(self):
        """Get the output voltage from the inverter and return the value.

        Returns:
            float: Voltage in Volts."""
        self._get_voltage()
        return self.voltage

    def get_power(self):
        """Get the output power from the inverter and return the value.

        Returns:
            float: Power in kW."""
        self._get_power()
        return self.power
