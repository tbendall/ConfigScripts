#!/usr/bin/python3

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__     = "v0.3"

"""peerprefixes.py: Script to interrogate each supplied PE and return prefixes learnt from non-IBGP neighbors"""

from jnpr.junos import Device
from jnpr.junos.factory import loadyaml
from os.path import splitext
from prettytable import PrettyTable
import sys
import getpass

_YAML_ = splitext(__file__)[0] + '.yml'

globals().update(loadyaml(_YAML_))

def main(*args):

    username = input("Enter username (blank for default): ")

    entered_pass = getpass.getpass()

    devices = sys.argv[1:]

    if len(devices) == 0:

        print("Not enough PEs!")

        sys.exit(0)

    for device in devices:

        try:

            with Device(host=device, user=username, passwd="{0}".format(entered_pass), port=22) as dev:

                bgp = BgpNeigh(dev).get()

        except Exception as e:

            print("Please try again - ",e)

            sys.exit(0)

        table = PrettyTable(["Peer", "State", "Peer-AS", "Received Prefixes", "RIB", "Description"])
        table.align = ("l")

        sbgp = sorted(bgp,key=lambda item:item['received-prefix'],reverse=True)

        for i in sbgp:

            table.add_row([i['Neig'],i['state'],i['AS'],i['received-prefix'], i['bgpRib'],i['description']])

        print(table)


if __name__ == "__main__":

    main(sys.argv[0])

