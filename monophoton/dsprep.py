import re
import os
import math
import sys
from pprint import pprint
from subprocess import Popen, PIPE

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import SampleDef
import config

book = sys.argv[1]
xsecFilePath = sys.argv[2]

skimDirPath = config.ntuplesDir + book

samples = {}
meds = []
dms = []

for line in os.listdir(skimDirPath):
    paramString = line.strip()

    params = [param.split('-')[1].strip() for param in paramString.split('_')[1:]]

    if float(params[2]) == 0 and float(params[3]) == 1:
        spin = 'dmafs'
    elif float(params[2]) == 1 and float(params[3]) == 0:
        spin = 'dmvfs'

    name = spin+'-'+params[0]+'-'+params[1]

    sdef = SampleDef(name, title = spin.upper(), book = book, directory = paramString, signal = True)
    samples[name] = sdef

    med = int(params[0])
    if not med in meds:
        meds.append(med)
    dm = int(params[1])
    if not dm in dms:
        dms.append(dm)

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
        
        xsec = float(temps[1])

        if xsec < 0.0001:
            scale = round(0.001 / xsec)
        else:
            scale = 1

        samples[name].crosssection = xsec
        samples[name].scale = scale
            
# for sname, sample in sorted(samples.items()):
for spin in ["dmafs", "dmvfs"]:
    for med in sorted(meds):
        for dm in sorted(dms):
            sname = '%s-%d-%d' % (spin, med, dm)
            try:
                sample = samples[sname]
            except:
                continue

            # print sname
            print sample.getWeights(config.ntuplesDir)
            
            if float(sample.crosssection) == 0.:
                print "\txsec == 0"
                
            if float(sample.nevents) == 0.:
                print "\tnevents == 0"
