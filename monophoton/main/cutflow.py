import os
import sys
sys.dont_write_bytecode = True
import array
from argparse import ArgumentParser

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
import utils

argParser = ArgumentParser(description = 'Print cut flow')
argParser.add_argument('region', metavar = 'REGION', help = 'Control/signal region name.')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '+', help = 'Sample names.')
argParser.add_argument('--events', '-E', action = 'store_true', dest = 'eventList', help = 'Print list of events instead of cutflow.')
argParser.add_argument('--skim-dir', '-s', metavar = 'PATH', dest = 'skimDir', default = config.skimDir, help = 'Directory of skim files to read from.')
argParser.add_argument('--ntuples-dir', '-n', metavar = 'PATH', dest = 'ntuplesDir', default = config.ntuplesDir, help = 'Directory of source ntuples.')
argParser.add_argument('--flow', '-f', metavar = 'CUTS', nargs = '+', dest = 'cutflow', help = 'Cutflow')
argParser.add_argument('--cut-results', '-r', metavar = 'EVENTID', dest = 'eventId', help = 'Show results of the cuts on a specific event.')
argParser.add_argument('--out', '-o', metavar = 'PATH', dest = 'outName', default = '', help = 'Output file name. Use "-" for stdout.')
argParser.add_argument('--uw-format', '-U', action = 'store_true', dest = 'uwFormat', help = 'Print event list in run:event:lumi format.')

args = argParser.parse_args()
sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

data = False

ntotal = 0

sampleNames = []

tree = ROOT.TChain('cutflow')
for sample in allsamples.getmany(args.snames):
    sampleNames.append(sample.name)

    if sample.data:
        data = True

    if args.skimDir == config.skimDir:
        # default skim directory -> assume nevents in DB is accurate
        ntotal += sample.nevents

        filePath = utils.getSkimPath(sample.name, args.region)

    else:
        # otherwise open the original files
        sdir = args.ntuplesDir + '/' + sample.book + '/' + sample.fullname
        for fname in os.listdir(sdir):
            source = ROOT.TFile.Open(sdir + '/' + fname)
            counter = source.Get('counter')
            if not counter:
                source.Close()
                continue
    
            ntotal += counter.GetBinContent(1)
            source.Close()

        filePath = args.skimDir + '/' + sample.name + '_' + args.region + '.root'

    print filePath
    tree.Add(filePath)

if args.cutflow is None:
    if data:
        cutflow = [('HLT_Photon165_HE10',)]
    else:
        cutflow = []
    
    cutflow += [
        ('MetFilters',),
        ('PhotonSelection',),
        ('LeptonSelection',),
    ]

    if args.region == 'monoph':
        cutflow += [
            ('Met',),
            ('PhotonMetDPhi',),
            ('JetMetDPhi',),
            # ('TauVeto',)
        ]

    elif args.region == 'monoel':
        cutflow += [
            ('RealMetCut',),
            ('LeptonMt',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('JetMetDPhi',),
        ]

    elif args.region == 'monomu':
        cutflow += [
            ('LeptonMt',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('JetMetDPhi',),
        ]

    elif args.region in ['dimu', 'diel']:
        cutflow += [
            ('OppositeSign',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('Mass',),
            ('JetMetDPhi',),
        ]

else:
    cutflow = []
    for cutstr in args.cutflow:
        cuts = tuple(cutstr.split(','))
        cutflow.append(cuts)

if args.eventList:
    run = array.array('I', [0])
    lumi = array.array('I', [0])
    event = array.array('I', [0])
    
    tree.SetBranchAddress('runNumber', run)
    tree.SetBranchAddress('lumiNumber', lumi)
    tree.SetBranchAddress('eventNumber', event)

    for ic, cut in enumerate(list(cutflow)):
        if type(cut) is tuple:
            cutflow[ic] = cut[0]
            cutflow.extend(list(cut[1:]))

    tree.Draw('>>elist', ' && '.join(cutflow), 'entrylist')
    elist = ROOT.gDirectory.Get('elist')
    tree.SetEntryList(elist)
    
    evlist = []
    
    iListEntry = 0
    while True:
        iEntry = tree.GetEntryNumber(iListEntry)
        if iEntry < 0:
            break
    
        iListEntry += 1
    
        tree.GetEntry(iEntry)

        # ad-hoc fix
        # L1A comes at ~100kHz * one lumi section is 23 seconds.
        # giving a huge safety factor of allowing 10kHz rate.
        eventNumber = int(event[0])
        if eventNumber < lumi[0] * 23 * 10000:
            eventNumber += 0x100000000

        if args.uwFormat:
            evlist.append((run[0], eventNumber, lumi[0]))
        else:
            evlist.append((run[0], lumi[0], eventNumber))

    evlist.sort()

    outputLines = ['%d:%d:%d' % ev for ev in evlist]

    if args.uwFormat:
        outputLines.sort() # sorted as string

    if args.outName == '':
        args.outName = 'events_' + args.region + '_' + '+'.join(sampleNames) + '.list'

elif args.eventId:
    if args.uwFormat:
        run, event, lumi = map(int, args.eventId.split(':'))
    else:
        run, lumi, event = map(int, args.eventId.split(':'))

    # panda 004 has 32-bit event numbers
    event = event % 0x100000000

    results = {}
    for cuts in cutflow:
        for cut in cuts:
            bit = array.array('B', [0])
            tree.SetBranchAddress(cut, bit)
            results[cut] = bit

    tree.Draw('>>elist', 'runNumber == %d && lumiNumber == %d && eventNumber == %d' % (run, lumi, event), 'entrylist')
    elist = ROOT.gDirectory.Get('elist')

    if elist.GetN() == 0:
        print 'No event %d:%d:%d found' % (run, lumi, event)
        sys.exit(1)

    tree.SetEntryList(elist)
    iEntry = tree.GetEntryNumber(0)
    tree.GetEntry(iEntry)

    outputLines = []
   
    for cuts in cutflow:
        result = 1
        for cut in cuts:
            result *= results[cut][0]

        outputLines.append('%s: %d' % (' && '.join(cuts), result))

    if not args.outName:
        args.outName = '-'

else:
    def formLine(title, ncut, nprev):
        return "%40s %15d %15.4f %15.4e %15.1e" % (title, ncut, float(ncut) / nprev, float(ncut) / ntotal, ROOT.TEfficiency.ClopperPearson(ntotal, ncut, 0.6826895, True) - float(ncut) / ntotal)

    outputLines = []

    outputLines.append('%40s %15s %15s %15s %15s' % ('Cut', 'Events', 'Events/Prev.', 'Events/Total', 'Stat.'))

    outputLines.append(formLine('Total', ntotal, ntotal))

    nevt = tree.GetEntries()
    outputLines.append(formLine('PhotonSkim', nevt, ntotal))

    expr = ''
    for cuts in cutflow:
        if expr == '':
            name = ' && '.join(cuts)
            expr = name
        else:
            name = ' && ' + ' && '.join(cuts)
            expr += name
    
        prev = nevt
        nevt = tree.GetEntries(expr)
        outputLines.append(formLine(name, nevt, prev))

    if args.outName == '':
        args.outName = 'cutflow_' + args.region + '_' + '+'.join(sampleNames) + '.list'

if args.outName == '-':
    for line in outputLines:
        print line

else:
    with open(args.outName, 'w') as output:
        for line in outputLines:
            output.write(line + '\n')
