#!/usr/bin/env python

import sys
import os
import collections

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

merged = {} # {(sample, skim): mtime}
skimmed = collections.defaultdict(int) # {(sample, skim): last update time}

for sditem in os.listdir(config.skimDir):
    if os.path.isdir(config.skimDir + '/' + sditem):
        dname = config.skimDir + '/' + sditem
        for fname in os.listdir(dname):
            sample = fname[:fname.find('_')]
            skim = fname[fname.rfind('_') + 1:fname.rfind('.root')]

            mtime = os.stat(dname + '/' + fname).st_mtime
            if mtime > skimmed[(sample, skim)]:
                skimmed[(sample, skim)] = mtime
        
    else:
        sample = sditem[:sditem.find('_')]
        skim = sditem[sditem.rfind('_') + 1:sditem.rfind('.root')]

        mtime = os.stat(config.skimDir + '/' + sditem).st_mtime
        merged[(sample, skim)] = mtime

for ss in sorted(skimmed.keys()):
    if ss not in merged:
        print ss, 'is unmerged'

    elif skimmed[ss] > merged[ss]:
        print ss, 'have new skims'
