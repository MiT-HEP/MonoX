import os
import sys
import subprocess
import collections
import re
import json
import shutil
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Calculate integrated luminosity from Bambu output')
argParser.add_argument('snames', nargs = '*', help = 'Sample names.')
argParser.add_argument('--list', '-l', metavar = 'PATH', dest = 'list', default = '', help = 'Supply a good lumi list and skip lumi extraction from Bambu files.')
argParser.add_argument('--mask', '-m', metavar = 'PATH', dest = 'mask', default = '', help = 'Good lumi list to apply.')
argParser.add_argument('--save', '-S', action = 'store_true', dest = 'save', help = 'Save the json file to data/lumis.txt.')
argParser.add_argument('--save-plain', '-P', action = 'store_true', dest = 'savePlain', help = 'Also save just the list of lumis (i.e. CMS-standard JSON).')

args = argParser.parse_args()
sys.argv = []

try:
    proc = subprocess.Popen(['klist'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    out = proc.communicate()[0]
    line = out.split('\n')[1]
    if not line.endswith('CERN.CH'):
        raise RuntimeError('No token')

    kuser = line.replace('Default principal: ', '').replace('@CERN.CH', '')

except:
    print 'You need a CERN kerberos token.'
    print 'kinit -A -f <user>@CERN.CH'
    sys.exit(1)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
monoxdir = os.path.dirname(basedir)
sys.path.append(basedir)
from datasets import allsamples
import config

import ROOT

normtag = '/afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json'

print 'Calculating integrated luminosity for', args.snames, 'from', config.ntuplesDir
print 'Normtag is', normtag

allLumis = collections.defaultdict(set)
sampleRuns = collections.defaultdict(set)

if not args.list:
    def readFile(path, sname):
        source = ROOT.TFile.Open(path)
        if not source:
            return
    
        gr = source.Get('ProcessedRunsLumis')
    
        for iP in range(gr.GetN()):
            run = int(gr.GetX()[iP])
            lumi = int(gr.GetY()[iP])
    
            allLumis[run].add(lumi)
            sampleRuns[sname].add(run)
    
        source.Close()
    
    for sname in args.snames:
        sample = allsamples[sname]

        dname = config.ntuplesDir + '/' + sample.book + '/' + sample.fullname
    
        for fname in os.listdir(dname):
            if fname.endswith('.root'):
                readFile(dname + '/' + fname, sname)
    
    text = ''
    for run in sorted(allLumis.keys()):
        text += '\n  "%d": [\n' % run
    
        current = -1
        for lumi in sorted(allLumis[run]):
            if lumi == current + 1:
                current = lumi
                continue
    
            if current > 0:
                text += '%d],\n' % current
    
            current = lumi
            text += '    [%d, ' % current
    
        text += '%d]\n' % current
        text += '  ],'
    
    with open('_lumis_tmp.txt', 'w') as json:
        json.write('{' + text[:-1] + '\n}')

else:
    source = json.load(open(args.list))
    for run, ranges in source.items():
        for begin, end in ranges:
            allLumis[int(run)] |= set(range(begin, end + 1))

    shutil.copyfile(args.list, '_lumis_tmp.txt')

sshOpts = ['-oGSSAPIDelegateCredentials=yes', '-oGSSAPITrustDns=yes']

proc = subprocess.Popen(['scp'] + sshOpts + ['_lumis_tmp.txt', 'lxplus.cern.ch:./_lumis_tmp.txt'])
proc.communicate()

proc = subprocess.Popen(['ssh'] + sshOpts + ['lxplus.cern.ch', 'export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.0.3/bin:$PATH;brilcalc lumi --normtag ' + normtag + ' -i _lumis_tmp.txt'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

os.remove('_lumis_tmp.txt')

out = proc.communicate()[0]

print out

integrated = {}

for line in out.split('\n'):
    matches = re.match('\| +([0-9]+):[0-9]+ +\|[^|]+\|[^|]+\|[^|]+\|[^|]+\| +([0-9.]+) +\|', line)
    if not matches:
        continue

    run = int(matches.group(1))
    recorded = float(matches.group(2)) * 1.e-6

    integrated[run] = recorded

for sname in sorted(sampleRuns.keys()):
    total = 0.
    for run in sampleRuns[sname]:
        total += integrated[run]

    print '%s: %.1f' % (sname, total)

if args.save:
    text = ''
    for run in sorted(allLumis.keys()):
        text += '\n  "%d": {\n' % run
        text += '    "integrated": %f,\n' % integrated[run]
        text += '    "lumisections": [\n' 
    
        current = -1
        for lumi in sorted(allLumis[run]):
            if lumi == current + 1:
                current = lumi
                continue
    
            if current > 0:
                text += '%d],\n' % current
    
            current = lumi
            text += '      [%d, ' % current
    
        text += '%d]\n' % current
        text += '    ]\n'
        text += '  },'
    
    with open(basedir + '/data/lumis.txt', 'w') as json:
        json.write('{' + text[:-1] + '\n}\n')

if args.savePlain:
    text = ''
    for run in sorted(allLumis.keys()):
        text += '\n  "%d": [\n' % run
        current = -1
        for lumi in sorted(allLumis[run]):
            if lumi == current + 1:
                current = lumi
                continue
    
            if current > 0:
                text += '%d],\n' % current
    
            current = lumi
            text += '    [%d, ' % current
    
        text += '%d]\n' % current
        text += '  ],'
    
    with open(basedir + '/data/lumis_plain.txt', 'w') as json:
        json.write('{' + text[:-1] + '\n}\n')
