import os
import sys
import subprocess
import collections
import re

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
samples = ['sph-16b2', 'sph-16b2s']

print 'Calculating integrated luminosity for', samples, 'from', config.ntuplesDir
print 'Normtag is', normtag

allLumis = collections.defaultdict(set)

def readFile(path):
    source = ROOT.TFile.Open(path)
    if not source:
        return

    gr = source.Get('ProcessedRunsLumis')

    for iP in range(gr.GetN()):
        run = int(gr.GetX()[iP])
        lumi = int(gr.GetY()[iP])

        allLumis[run].add(lumi)

    source.Close()

for sname in samples:
    sample = allsamples[sname]

    dname = config.ntuplesDir + '/' + sample.book + '/' + sample.fullname

    for fname in os.listdir(dname):
        if fname.endswith('.root'):
            readFile(dname + '/' + fname)

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

sshOpts = '-oGSSAPIDelegateCredentials=yes -oGSSAPITrustDns=yes'

proc = subprocess.Popen(['scp', sshOpts, '_lumis_tmp.txt', 'lxplus.cern.ch:./_lumis_tmp.txt'])
proc.communicate()

proc = subprocess.Popen(['ssh', sshOpts, 'lxplus.cern.ch', 'export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.0.3/bin:$PATH;brilcalc lumi --normtag ' + normtag + ' -i _lumis_tmp.txt'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

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
    text += '  },\n'

with open(basedir + '/data/lumis.txt', 'w') as json:
    json.write('{' + text[:-1] + '\n}')

os.remove('_lumis_tmp.txt')
