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
__version__ = '0.1.0'

import argparse
import wsma_cryostat_compressor

default_ip = '192.168.42.128'

parser = argparse.ArgumentParser(description="Communicate with a Cryomech compressor's "
                                             "digital control panel.")

parser.add_argument("-v", "--verbosity", action="store_true",
                    help="Display detailed output from compressor")
parser.add_argument("-a", "--address", default=default_ip,
                    help="The IP address of the compressor")
group = parser.add_mutually_exclusive_group()
group.add_argument("--on", action="store_true", help="Turn the compressor on")
group.add_argument("--off", action="store_true", help="Turn the compressor off")


def main(args=None):
    args = parser.parse_args(args=args)

    # Create the compressor object for communication with the controller
    # If address is 0.0.0.0, create a dummy compressor for testing purposes.
    if args.address == "0.0.0.0":
        print(args)
        return None
        # comp = wsma_cryostat_compressor.DummyCompressor()
    else:
        comp = wsma_cryostat_compressor.Compressor(ip_address=args.address)

        if args.verbosity:
            comp.verbose = True

        if args.off:
            if comp.state_code == 0:
                print("{} compressor {} at {} is already off".format(comp.model, comp.serial, comp.ip_address))
            elif comp.state_code == 5:
                print("{} compressor {} at {} is already stopping".format(comp.model, comp.serial, comp.ip_address))
            elif comp.state_code == 2:
                print("{} compressor {} at {} is still starting, please try again later".format(comp.model,
                                                                                                comp.serial,
                                                                                                comp.ip_address))
            else:
                try:
                    print("Turning {} compressor {} at {} off".format(comp.model, comp.serial, comp.ip_address))
                    comp.off()
                except RuntimeError:
                    print("Could not turn compressor off")
                    print("")
                    print("State: {}".format(comp.state))
                    print("Errors:")
                    print(" \n".join(comp.errors.split(",")))
            if args.verbosity:
                print()
                print(comp.status)

        elif args.on:
            if comp.state_code == 2 or comp.state_code == 3:
                print("{} compressor {} at {} is already on".format(comp.model, comp.serial, comp.ip_address))
            elif comp.state_code != 0:
                print("{} compressor {} at {} cannot start at this time".format(comp.model,
                                                                                comp.serial, comp.ip_address))
            else:
                print("Turning {} compressor {} at {} on".format(comp.model, comp.serial, comp.ip_address))
                try:
                    comp.on()
                except RuntimeError:
                    print("Could not turn compressor on")
                    print("")
                    print("State: {}".format(comp.state))
                    print("Errors:")
                    print(" \n".join(comp.errors.split(",")))
            if args.verbosity:
                print()
                print(comp.status)

        else:
            print(comp)
