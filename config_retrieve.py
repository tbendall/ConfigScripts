#!/usr/bin/python3

"""config_retrieve.py: Script to retrieve config from Juniper Routers in XML/SET/JSON Format"""

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__     = "v2.0"


from jnpr.junos import Device
from lxml import etree as ET
import re
import argparse
import json
from email_script import sendEmail
import sys

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-f','--cformat', type=str)
arg_parser.add_argument('-d','--devel', type=str)
arg_parser.add_argument('-t','--device_type', type=str)
configs = {}

globals().update(vars(arg_parser.parse_args()))




project_path = "< path to project dir >"
secrets_file = "< path to secrets file >"


with open(secrets_file,"r") as f:

	secret_dict = json.loads(f.read())

	# Set password
	rtr_password = secret_dict["password"]
	rtr_username = secret_dict["user"]

def retrieveDevices(deviceType):

	if not deviceType:

		deviceType = ""

	devices = {}

	# Open RANCID routerdb file to populate routers
	with open("{0}/router.db".format(project_path),"r") as f:

		devices = dict([((x.split(":")[3].strip("/\n")).lower(),x.split(":")[0]) for x in f if re.match(".*{0}-".format(deviceType),x) if re.match(".*{0}.*".format("juniper"),x)])

	print(len(devices))
	
	return devices

def retrieveConfig(hosts,devel):

	written_hosts = []

	errors = {}

	if configFormat in ["xml","set","json"]:

		if not devel:

			print("not dev")

			for k,v in hosts.items():

				hostname = k 

				ip = v

				try:

					with Device(host=ip,user=rtr_username,passwd=rtr_password,port=22, huge_tree=True) as dev:

						data = dev.rpc.get_config(options={'format':configFormat})

				except Exception as e:

					errors[hostname] = e

					print(e)

					continue

				if configFormat == "json":

					config = json.dumps(data)
					
				else:

					config = ET.tostring(data, pretty_print=True, encoding='utf-8').decode("utf-8")

				writeFile(config,hostname,configFormat)

				written_hosts.append(hostname)

				print(hostname)

		if devel:

			hostname = devel

			ip = hosts[hostname]

			print(hostname)

			try:
				
				with Device(host=ip,user=rtr_username,passwd=rtr_password,port=22,timeout=5,huge_tree=True) as dev:

					data = dev.rpc.get_config(options={'format':configFormat})
				
			except Exception as e:

				errors[hostname] = e

				sys.exit()

			if configFormat == "json":

				configs[hostname] = json.dumps(data)
					
			else:

				configs[hostname] = ET.tostring(data, pretty_print=True, encoding='utf-8').decode("utf-8")

			written_hosts.append(hostname)

			writeFile(configs[hostname],hostname,configFormat)

	sendEmail("< recipient_email_address >", "Config Fetcher","{0} files written to {2} folder".format(str(len(written_hosts)), device_type, configFormat))

def writeFile(config,hostname,conf_type):

	hosts = []

	with open("project_path/{1}/{0}.txt".format(hostname,conf_type),"w") as f:

		f.write(config)

if __name__ == "__main__":

	if cformat is None:

		configFormat = "json"
	
	else:

		configFormat = cformat

	hosts = retrieveDevices(device_type)

	retrieveConfig(hosts,devel)
