"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mwsma_cryostat_selector` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``wsma_cryostat_selector.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``wsma_cryostat_selector.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
__version__ = '0.1.1'

import argparse
import wsma_cryostat_compressor.inverter

default_port = 'COM3'

parser = argparse.ArgumentParser(description="Communicate with a Cryomech compressor's "
                                             "inverter.")

parser.add_argument("-v", "--verbosity", action="store_true",
                    help="Display detailed output from inverter")
parser.add_argument("-p", "--port", default=default_port,
                    help="The serial port connected to the inverter")
parser.add_argument("-f", "--freq", help="Frequency to set the inverter to", type=float)


def main(args=None):
    args = parser.parse_args(args=args)

    # Create the Inverter object for communication with the inverter.
    # If port is "Test", create a dummy invert for testing purposes.
    if args.port == "Test":
        print(args)
        return None
        # inv = wsma_cryostat_compressor.inverter.Dummy_Inverter()
    else:
        inv = wsma_cryostat_compressor.inverter.Inverter(port=args.port)

        if args.verbosity:
            inv.verbose = True

        if args.freq:
            try:
                inv.set_frequency(args.freq)
            except RuntimeError:
                    print("Could not set inverter frequency")
            if args.verbosity:
                print(inv)

        else:
            print(inv)