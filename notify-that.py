#!/usr/bin/env python

import urllib
import urllib2
import smtplib
import sys
import httplib
import subprocess
import argparse

from email.mime.text import MIMEText

from twilio.rest import TwilioRestClient

from config import YO_API_KEY
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from config import EMAIL_LOGIN_USER, EMAIL_LOGIN_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT
from config import PASTEBIN_API_KEY

from pastebin_python.pastebin import PastebinPython


DEFAULT_NOTIFICATION_METHOD = 'yo'


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

# Post text to pastebin and return the url
def pasteToPasteBin(text, name='Notify-that output'):
	pasteBin = PastebinPython(api_dev_key=PASTEBIN_API_KEY)
	return pasteBin.createPaste(text, api_paste_name=name)


# Opens a subprocess so it can get the program's output in realtime
def openSubprocess(cmd, notificationMethod=DEFAULT_NOTIFICATION_METHOD, pasteToPastebin=True):
	lines = []

	p = subprocess.Popen(['stdbuf', '-oL'] + cmd, stdout=subprocess.PIPE)
	
	try:
		# Grab stdout line by line as it becomes available.  This will loop until p terminates.
		while p.poll() is None:
			line = p.stdout.readline()  # This blocks until it receives a newline.
			lines.append(line)
			sys.stdout.write(line)
	except KeyboardInterrupt:
		# Suppress raising an exception on ctrl+c (but not in the subprocess)
		return

	# When the subprocess terminates there might be unconsumed output that still needs to be processed.
	line = p.stdout.read()
	lines.append(line)
	sys.stdout.write(line)

	p.stdout.close()

	print 'Notifying you...'

	if notificationMethod == 'yo':
		notifyYo('madcow')
	elif notificationMethod == 'text':
		if pasteToPastebin:
			pastebinURL = pasteToPasteBin(''.join(lines))
			text = 'Notify-that! View script\'s output here: %s' % pastebinURL
		else:
			text = 'Notify-that!'
		notifyText('4108070375', text)
	elif notificationMethod == 'email':
		if pasteToPastebin:
			pastebinURL = pasteToPasteBin(''.join(lines))
			text = 'Check out your script\'s output here: %s' % pastebinURL
		else:
			text = 'Script finished!'
		notifyEmail('nvcarski@gmail.com', 'Notify that!', text)
	else:
		# Fallback
		notifyYo('madcow')


if __name__ == '__main__':
	# Set up the command line parser
	parser = argparse.ArgumentParser(description='Run COMMAND and notify you on termination via Yo, text, or email.')
	parser.add_argument('-m', action='store', dest='notification_method', nargs=1, default=[DEFAULT_NOTIFICATION_METHOD],
	                    help='Set environment')
	parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run')

	args = parser.parse_args()

	notificationMethod = args.notification_method[0]
	command = args.command

	openSubprocess(command, notificationMethod)
