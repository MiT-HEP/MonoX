#!/usr/bin/env python

import sys
import os
from subprocess import Popen, PIPE

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import selections as s

scratchPath = '/data/t3home000/ballen/hist/purity/'+s.Version

argFile = file('condorArgs.txt', 'w')

PhotonIds = [ 'none' ]
for base in ['loose', 'medium', 'tight', 'highpt']:
     PhotonIds += [ base, base+'-pixel', base+'-pixel-monoph' ]

#print sorted(s.PhotonPtSels.keys())
#print sorted(s.MetSels.keys())
#sys.exit(0)

for era in s.Eras:
    for loc in s.Locations[:1]:
        for pt in sorted(s.PhotonPtSels.keys())[-1:]:
            for met in sorted(s.MetSels.keys())[:1]:
                for sel in PhotonIds:
                    # print loc, sel, chiso[0], pt[0], met[0]
                    outDir = scratchPath + '/' + era + '_' + loc + '_' + sel + '_' + pt + '_' + met
                    # print outDir
                    if not os.path.exists(outDir):
                        os.makedirs(outDir)
                    argFile.write(loc + ' ' + sel + ' ' + pt.replace('PhotonPt', '') + ' ' + met.replace('Met', '') + ' ' + era + ' \n')

argFile.close()
submit = Popen( ['/home/ballen/bin/condor-run', 'bkgdstats.py', '-a', 'condorArgs.txt'], stdout = PIPE, stderr = PIPE )
(sout, serr) = submit.communicate()
print sout, '\n'
print serr, '\n'
