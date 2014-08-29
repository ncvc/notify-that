#!/usr/bin/env python

import urllib
import urllib2
import smtplib
import sys
import httplib

from email.mime.text import MIMEText

from twilio.rest import TwilioRestClient

from config import YO_API_KEY
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from config import EMAIL_LOGIN_USER, EMAIL_LOGIN_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT


YO_API_URL = 'https://api.justyo.co/yo/'

EMAIL_FROM_ADDRESS = 'ncvc@mit.edu'


def notifyYo(username):
	args = { 'api_token': YO_API_KEY, 'username': username }
	encodedArgs = urllib.urlencode(args)

	try:
		responseCode = urllib2.urlopen(YO_API_URL, encodedArgs).getcode()
	except urllib2.HTTPError:
		# We were probably rate-limited, Yo limits you to 1 Yo per minute
		return False

	return responseCode == httplib.OK

def notifyText(number, messageStr):
	client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	client.messages.create(to=number, from_=TWILIO_NUMBER, body=messageStr)

def notifyEmail(emailAddress, subject, messageStr):
	msg = MIMEText(messageStr)

	msg['Subject'] = subject
	msg['From'] = EMAIL_FROM_ADDRESS
	msg['To'] = emailAddress

	s = smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
	s.login(EMAIL_LOGIN_USER, EMAIL_LOGIN_PASSWORD)
	s.sendmail(EMAIL_FROM_ADDRESS, [emailAddress], msg.as_string())
	s.quit()

def fromPipe():
	lines = []
	for line in sys.stdin:
		sys.stdout.write(line)
		lines.append(line)

	return notifyYo('madcow')
	# notifyText('4108070375', 'Done!')
	# notifyEmail('nvcarski@gmail.com', 'subj', ''.join(lines))


if __name__ == '__main__':
	fromPipe()
