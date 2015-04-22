#!/usr/bin/env python
# Author: Bernhard Erren <bernhard.erren@googlemail.com> URL: https://github.com/pjfrey3000/SMSserver
#
# Many thanks to Stuart Rackham, <srackham@gmail.com> for the clickatell library.
#
# This file is part of SMSserver.
#
# SMSserver: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# SMSserver is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.
# Check needed software dependencies to nudge users to fix their setup

import smsserver
from smsserver import clickatell
from smsserver import pop3
from smsserver import logger

import poplib
import email
import os, sys, time, re
import shutil
import glob
import time
import simplejson as json
import string
import signal
import traceback
import getopt
import threading

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

SMSSERVERVERSION = "master"
TMPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"TMPDIR")
PROG = os.path.basename(__file__)
# HOME = os.environ.get('HOME', os.environ.get('HOMEPATH',os.path.dirname(os.path.realpath(__file__))))
HOME = os.path.dirname(os.path.abspath(__file__))
global LOG_FILE
LOG_FILE = os.path.join(HOME,'sms.log')
global PID_FILE
PID_FILE = os.path.join(HOME,'.sms.pid')
global LASTPOP_FILE
LASTPOP_FILE = os.path.join(HOME,'.sms.lastpop')
CONF_FILE = os.path.join(HOME,'.sms.conf')
if os.path.isfile(CONF_FILE):
    CONF = json.load(open(CONF_FILE))
SENDER_ID = CONF['SENDER_ID']
PHONE_BOOK = CONF['PHONE_BOOK']
POPLOOP = CONF['POPLOOP']

MAILUSER = CONF['MAILUSER']
MAILPASS = CONF['MAILPASS']
MAILHOST = CONF['MAILHOST']
MAILPORT = CONF['MAILPORT']
MAILTIME = CONF['MAILTIME']



def help_message(PROG):
    """
    print help message for commandline options
    """
    help_msg = "\n"
    help_msg += "Usage: " + PROG + " <option> <another option>\n"
    help_msg += "\n"
    help_msg += "Options:\n"
    help_msg += "\n"
    help_msg += " -h --help Prints this message\n"
    help_msg += " -q --quiet Disables logging to console\n"
    help_msg += " -d --daemon Run as double forked daemon (includes options --quiet --nolaunch)\n"
    help_msg += " -p <port> --port=<port> Override default/configured port to listen on\n"
    return help_msg

def daemonize(CREATEPID, LOG_FILE, PID_FILE, loghandler):
    """
    Fork off as a daemon
    """
    # pylint: disable=E1101 Make a non-session-leader child process
    try:
        pid = os.fork() # @UndefinedVariable - only available in UNIX
        if pid != 0:
            os._exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)
    os.setsid() # @UndefinedVariable - only available in UNIX
    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))
    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork() # @UndefinedVariable - only available in UNIX
        if pid != 0:
            os._exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Write pid
    if CREATEPID:
        pid = str(os.getpid())
        logger.writelog(loghandler, "Writing PID: " + pid + " to " + str(PID_FILE), "info")
        #        print >>open(LOG_FILE, 'a'),'SMS - %17s,Writing PID: %s to %s' % (time.strftime("%Y.%m.%d %H:%M:%S"), pid, str(PID_FILE))
        try:
            file(PID_FILE, 'w').write("%s\n" % pid)
        except IOError, e:
            logger.writelog(loghandler, "Unable to write PID file: " + str(PID_FILE) + ". " + str(e.strerror) + " [" + str(e.errno) + "]", "error")
#            print >>open(LOG_FILE, 'a'),'SMS - %17s,Unable to write PID file: %s Error %s [%s]' % (time.strftime("%Y.%m.%d %H:%M:%S"), str(PID_FILE), str(e.strerror), str(e.errno))
    # Redirect all output
    sys.stdout.flush()
    sys.stderr.flush()
    devnull = getattr(os, 'devnull', '/dev/null')
    stdin = file(devnull, 'r')
    stdout = file(devnull, 'a+')
    stderr = file(devnull, 'a+')
    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())


def main():

    CREATEPID = True
    DAEMON = False
    forcedPort = None
    noLaunch = True
    
    loghandler = logger.openlog(LOG_FILE)
    logger.writelog(loghandler, "Starting SMSserver", "info")
    
    MY_ARGS = sys.argv[1:]
    
    consoleLogging = (not hasattr(sys, "frozen")) or (PROG.lower().find('-console') > 0)
    
    threading.currentThread().name = "MAIN"
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfqdp::", ['help', 'quiet', 'daemon', 'port='])  # @UnusedVariable
    except getopt.GetoptError:
        sys.exit(help_message())
    
    for o, a in opts:

        # Prints help message
        if o in ('-h', '--help'):
            sys.exit(help_message(PROG))

        # Disables logging to console
        if o in ('-q', '--quiet'):
            consoleLogging = False

        # Run as a double forked daemon
        if o in ('-d', '--daemon'):
            DAEMON = True
            # When running as daemon disable consoleLogging and don't start browser
            consoleLogging = False

            
    # The pidfile is only useful in daemon mode, make sure we can write the file properly
    if CREATEPID:
        if DAEMON:
            pid_dir = os.path.dirname(PID_FILE)
            if not os.access(pid_dir, os.F_OK):
                sys.exit("PID dir: " + pid_dir + " doesn't exist. Exiting.")
            if not os.access(pid_dir, os.W_OK):
                sys.exit("PID dir: " + pid_dir + " must be writable (write permissions). Exiting.")

        else:
            if consoleLogging:
                sys.stdout.write("Not running in daemon mode. PID file creation disabled.\n")

            CREATEPID = False

    if consoleLogging:
        sys.stdout.write("Starting up SMSserver " + SMSSERVERVERSION + "\n")
        if not os.path.isfile(CONF_FILE):
            sys.stdout.write("Unable to find '" + CONF_FILE + "' , all settings will be default!" + "\n")

    if DAEMON:
        daemonize(CREATEPID, LOG_FILE, PID_FILE, loghandler)

    # Use this PID for everything
    PID = os.getpid()

    
    while True:
        
        smsserver.pop3.pop3(MAILHOST,MAILPORT,MAILTIME,MAILUSER,MAILPASS,TMPDIR,LOG_FILE,LASTPOP_FILE)

#        print >>open(PID_FILE, 'w'),'RUN - %17s' % (time.strftime("%Y.%m.%d %H:%M:%S"))
        files=glob.glob(TMPDIR+"//*")
        for file in files:
            f=open(file, 'r')
            sender = f.readline().rstrip()
            recipient = f.readline().rstrip()
            if check_if_allowed(sender, recipient, loghandler) == False:
                break
            outputnumber = clickatell.sanitize_phone_number(f.readline().rstrip())
    #        print 'Num : %s' % outputnumber
            line = f.readline()
            outputsms = line.rstrip()
            while line:
                line=f.readline()
                outputsms = outputsms + " " + line.rstrip()
    #        print 'SMS : %s' % outputsms.rstrip()
            smsserver.clickatell.send_message(outputsms, outputnumber, loghandler)
            f.close()
            if os.path.isfile(file):
                os.remove(file)
        time.sleep(float(POPLOOP))
        
        return
        
if __name__ == "__main__":
    main()
