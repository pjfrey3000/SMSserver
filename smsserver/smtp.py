import smtplib
import email
import os, sys, time, re
import tempfile
import shutil
import simplejson as json
import time
from email.mime.text import MIMEText
import smsserver
from smsserver import logger

def smtp(toaddr, subject, content, HOME, consoleLogging, loghandler):

    CONF = {
        'SMTPUSER': '',
        'SMTPPASS': '',
        'SMTPHOST': '',
        'SMTPSENDER': '',
        'SMTPPORT': '',
        'SMTPTIME': '',
    }

    TMPDIR = os.path.join(HOME,"TMPDIR")
    CONF_FILE = os.path.join(HOME,'.sms.conf')
    if os.path.isfile(CONF_FILE):
        CONF = json.load(open(CONF_FILE))

    SMTPUSER = CONF['SMTPUSER']
    SMTPPASS = CONF['SMTPPASS']
    SMTPHOST = CONF['SMTPHOST']
    SMTPSENDER = CONF['SMTPSENDER']
    SMTPPORT = CONF['SMTPPORT']
    SMTPTIME = CONF['SMTPTIME']

    msg = MIMEText(content)
    msg['From'] = SMTPSENDER
    msg['To'] = toaddr
    msg['Subject'] = subject
    try:
        mail = smtplib.SMTP(SMTPHOST,int(SMTPPORT))
    except:
        logger.writelog(loghandler, "Timeout [" + str(SMTPTIME) + "] while accessing " + str(SMTPHOST) + ":" + str(SMTPPORT) + ".", "error")
        if consoleLogging:
            sys.stdout.write("Timeout [" + str(SMTPTIME) + "] while accessing " + str(SMTPHOST) + ":" + str(SMTPPORT) + ".\n")
        return True
    mail.ehlo()
    if mail.has_extn('STARTTLS'):
        mail.starttls()
        mail.ehlo() # re-identify ourselves over TLS connection
    try:
        smtploginuser = mail.login(SMTPUSER,SMTPPASS)
    except:
        logger.writelog(loghandler, "Invalid SMTP credentials[" + str(SMTPUSER) + "].", "error")
        if consoleLogging:
            sys.stdout.write("Invalid SMTP credentials [" + str(SMTPUSER) + "/" + str(SMTPPASS) + "].\n")
        return True
    try:
        mail.sendmail(SMTPSENDER, toaddr, msg.as_string() + "\r\n")
    except:
        pass
    mail.quit()
    return True
