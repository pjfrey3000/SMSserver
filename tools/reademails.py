import os
import glob

TMPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"TMPDIR//*")

files=glob.glob(TMPDIR)
for file in files:
    f=open(file, 'r')
    print 'Num :  %s' % f.readline().rstrip()
    line = f.readline()
    while line:
        print 'SMS : %s' % line
        line = f.readline()
    f.close()
