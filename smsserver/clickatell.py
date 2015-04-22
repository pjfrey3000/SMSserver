#!/usr/bin/env python

# A simple Python command-line script to send SMS messages using
# Clickatell's HTTP API (see http://clickatell.com).

'''
NAME
    %(prog)s - Send SMS message

SYNOPSIS
    %(prog)s PHONE MESSAGE
    %(prog)s -s MSGID
    %(prog)s -b | -l

DESCRIPTION
    A simple Python command-line script to send SMS messages using
    Clickatell's HTTP API (see http://clickatell.com).
    Records messages log in %(log)s
    Reads configuration parameters from %(conf)s

OPTIONS
    -s MSGID
        Query message delivery status.

    -b
        Query account balance.

    -l
        List message log file using %(pager)s.

    -p
        List phone book.

AUTHOR
    Written by Stuart Rackham, <srackham@gmail.com>

COPYING
    Copyright (C) 2010 Stuart Rackham. Free use of this software is
    granted under the terms of the MIT License.
'''
VERSION = '0.2.4'

import urllib
import os, sys, time, re
import simplejson as json

# Clickatell account configuration parameters.
# Create a separate configuration file named `.sms.conf` in your `$HOME`
# directory. The configuration file is single JSON formatted object with the
# same attributes and attribute types as the default CONF variable below.
# Alternatively you could dispense with the configuration file and edit the
# values in the CONF variable below.
CONF = {
    'USERNAME': '',
    'PASSWORD': '',
    'API_ID': '',
    'SENDER_ID': '',  # Your registered mobile phone number.
    'PHONE_BOOK': {},
    'ALLOWED_SENDER': {},
    'ALLOWED_RECIPIENT': {}
}

PROG = os.path.basename(__file__)
# HOME = os.environ.get('HOME', os.environ.get('HOMEPATH',os.path.dirname(os.path.realpath(__file__))))
HOME = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HOME,'sms.log')
CONF_FILE = os.path.join(HOME,'.sms.conf')
if os.path.isfile(CONF_FILE):
    CONF = json.load(open(CONF_FILE))
SENDER_ID = CONF['SENDER_ID']
PHONE_BOOK = CONF['PHONE_BOOK']
PAGER = os.environ.get('PAGER','less')

# URL query string parameters.
QUERY = {'user': CONF['USERNAME'], 'password': CONF['PASSWORD'],
          'api_id': CONF['API_ID'], 'concat': 3}

# Clickatell status messages.
MSG_STATUS = {
    '001': 'message unknown',
    '002': 'message queued',
    '003': 'delivered to gateway',
    '004': 'received by recipient',
    '005': 'error with message',
    '007': 'error delivering message',
    '008': 'OK',
    '009': 'routing error',
    '012': 'out of credit',
}

# Retrieve Clickatell account balance.
def account_balance():
    return http_cmd('getbalance')

# Query the status of a previously sent message.
def message_status(msgid):
    QUERY['apimsgid'] = msgid
    result = http_cmd('getmsgcharge')
    result += ' (' + MSG_STATUS.get(result[-3:],'') + ')'
    return result

# Strip number punctuation and check the number is not obviously illegal.
def sanitize_phone_number(number):
    result = re.sub(r'[+ ()-]', '', number)
    if not re.match(r'^\d+$', result):
        print 'illegal phone number: %s' % number
#        exit(1)
        result = 'illegal phone number'
    return result

def check_if_allowed(sender, recipient, loghandler):
    allok = False
    if sender.lower() in ALLOWED_SENDER and recipient.lower() in ALLOWED_RECIPIENT:
            allok = True
    logger.writelog(loghandler, "Sender " + sender + " or recipient " + recipient + " not allowed!","info")
    return(allok)


# Send text message. The recipient phone number can be a phone number
# or the name of a phone book entry.
def send_message(text, to, loghandler):
    if to in PHONE_BOOK:
        name = to
        to = PHONE_BOOK[to]
    else:
        name = None
    to = sanitize_phone_number(to)
    sender_id = sanitize_phone_number(SENDER_ID)
    if sender_id.startswith('64') and to.startswith('6427'):
        # Use local number format if sending to Telecom NZ mobile from a NZ
        # number (to work around Telecom NZ blocking NZ originating messages
        # from Clickatell).
        sender_id = '0' + sender_id[2:]
    QUERY['from'] = sender_id
    QUERY['to'] = to
    QUERY['text'] = text
    result = http_cmd('sendmsg')
    now = time.localtime(time.time())
    if name:
        to += ': ' + name
    logger.writelog(loghandler, "SMS sent to " + to + " from " + sender_id + ". Result : [" + result + "] " + text,"info")
#    print >>open(LOG_FILE, 'a'),'SMS - %17s,%s,%s,%40s,%s' % (time.strftime("%Y.%m.%d %H:%M:%S"), to, sender_id, result, text)
    return result

# Execute Clickatell HTTP command.
def http_cmd(cmd):
    url = 'http://api.clickatell.com/http/' + cmd
    query = urllib.urlencode(QUERY)
    file = urllib.urlopen(url, query)
    result = file.read()
    file.close()
    return result

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 3:
        if sys.argv[1] == '-s':
            print message_status(sys.argv[2])
        else:
            print send_message(sys.argv[2], sys.argv[1])
    elif argc == 2 and sys.argv[1] == '-b':
        print account_balance()
    elif argc == 2 and sys.argv[1] == '-l': # View log file.
        os.system(PAGER + ' ' + LOG_FILE)
    elif argc == 2 and sys.argv[1] == '-p': # List phone book.
        for i in PHONE_BOOK.items():
            print '%s: %s' % i
    else:
        print __doc__ % {'prog':PROG,'log':LOG_FILE,'conf':CONF_FILE,'pager':PAGER}

