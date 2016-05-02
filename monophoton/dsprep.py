import re
import os
import math
import sys
from pprint import pprint

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import SampleDef
    

skimFilePath = sys.argv[1]
xsecFilePath = sys.argv[2]

samples = {}

with open(skimFilePath) as skimFile:
    for line in skimFile:
        path = line.strip()

        (bookString, paramString) = path.split('monophoton_')
        
        bookParts = bookString.strip('/').split('/')
        book = bookParts[-2] + '/' + bookParts[-1]
        
        params = [param.split('-')[1].strip() for param in paramString.split('_')]
        
        if float(params[2]) == 0 and float(params[3]) == 1:
            spin = 'dmafs'
        elif float(params[2]) == 1 and float(params[3]) == 0:
            spin = 'dmvfs'

        name = spin+'-'+params[0]+'-'+params[1]
            
        sdef = SampleDef(name, title = spin.upper(), book = book, directory = paramString, signal = True)
        samples[name] = sdef

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
            
for sname, sample in sorted(samples.items()):
    if float(sample.crosssection) == 0.:
        continue
    sample.linedump()

print '\n'
print '\n'

for sname, sample in sorted(samples.items()):
    if float(sample.crosssection) != 0.:
        continue
    sample.linedump()

print '\n'
print '\n'

names = [sname for sname in sorted(samples)]
print ' '.join(names)
