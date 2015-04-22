import poplib
import email
import os, sys, time, re
import tempfile
import shutil
import time
import simplejson as json

CONF = {
    'MAILUSER': '',
    'MAILPASS': '',
    'MAILHOST': '',
}
    
HOME = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HOME,'sms.log')
CONF_FILE = os.path.join(HOME,'.sms.conf')
if os.path.isfile(CONF_FILE):
    CONF = json.load(open(CONF_FILE))
MAILUSER = CONF['MAILUSER']
MAILPASS = CONF['MAILPASS']
MAILHOST = CONF['MAILHOST']

mail = poplib.POP3(MAILHOST)
mailwelcome = mail.getwelcome()
mailloginuser = mail.user(MAILUSER)
mailloginpass = mail.pass_(MAILPASS)
mailstat = mail.stat()
maillist = mail.list()

print(mailwelcome)
print(mailloginuser)
print(mailloginpass)
print(mailstat)
print(maillist)
print ""

print >>open(LOG_FILE, 'a'),'POP - %17s,%s' % (time.strftime("%Y.%m.%d %H:%M:%S"), mailstat)
if mail.stat()[1] > 0:
    numMessages = len(mail.list()[1])
    for i in range(numMessages):
        outfilename = "tmpplainsms.%.7f" % time.time()
        outfile = open(outfilename,'w')
        for j in mail.retr(i+1)[1]:
            outfile.write(j)
            outfile.write("\n")
        outfile.close()

mail.quit()
