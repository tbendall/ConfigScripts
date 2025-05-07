#!/usr/bin/python3

""" config_load.py: A Python script using Junos-PYEZ to load, diff and commit configuration on NETCONF enabled devices """

__author__	  = "Tristan Bendall/tristan@bendall.co" 
__version__	 = "v1.0"

import json
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import ConnectAuthError
import re
from lxml import etree as ET
import os
import getpass
import argparse
import sys

hosts = [

### Hosts go here

]

config_file = '< path to set config >' 

diff_results_path = "< path to diff results path >" 

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-d','--development', type=str)
arg_parser.add_argument('-c','--commit', type=str)
arg_parser.add_argument('-k','--check', type=str)

globals().update(vars(arg_parser.parse_args()))


username = input("Enter username (blank for default): ")

entered_pass = getpass.getpass()

def opener(path,flags):

    return os.open(path, flags, 0o660)

def config_check():

        ## Run a commit check to end the commit-confirmed period - will also check if connectivity works
    for i in hosts:

        result = {}

        result[i] = {}

        dev = Device(host=i,user=username,passwd=entered_pass,port=22,timeout=5)

        try:

            dev.open()

        except Exception as e:

            print(i,e)

            continue            

        try:

            with Device(host=i,user=username,passwd=entered_pass,port=22) as dev:

                with Config(dev, mode='exclusive') as cu:

                    try:

                        cu.load(config_file, format='set')

                    except ConfigLoadError as e:

                        print(e)

                        if e.errs[0]["severity"] == "warning":

                            pass

                        else:

                            sys.exit()

                    try:

                        cu.commit_check(timeout=60)

                    except Exception as e:

                        result[i]["commit_check"] = e

                        print(e)

                        sys.exit()

                print("{0} config has checked OK".format(i))

        except ConnectAuthError as e:

            print(i," - ", e)
            
            sys.exit()

def main(*args):

    result = {}
    
    with open(config_file,"r") as f:

        file_config = f.read()

    for i in hosts:

        result[i] = {}

        dev = Device(host=i,user=username,passwd=entered_pass,port=22,timeout=5)

        try:

            dev.open()

        except Exception as e:

            print(i,e)

            continue            

        with Device(host=i,user=username,passwd=entered_pass,port=22) as dev:
            
                with Config(dev, mode='exclusive') as cu:

                    try:

                        cu.load(file_config, format='set')

                    except ConfigLoadError as e:

                        print(e)

                        if e.errs[0]["severity"] == "warning" or e.errs[0]["severity"] == "error":

                            pass

                        else:

                            sys.exit()
                        
                    result[i]["diff"] = cu.diff(rb_id=0)

                    try:

                        cu.commit_check(timeout=60)
                    
                    except Exception as e:

                        result[i]["commit_check"] = e

                        print(e)

                        sys.exit()

                    result[i]["commit_check"] = True

                    print("{0} config has checked OK".format(i))

                    #print(result[i]["diff"])

                    if commit == "commit":

                        try:

                            cu.commit(confirm = 20)

                        except Exception as e:

                            print(e)

                            sys.exit()
                            
                        result[i]["committed"] = True

                        print("{0} config has been committed OK".format(i))

                try:

                    writeResult(result,i)

                except Exception as e:

                    print(e)



    config_check()

def writeResult(result,k):

    with open('{0}/{1}_result.txt'.format(diff_results_path,k),"w",opener=opener) as f:

        f.write(result[k]["diff"])

 

if __name__ == "__main__":

    if development is not None:

        main(development)

    elif commit is not None:

        main(commit)

    elif check is not None:

        config_check()
    
    else:

        main()
