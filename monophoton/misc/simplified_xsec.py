#!/usr/bin/env python

import os
import sys
import subprocess

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

point = ' '.join(sys.argv[1:])

outdir = config.histDir + '/simplified_xsec'

if point == 'combine':

    values = {}

    for fname in os.listdir(outdir):
        with open(outdir + '/' + fname) as source:
            for line in source:
                line = line.strip()
                if 'final cross section' in line:
                    values[fname.replace('.dat', '')] = line[line.find('=') + 2:]
                    break

    with open(outdir + '/xsec.txt', 'w') as output:
        for point in sorted(values.keys()):
            output.write(point + ' ' + values[point] + '\n')

else:
    outname = outdir + '/' + point.replace('[', '').replace(']', '').replace(' ', '_') + '.dat'
    if os.path.exists(outname):
        sys.exit(0)

    files = None
    with open('simplified_fastsim.txt') as flist:
        for line in flist:
            line = line.strip()
            if line.startswith(point):
                files = []
                continue
    
            if files is None:
                continue
    
            if not line:
                break
    
            files.append(line)
    
    inputFiles = ' '.join(['inputFiles=%s' % f for f in files])
    
    output = open(outname, 'w')
    
    proc = subprocess.Popen('source /cvmfs/cms.cern.ch/cmsset_default.sh;export X509_USER_PROXY=/home/' + os.environ['USER'] + '/x509up_u' + str(os.getuid()) + '; cd ' + os.environ['CMSSW_BASE'] + ';eval `scram runtime -sh`;cmsRun genxsec.py ' + inputFiles, shell = True, stdout = output, stderr = subprocess.STDOUT)
    
    proc.communicate()
    
    output.close()
