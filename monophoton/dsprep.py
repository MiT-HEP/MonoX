import re
import os
import math
import sys
from pprint import pprint
from subprocess import Popen, PIPE

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
print basedir
sys.path.append(basedir)
from datasets import SampleDef, allsamples, defaultList
import config

book = sys.argv[1]
xsecFilePath = sys.argv[2]

skimDirPath = config.ntuplesDir + '/' + book

samples = {}
meds = set()
dms = set() 

for line in os.listdir(skimDirPath):
    paramString = line.strip()

    params = [param.split('-')[1].strip() for param in paramString.split('_')[1:]]

    if float(params[2]) == 0 and float(params[3]) == 1:
        spin = 'dmafs'
    elif float(params[2]) == 1 and float(params[3]) == 0:
        spin = 'dmvfs'

    name = spin+'-'+params[0]+'-'+params[1]

    try:
        sdef = allsamples[name]
    except:
        sdef = SampleDef(name, title = spin.upper(), book = book, fullname = paramString)
        samples[name] = sdef
        # not appending to allsamples here to have a proper ordering

    meds.add(int(params[0]))
    dms.add(int(params[1]))

with open(xsecFilePath) as xsecFile:
    for line in xsecFile:
        line = line.strip()
        temps = line.split(' ')

        params = temps[0].split('_')
        med = params[0].strip('med-')
        dm = params[1].strip('dm-')

        if params[2] == 'AV':
            spin = 'dmafs'
        elif params[2] == 'V':
            spin = 'dmvfs'
        
        name = spin+'-'+med+'-'+dm

        try:
            sample = samples[name]
        except:
            continue

        sample.crosssection = float(temps[1])

        sample.recomputeWeight([config.ntuplesDir])

        if sample.crosssection == 0. or sample.sumw == 0.:
            samples.pop(name)

# for sname, sample in sorted(samples.items()):
for spin in ["dmafs", "dmvfs"]:
    for med in sorted(meds):
        for dm in sorted(dms):
            sname = '%s-%d-%d' % (spin, med, dm)
            try:
                sample = samples[sname]
            except:
                continue

            if sample not in allsamples.samples:
                allsamples.samples.append(sample)

allsamples.save(defaultList)
