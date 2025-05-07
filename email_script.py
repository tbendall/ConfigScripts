#!/usr/bin/python3

"""email_script.py: Script to use TLS SMTP servers to relay emails"""

__author__      = "Tristan Bendall/tristan@bendall.co"
__version__     = "v2.0"

# Import various modules
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from os.path import basename
from email.mime.application import MIMEApplication
import json
from smtplib import SMTP
import ssl

secrets_file = "< path to secrets file"

with open(secrets_file,"r") as f:

	secret_dict = json.loads(f.read())

# Set smtp server 
smtpServ = '< smtp server >'

# Set email "from" address
rcptFrom = "< from address >"

# Set password
passwd = secret_dict["password"]
username = secret_dict["user"]

# Define function "sendEmail" with undefined number of arguements
# When calling the function, procedure is to always supply 3 arguments in this order ("To","subject","body text")
# 4th variable, below set as the attachement file, is optional
def sendEmail(*args):

	# Create Multipart MIME object "msg"
	msg = MIMEMultipart()

	# Set message "msg" element "subject" to 2nd argument passed to function
	msg['Subject'] = args[1]
	
	# Set message "msg" element "From" to variable "rcptFrom"
	msg['From'] = rcptFrom

	# Set message "msg" element "To" to 1st argument passed to function
	msg['To'] = args[0]

	# Set message "msg" text-part to 3rd argument passed to function
	msg.attach(MIMEText(args[2]))

	# Check number of args passed to function
	# If 4th arg is set, treat as file and attach to email object "msg"
	if len(args) > 3:

		# Set file arg as variable "f"
		f = args[3]

		# Open file
		with open(f,"rb") as fil:
		
			# Create MIME-encoded object as "part"
			part = MIMEApplication(fil.read(),Name=basename(f))

			# Set file encoding to object "part" element "Content-Disposition"
			part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)

			# "Attach" object/file to email "msg"
			msg.attach(part)


	#context = ssl.create_default_context()
	context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	s = SMTP(smtpServ,587)	
	s.ehlo()
	s.starttls(context=context)
	s.ehlo()
	s.login(username,passwd)

	# Call function sendmail on SMTP object "s", passing in message attributes "rcptFrom", "args[0]"/Recipient, "msg.as_string"/Body text)
	s.sendmail(rcptFrom, args[0],  msg.as_string())		

	# Housekeeping to Terminate SMTP connection
	s.quit()
