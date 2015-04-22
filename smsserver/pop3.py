import poplib
import email
import os, sys, time, re
import tempfile
import shutil
import simplejson as json
import time

import smsserver
from smsserver import logger

def pop3(HOME, consoleLogging, loghandler):

    CONF = {
        'USERNAME': '',
        'PASSWORD': '',
        'API_ID': '',
        'SENDER_ID': '',  # Your registered mobile phone number.
        'PHONE_BOOK': {},
        'ALLOWED_RECIPIENT': {},
        'ALLOWED_SENDER': {},
        'POPLOOP': '',
        'MAILUSER': '',
        'MAILPASS': '',
        'MAILHOST': '',
        'MAILPORT': '',
        'MAILTIME': '',
    }

    TMPDIR = os.path.join(HOME,"TMPDIR")
    LASTPOP_FILE = os.path.join(HOME,'.sms.lastpop')
    CONF_FILE = os.path.join(HOME,'.sms.conf')
    if os.path.isfile(CONF_FILE):
        CONF = json.load(open(CONF_FILE))

    MAILUSER = CONF['MAILUSER']
    MAILPASS = CONF['MAILPASS']
    MAILHOST = CONF['MAILHOST']
    MAILPORT = CONF['MAILPORT']
    MAILTIME = CONF['MAILTIME']

    try:
        mail = poplib.POP3(MAILHOST,int(MAILPORT),int(MAILTIME))
    except:
        logger.writelog(loghandler, "Timeout [" + str(MAILTIME) + "] while accessing " + str(MAILHOST) + ":" + str(MAILPORT) + ".", "error")
        if consoleLogging:
            sys.stdout.write("Timeout [" + str(MAILTIME) + "] while accessing " + str(MAILHOST) + ":" + str(MAILPORT) + ".\n")
        return True
        
    try:
        mailloginuser = mail.user(MAILUSER)
    except:
        logger.writelog(loghandler, "Invalid POP3 user[" + str(MAILUSER) + "].", "error")
        if consoleLogging:
            sys.stdout.write("Invalid POP3 user [" + str(MAILUSER) + "].\n")
        return True

    try:
        mailloginpass = mail.pass_(MAILPASS)
    except:
        logger.writelog(loghandler, "Invalid POP3 password for user [" + str(MAILUSER) + "].", "error")
        if consoleLogging:
            sys.stdout.write("Invalid POP3 user [" + str(MAILUSER) + "].\n")
        return True

    mailstat = mail.stat()

    shutil.rmtree(TMPDIR, ignore_errors=True)

    if not os.path.exists(TMPDIR):
        os.makedirs(TMPDIR)

    try:
        file(LASTPOP_FILE, 'w').write("%17s,%s,%s,%s\n" % (time.strftime("%Y.%m.%d %H:%M:%S"), mailstat, mailloginuser, mailloginpass))
    except IOError, e:
        logger.writelog(loghandler, "Unable to write LASTPOP file: " + str(LASTPOP_FILE) + ". " + str(e.strerror) + " [" + str(e.errno) + "]", "error")
        if consoleLogging:
            sys.stdout.write("Unable to write LASTPOP file: " + str(LASTPOP_FILE) + ". " + str(e.strerror) + " [" + str(e.errno) + "].\n")
        return True
    
    if mail.stat()[1] > 0:
        logger.writelog(loghandler, str(mailstat) + " - " + str(mailloginuser) + " - " +  str(mailloginpass),"info")
        if consoleLogging:
            sys.stdout.write(str(mailstat) + " - " + str(mailloginuser) + " - " +  str(mailloginpass))
        numMessages = len(mail.list()[1])
        for i in range(numMessages):
            outfilename = TMPDIR + "//tmpsms.%.7f" % time.time()
            outfile = open(outfilename,'w')
            subjectwritten = False
            senderwritten = False
            recipientwritten = False
            bodybegins = False
            firstdashes = False
            bodyends = False
            for j in mail.retr(i+1)[1]:
                if "From: " in j[:6] and senderwritten == False:
                    outfile.write(re.search(r'\<(.*)\>', j).group(1))
                    outfile.write("\n")
                    senderwritten = True
                if "To: " in j[:4] and recipientwritten == False:
                    outfile.write(re.search(r'\<(.*)\>', j).group(1))
                    outfile.write("\n")
                    recipientwritten = True
                if "Subject" in j[:8] and subjectwritten == False:
                    outfile.write(j[9:])
                    outfile.write("\n")
                    subjectwritten = True
                elif bool(j and j.strip()) == False and bodybegins == False:
                    bodybegins = True
                elif bool(j and j.strip()) and bodybegins == True and bodyends == False:
                    if "--" in j[:2] and firstdashes == True:
                        bodyends = True
                    if "--" in j[:2] and firstdashes == False:
                        firstdashes = True
                    if not "--" in j[:2] and not "Content-Type" in j[:12] and not "Content-Transfer-Encoding" in j[:25]:
                        outfile.write(j)
                        outfile.write("\n")
            mail.dele(i+1)
            outfile.close()
    mail.quit()
    return(True)

if __name__ == '__main__':
   print pop3()
