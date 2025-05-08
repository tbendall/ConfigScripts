#!/usr/bin/python3

"""getKey.py: Script to retrieve key lists from S3 buckets"""

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__     = "v1.0"

# Import various module
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-e', '--environment', type=str)

globals().update(vars(parser.parse_args()))

print(environment)

with open("../secrets",'r') as f:
	
	secrets = json.load(f)

ak = secrets['awsaccess']

sk = secrets['awssecret']

bt = secrets['awsbucket']

pak = secrets['prodawsaccess']

psk = secrets['prodawssecret']

pab = secrets['prodawsbucket']


if environment == 'prod':

	conn = S3Connection(pak,psk)

	b = conn.get_bucket(pab)
	

else:

	conn = S3Connection(ak,sk)

	b = conn.get_bucket(bt)

for i in b:

	print(i)
