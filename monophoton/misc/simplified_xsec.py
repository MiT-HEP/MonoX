#!/usr/bin/env python

import os
import sys
import subprocess
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

# sed -n 's/\[\(med-[^ ]*\) \(.*\)\] [1-9][0-9]* events/\1_\2/p' simplified_fastsim.txt | while read line; do [ -e /scratch5/yiiyama/studies/monophoton16/simplified_xsec/$line.dat ] || echo $line >> ~/tmp/points.txt; done
# condor-run $PWD/simplified_xsec.py -a ~/tmp/points.txt

# med-X_dm-Y_V/AV
point = sys.argv[1]

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
    outname = outdir + '/' + point + '.dat'
    if os.path.exists(outname):
        sys.exit(0)

    header = '[' + point[:point.rfind('_')] + ' ' + point[point.rfind('_') + 1:] + ']'

    files = None
    with open(basedir + '/data/simplified_fastsim.txt') as flist:
        for line in flist:
            line = line.strip()
            if line.startswith(header):
                files = []
                continue
    
            if files is None:
                continue
    
            if not line:
                break
    
            files.append(line)

    if files is None:
        sys.exit(1)
    
    inputFiles = ' '.join(['inputFiles=%s' % f for f in files])

    output = open(outname, 'w')

    commands = [
        'source /cvmfs/cms.cern.ch/cmsset_default.sh',
        'export X509_USER_PROXY=$PWD/x509up_u%d' % os.getuid(),
        'cd ' + os.environ['CMSSW_BASE'],
        'eval `scram runtime -sh`'
        'cmsRun /home/yiiyama/cms/cmssw/cfg/genxsec.py ' + inputFiles
    ]

    proc = subprocess.Popen(';'.join(commands), shell = True, stdout = output, stderr = subprocess.STDOUT)
    
    proc.communicate()
    
    output.close()

    output = open(outname)

    for line in output:
        if 'final cross section' in line:
            output.close()
            break

    else:
        output.close()
        os.remove(outname)
