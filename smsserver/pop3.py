import poplib
import email
import os, sys, time, re
import tempfile
import shutil
import simplejson as json
import time

import smsserver
from smsserver import logger

def pop3(MAILHOST,MAILPORT,MAILTIME,MAILUSER,MAILPASS,TMPDIR,LOG_FILE):

    mail = poplib.POP3(MAILHOST,int(MAILPORT),int(MAILTIME))
    mailloginuser = mail.user(MAILUSER)
    mailloginpass = mail.pass_(MAILPASS)
    mailstat = mail.stat()

    shutil.rmtree(TMPDIR, ignore_errors=True)

    if not os.path.exists(TMPDIR):
        os.makedirs(TMPDIR)

    if mail.stat()[1] > 0:
        logger.writelog(loghandler, mailstat + " - " + mailloginuser + " - " +  mailloginpass,"info")
#        print >>open(LOG_FILE, 'a'),'POP - %17s,%s,%s,%s' % (time.strftime("%Y.%m.%d %H:%M:%S"), mailstat, mailloginuser, mailloginpass)
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
