import os
import sys
import subprocess
import collections
import re
import json
import shutil
import array
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Calculate integrated luminosity from Bambu output')
argParser.add_argument('snames', nargs = '*', help = 'Sample names.')
argParser.add_argument('--list', '-l', metavar = 'PATH', dest = 'list', default = '', help = 'Supply a good lumi list and skip lumi extraction from Bambu files.')
argParser.add_argument('--mask', '-m', metavar = 'PATH', dest = 'mask', default = '', help = 'Good lumi list to apply.')
argParser.add_argument('--no-calc', '-N', action = 'store_true', dest = 'noCalc', help = 'Just write the json file and quit.')
argParser.add_argument('--save', '-S', action = 'store_true', dest = 'save', help = 'Save the json file to data/lumis.txt.')
argParser.add_argument('--save-plain', '-P', action = 'store_true', dest = 'savePlain', help = 'Also save just the list of lumis (i.e. CMS-standard JSON).')

args = argParser.parse_args()
sys.argv = []

if not args.noCalc:
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

def listOfRanges(lumis):
    ranges = []

    begin = -1
    end = -1
    for lumi in sorted(lumis):
        if lumi == end + 1:
            end = lumi

        else:
            if begin > 0:
                ranges.append((begin, end))

            begin = lumi
            end = begin

    if begin > 0:
        ranges.append((begin, end))

    return ranges

mask = collections.defaultdict(set)
if args.mask:
    with open(args.mask) as source:
        for run, ranges in json.load(source).items():
            for begin, end in ranges:
                mask[int(run)] |= set(range(begin, end + 1))

allLumis = collections.defaultdict(set)
sampleRuns = collections.defaultdict(set)

if not args.list:
    print 'Calculating integrated luminosity for', args.snames, 'from', config.ntuplesDir

    arun = array.array('I', [0])
    alumi = array.array('I', [0])

    for sample in allsamples.getmany(args.snames):
        for path in sample.files():
            source = ROOT.TFile.Open(path)

            if not source:
                print 'Cannot open', path
                continue
        
            tree = source.Get('lumiSummary')
            if not tree:
                print path, 'does not have lumiSummary. Extracting the lumi list from the events tree.'
                tree = source.Get('events')

            tree.SetBranchStatus('*', False)
            tree.SetBranchStatus('runNumber', True)
            tree.SetBranchStatus('lumiNumber', True)
            tree.SetBranchAddress('runNumber', arun)
            tree.SetBranchAddress('lumiNumber', alumi)

            entry = 0
            while tree.GetEntry(entry) > 0:
                entry += 1

                run = arun[0]
                lumi = alumi[0]

                if len(mask) != 0 and run not in mask or lumi not in mask[run]:
                    continue

                allLumis[run].add(lumi)
                sampleRuns[sample.name].add(run)
    
            source.Close()

    blocks = []
    for run in sorted(allLumis.keys()):
        text = '  "%d": [\n' % run

        ranges = listOfRanges(allLumis[run])

        text += ',\n'.join('    [%d, %d]' % r for r in ranges) + '\n'
        text += '  ]'

        blocks.append(text)
    
    with open('_lumis_tmp.txt', 'w') as out:
        out.write('{\n' + ',\n'.join(blocks) + '\n}')

else:
    with open(args.list) as source:
        for run, ranges in json.load(source).items():
            for begin, end in ranges:
                allLumis[int(run)] |= set(range(begin, end + 1)) & mask[int(run)]

    shutil.copyfile(args.list, '_lumis_tmp.txt')

if not args.noCalc:
    normtag = '/afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json'
    print 'Normtag is', normtag

    sshOpts = ['-oGSSAPIDelegateCredentials=yes', '-oGSSAPITrustDns=yes']
    
    proc = subprocess.Popen(['scp'] + sshOpts + ['_lumis_tmp.txt', 'lxplus.cern.ch:./_lumis_tmp.txt'])
    proc.communicate()
    
    proc = subprocess.Popen(['ssh'] + sshOpts + ['lxplus.cern.ch', 'export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH;brilcalc lumi -b "STABLE BEAMS" --normtag ' + normtag + ' -i _lumis_tmp.txt;echo brilcalc version is `brilcalc --version`'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

if args.noCalc or args.savePlain:
    os.rename('_lumis_tmp.txt', basedir + '/data/lumis_plain.txt')
    if args.noCalc:
        sys.exit(0)

else:
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
        try:
            total += integrated[run]
        except KeyError:
            pass

    print '%s: %.1f' % (sname, total)

if args.save:
    blocks = []
    for run in sorted(allLumis.keys()):
        if run not in integrated:
            continue

        text = '  "%d": {\n' % run
        text += '    "integrated": %f,\n' % integrated[run]
        text += '    "lumisections": [\n' 

        ranges = listOfRanges(allLumis[run])

        text += ',\n'.join('      [%d, %d]' % r for r in ranges) + '\n'
        text += '    ]\n'
        text += '  }'

        blocks.append(text)
    
    with open(basedir + '/data/lumis.txt', 'w') as out:
        out.write('{\n' + ',\n'.join(blocks) + '\n}\n')
