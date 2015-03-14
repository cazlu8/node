#!/usr/bin/python

import sys
import shutil
reload(sys)
sys.setdefaultencoding("utf-8")

import optparse
import os
import glob

endian=sys.byteorder

parser = optparse.OptionParser(usage="usage: %prog -n {NAME} -d {DEST} -i {ICU}")

parser.add_option("-d", "--dest-dir",
                  action="store",
                  dest="dest",
                  help="The destination directory")

parser.add_option("-n", "--name",
                  action="store",
                  dest="name",
                  help="The application package name")

parser.add_option("-i", "--icu-path",
                  action="store",
                  dest="icu",
                  help="The ICU tool path")

parser.add_option("-l", "--endian",
                  action="store",
                  dest="endian",
                  help='endian: big, little or host. your default is "%s"' % endian, default=endian, metavar='endianess')

(options, args) = parser.parse_args()

print(options)

optVars = vars(options);

for opt in ["dest", "name", "icu"]:
    if optVars[opt] is None:
        print "Missing required option: %s" % opt
        sys.exit(1)

if options.endian not in ("big", "little", "host"):
    print "Unknown endianess: %s" % options.endian
    sys.exit(1)

if options.endian == "host":
    options.endian = endian

if not os.path.isdir(options.dest):
    print "Destination is not a directory"
    sys.exit(1)

if not os.path.isdir(options.icu):
    print "ICU Path is not a directory"
    sys.exit(1)

if options.icu[-1] != '/':
    options.icu += '/'

genrb = options.icu + 'genrb'
pkgdata = options.icu + 'pkgdata'

if not os.path.isfile(genrb):
    print 'ICU Tool "%s" does not exist' % genrb
    sys.exit(1)

if not os.path.isfile(pkgdata):
    print 'ICU Tool "%s" does not exist' % pkgdata
    sys.exit(1)

def runcmd(tool, cmd, doContinue=False):
    cmd = "%s %s" % (tool, cmd)
    rc = os.system(cmd)
    if rc is not 0 and not doContinue:
        print "FAILED: %s" % cmd
        sys.exit(1)
    return rc

resfiles = glob.glob("%s/*.res" % options.dest)
_listfile = os.path.join(options.dest, 'packagefile.lst')
datfile = "%s/%s.dat" % (options.dest, options.name)

def clean():
    for f in resfiles:
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isfile(_listfile):
        os.remove(_listfile)
    if (os.path.isfile(datfile)):
        os.remove(datfile)

## Step 0, Clean up from previous build
clean()

## Step 1, compile the txt files in res files
runcmd(genrb, "-e utf8 -d %s resources/*.txt" % options.dest)

resfiles = [os.path.relpath(f) for f in glob.glob("%s/*.res" % options.dest)]

# pkgdata requires relative paths... it's annoying but necessary
# for us to change into the dest directory to work
cwd = os.getcwd();
os.chdir(options.dest)

## Step 2, generate the package list
listfile = open(_listfile, 'w')
listfile.write(" ".join([os.path.basename(f) for f in resfiles]))
listfile.close()

## Step 3, generate the dat file using pkgdata and the package list
runcmd(pkgdata, '-p %s -m common packagefile.lst' % options.name)

## All done with this tool at this point...
os.chdir(cwd); # go back to original working directory
