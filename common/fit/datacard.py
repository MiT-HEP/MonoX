import sys
import os
import collections

import ROOT

# datacard.py workspace output signal

wsPath = sys.argv[1]
outputPath = sys.argv[2]
signal = sys.argv[3]

workspace = ROOT.TFile.Open(wsPath).Get('wspace')

samples = collections.defaultdict(list)
nuisances = []
signalRegion = ''

pdfs = workspace.allPdfs()
itr = pdfs.iterator()

while True:
    pdf = itr.Next()
    if not pdf:
        break

    name = pdf.GetName()
    proc = name[:name.rfind('_')]
    region = name[name.rfind('_') + 1:]

    if proc.startswith('signal-'):
        if proc != 'signal-' + signal:
            continue

        signalRegion = region

    samples[region].append(proc)

if not signalRegion:
    raise RuntimeError('No signal region found')

procids = {}
for region, procs in samples.items():
    for proc in procs:
        if proc in procids:
            continue

        if proc.startswith('signal-'):
            continue
        elif len(procids) == 0:
            procids[proc] = 1
        else:
            procids[proc] = max(procids.values()) + 1

args = workspace.allVars()
itr = args.iterator()

while True:
    arg = itr.Next()
    if not arg:
        break

    if arg.getAttribute('nuisance'):
        nuisances.append(arg.GetName())

nuisances.sort()

lines = [
    'imax * number of bins',
    'jmax * number of processes minus 1',
    'kmax * number of nuisance parameters',
    '----------------------------------------------------------------------------------------------------------------------------------',
    'shapes * * ' + os.path.realpath(wsPath) + ' wspace:$PROCESS_$CHANNEL',
    '----------------------------------------------------------------------------------------------------------------------------------'
]

line = 'bin          ' + ('%9s' % signalRegion) + ''.join(sorted(['%9s' % r for r in samples if r != signalRegion]))
lines.append(line)

line = 'observation  ' + ''.join('%9.1f' % o for o in [-1.] * len(samples))
lines.append(line)

lines.append('----------------------------------------------------------------------------------------------------------------------------------')

columns = [
    (signalRegion, 'signal-' + signal, str(-1))
]

for proc in samples[signalRegion]:
    if proc.startswith('signal-'):
        continue

    columns.append((signalRegion, proc, str(procids[proc])))

for region, procs in samples.items():
    if region == signalRegion:
        continue

    for proc in procs:
        columns.append((region, proc, str(procids[proc])))

line = 'bin          '
for column in columns:
    w = max(len(s) for s in column)
    line += ('%{width}s'.format(width = w + 1)) % column[0]
lines.append(line)

line = 'process      '
for column in columns:
    w = max(len(s) for s in column)
    line += ('%{width}s'.format(width = w + 1)) % column[1]
lines.append(line)

line = 'process      '
for column in columns:
    w = max(len(s) for s in column)
    line += ('%{width}s'.format(width = w + 1)) % column[2]
lines.append(line)

line = 'rate         '
for column in columns:
    w = max(len(s) for s in column)
    line += ('%{width}.1f'.format(width = w + 1)) % 1.
lines.append(line)

lines.append('----------------------------------------------------------------------------------------------------------------------------------')

for nuisance in nuisances:
    lines.append(nuisance + ' param 0 1')

with open(outputPath, 'w') as datacard:
    for line in lines:
        datacard.write(line + '\n')
