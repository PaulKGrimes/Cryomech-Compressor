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
import argparse
import wsma_cryostat_compressor

default_ip = '192.168.42.100'

parser = argparse.ArgumentParser(description="Get current state variables from the compressor's "
                                             "digital control panel.")

parser.add_argument("-v", "--verbosity", action="store_true",
                    help="Display detailed output from compressor")
parser.add_argument("-a", "--address", default=default_ip,
                    help="The IP address of the compressor")


def main(args=None):
    args = parser.parse_args(args=args)

    # Create the selector wheel object for communication with the controller
    # If address is 0.0.0.0, create a dummy selector for testing purposes.
    if args.address=="0.0.0.0":
        comp = wsma_cryostat_compressor.DummyCompressor()
    else:
        comp = wsma_cryostat_compressor.Compressor(ip_address=args.address)

    print("Compressor state    : {}".format(comp.state))
    print("Compressor enabled  : {}".format(comp.enabled))
    print("Compressor warnings : {}".format(comp.warnings))
    print("Compressor errors   : {}".format(comp.errors))
    if args.verbosity:
        print("Coolant In          : {} {}".format(comp.coolant_in, comp.temp_unit))
        print("Coolant Out         : {} {}".format(comp.coolant_out, comp.temp_unit))
