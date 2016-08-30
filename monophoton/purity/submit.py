#!/usr/bin/env python

import sys
import os
from subprocess import Popen, PIPE

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import selections as s

scratchPath = '/scratch5/ballen/hist/purity/'+s.Version+'/sieie/Plots/SignalContam'

argFile = file('condorArgs.txt', 'w')

for source in ['nero']:
    for loc in s.Locations[:1]:
        for chiso in s.ChIsoSbSels[:]:
            for pt in s.PhotonPtSels[:]:
                for met in s.MetSels[1:2]:
                    for sel in ['none', 'medium_pixel_monoph']:
                        # print loc, sel, chiso[0], pt[0], met[0]
                        outDir = scratchPath + '/' + source + '/' + loc + '_' + sel + '_' + chiso[0] + '_' + pt[0] + '_' + met[0]
                        # print outDir
                        if not os.path.exists(outDir):
                            os.makedirs(outDir)
                        argFile.write(source + ' ' + loc + ' ' + sel + ' ' + chiso[0].replace('ChIso', '') + ' ' + pt[0].replace('PhotonPt', '') + ' ' + met[0].replace('Met', '') + ' \n')

argFile.close()
submit = Popen( ['/home/ballen/bin/condor-run', 'bkgdstats.py', '-a', 'condorArgs.txt'], stdout = PIPE, stderr = PIPE )
(sout, serr) = submit.communicate()
print sout, '\n'
print serr, '\n'
