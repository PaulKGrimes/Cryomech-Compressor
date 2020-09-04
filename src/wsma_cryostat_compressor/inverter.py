__version__ = '0.1.1'

from time import sleep
import asyncio
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

default_port = "COM3"

