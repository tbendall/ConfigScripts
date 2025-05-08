#!/usr/bin/python3

"""uploadS3.py: Script to upload files to S3 Buckets"""

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__     = "v1.0"

# Import various modules
import json
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import sys

# Read in secrets file
with open("./secrets",'r') as f:

        secrets = json.load(f)

ak = secrets['awsaccess']

sk = secrets['awssecret']

ab = secrets['awsbucket']

pak = secrets['prodawsaccess']

psk = secrets['prodawssecret']

pab = secrets['prodawsbucket']

# Create function uploadToS3, accepting variables "fileKey" and "fileName"
def uploadToS3(fileKey,filename,uploadProd):

	#Print upload type
	print(uploadProd)

	# Create list "ret"
	ret = []

	# Create variable with None Type
	responseBool = None

	if uploadProd == True:
	
		# Set S3Connection object "conn" with prod access/secret keys
		conn = S3Connection(pak,psk)		

	else:

		# Set S3Connection object "conn" with dev access/secret keys
		conn = S3Connection(ak,sk)

	# Try connecting to S3 bucket
	try:

		# Check if prod switch is set
		if uploadProd == True:
		
			# Set bucket to prod bucket
			b = conn.get_bucket(pab)

		else:

			# Set bucket to dev bucket
			b = conn.get_bucket(ab)


	# Catch any exceptions as "e"
	except Exception as e:

		# Set variable "responseBool" to False
		responseBool = False

		# Append variable "responseBool" to list "ret"
		ret.append(responseBool)
		
		# Append variable "e" to list "ret"
		ret.append(e)

		# Pass list "ret" to function output
		return ret
		
		#Terminate script processing
		sys.exit(0)

	# Implicit success of "Try" statement
	# Create S3 Key with bucket "b" object as "k" 
	k = Key(b)

	# Set key object "k" with key name "fileKey" 
	k.key = fileKey

	# Try uploading the contents of file passed-in to key "k"
	try:
		
		k.set_contents_from_filename(filename)

	# Catch any exceptions as "e"
	except Exception as e:

		# Set variable "responseBool" to False
		responseBool = False

		# Append variable "responseBool" to list "ret"
		ret.append(responseBool)

		# Append variable "e" to list "ret"
		ret.append(e)
		
		# Pass list "ret" to function output
		return ret

	# Implicit success of "Try" statement
	# Set variable "responseBool" to True
	responseBool = True

	# Append variable "responseBool" to list "ret"
	ret.append(responseBool)
	
	# Pass list "ret" to function output
	return ret

