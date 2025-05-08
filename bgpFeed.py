#!/usr/bin/python3

"""bgpfeed.py: Script to interrogate Peering Infrastructure, to feed Prefixes to S3 storage buckets"""

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__ 	= "v1.0"

# Import various modules
import argparse
import sys
import json
from jnpr.junos import *
from jnpr.junos.op.routes import RouteTable
from emailSc import sendEmail
from uploadS3 import uploadToS3


# Define peering points to choose from:

routers = {}

## routers['thn'] = "edge-1.thn" ## Example router

# Read in secrets file:
with open("./secrets",'r') as f:

        secrets = json.load(f)

user = secrets['user']

password = secrets['ropass']

ak = secrets['awsaccess']

sk = secrets['awssecret']

bt = secrets['awsbucket']

# Create Argument Parser "parser"
parser = argparse.ArgumentParser()

# Specify arguments to listen for when run via commandline

# Peer IP 
parser.add_argument('-p', '--peer', type=str)

# Peer name 
parser.add_argument('-n', '--name', type=str)

# Switch whether to upload to S3, or not
parser.add_argument('-u', '--upload', type=str)

# Switch whether to choose peering/specify router 
parser.add_argument('-r', '--router', type=str)


# Update global variables with contents of command line args
globals().update(vars(parser.parse_args()))

# Define function "pullBGP", accepting 2 arguments
def pullBGP(peer,name,rtr):

	# Create Device object "dev" - router to poll to
	dev = Device(rtr,user=user,password=password,port="22")

	# Try connecting to device and catch any exception "e"
	try:

		dev.open()

	except Exception as e:

		# Print exception to sys.stdout
		print(e)

		# Define email subject string
		sub = str("{0} BGP-Feed: FAIL".format(name))

		# Call function "sendEmail" with args (recipient, subject, body)
		sendEmail("tristan@bendall.co",sub,str(e))

	# Create RouteTable object "route_table" on defined device/router 
	route_table = RouteTable(dev)

	# Try returning route table from protocol bgp and peer address "peer"
	try:

		route_table.get(protocol='bgp',peer=peer)

	except Exception as e:
	
		# Print exception to sys.stdout
		print(e)

		# Define email subject string
		sub = str("{0} BGP-Feed: FAIL".format(name))

		# Call function "sendEmail" with args (recipient, subject, body)
		sendEmail("tristan@bendall.co",sub,str(e))

	# Housekeeping to close device/router connection
	dev.close()

	# Check if route table return was successful; 0 entries indicates error
	if len(route_table) == 0:

		# Define email subject string
		sub = str("{0} BGP-Feed: FAIL".format(name))

		# Call function "sendEmail" with args (recipient, subject, body)
		sendEmail("tristan@bendall.co",sub,"Route Table has 0 items - are you sure the peer is correct?")

		# Terminate script execution
		sys.exit()

	else:
		# If route table has >0 entries, progress with script
		pass

	# Set variable fileName as name (of peer) 
	fileName = str("{0}.txt".format(name))

	# Create file with file name fileName and write each route table entry to file
	with open(fileName, 'w') as outfile:

		for i in route_table:

			g = "{0}\n".format(i.name)
   	
			outfile.write(str(g))
	
	# Define email subject string
	sub = str("{pname} BGP-Feed: Success {prtr}".format(pname = name, prtr = rtr ))

	# Call function "sendEmail" with args (recipient, subject, body, attachment)
	sendEmail("tristan@bendall.co",sub,"",fileName)

	# Detect if "upload" command line switch is set
	# If set, upload to S3
	if upload is not None:

		# Create string for Key name
		keyString = str("{prouter}/{pname}/prefixes".format(pname = name, prouter = rtr) )	

		# Set Key name for location in S3 
		fileKey = keyString
		
		# Check if prod switch is set
		if upload == "prod":

			uploadType = True

		else:

			uploadType = False
		
		# Call function "uploadToS3" as "uploadRes" with name of Key and name of file 
		uploadRes = uploadToS3(fileKey,fileName,uploadType)
	
		# Send return value of S3 upload function
		print(uploadRes)

		# Check if return value has length above 1
		# uploadToS3 returns one two variables if function failed; one if successful
		if len(uploadRes) > 1: 

			# Define email subject string
			sub = str("{0} BGP-Feed: FAIL".format(name))

			# Call function "sendEmail" with args (recipient, subject, body)
			sendEmail("tristan@bendall.co",sub,str(uploadRes[1]))

		# If upload function returns just 1 variable and set to True:
		elif (uploadRes[0] == True):

			# Define email subject string
			sub = str("%s Upload Success -" % name)

			# Call function "sendEmail" with args (recipient, subject, body)
			sendEmail("tristan@bendall.co",sub,"")
		
		# If upload function returns just 1 variable and set to False:
		else:
	
			# Define email subject string
			sub = str("%s Upload: FAIL" % name)

			# Call function "sendEmail" with args (recipient, subject, body)
			sendEmail("tristan@bendall.co",sub,"")
	
	# If "upload" command line switch is NOT set:
	else:
	
		# Terminatate script processing
		sys.exit()

	
	
# Loop to run functions when script ran from commandline
if __name__ == '__main__':

	# Detect if "name" commandline variable is set
	if name is None:

		# Define email subject string
		sub = str("{0} BGP-Feed: FAIL".format(name))

		# Call function "sendEmail" with args (recipient, subject, body)
		sendEmail("tristan@bendall.co",sub,"No name supplied")
		
		# Terminatate script processing
		sys.exit()

	# Detect if "peer" commandline variable is set
	elif peer is None:

		# Define email subject string
		sub = str("{0} BGP-Feed: FAIL".format(name))

		# Call function "sendEmail" with args (recipient, subject, body)
		sendEmail("tristan@bendall.co",sub,"No peer IP supplied")

	# If both "peer" and "name" variables set:
	else:
	
		# Execute "main" function while passing in "peer", "name" and "specified" peering router commandline arguments
		pullBGP(peer, name, routers[router])
