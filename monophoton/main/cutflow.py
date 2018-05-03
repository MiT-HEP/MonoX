
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
argParser.add_argument('--flow', '-f', metavar = 'CUTS', nargs = '+', dest = 'cutflow', help = 'Cutflow. Can be "all" for --cut-results')
argParser.add_argument('--cut-results', '-r', metavar = 'EVENTID', nargs = '+', dest = 'eventIds', help = 'Show results of the cuts on a specific event.')
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
        for fname in sample.files():
            source = ROOT.TFile.Open(fname)
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
    ]

    if args.region in ['monoph', 'efake']:
        cutflow += [
            ('Met',),
            ('PhotonMetDPhi',),
            ('LeptonSelection',),
            ('JetMetDPhi',),
            ('PhotonPtOverMet',),
            # ('TauVeto',)
        ]

    elif args.region == 'monoel':
        cutflow += [
            ('LeptonSelection',),
            ('RealMetCut',),
            ('LeptonMt',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('JetMetDPhi',),
            ('PhotonPtOverMet',),
        ]

    elif args.region == 'monomu':
        cutflow += [
            ('LeptonSelection',),
            ('LeptonMt',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('JetMetDPhi',),
            ('PhotonPtOverMet',),
        ]

    elif args.region in ['dimu', 'diel']:
        cutflow += [
            ('LeptonSelection',),
            ('OppositeSign',),
            ('Met',),
            ('PhotonMetDPhi',),
            ('Mass',),
            ('JetMetDPhi',),
            ('PhotonPtOverMet',),
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

    print ' && '.join(cutflow)

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

        eventNumber = int(event[0])

        if data:
            # ad-hoc fix
            # L1A comes at ~100kHz * one lumi section is 23 seconds.
            # giving a huge safety factor of allowing 10kHz rate.
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

elif args.eventIds is not None:
    run = array.array('I', [0])
    lumi = array.array('I', [0])
    event = array.array('I', [0])
    
    tree.SetBranchAddress('runNumber', run)
    tree.SetBranchAddress('lumiNumber', lumi)
    tree.SetBranchAddress('eventNumber', event)

    eventIds = []
    for sid in args.eventIds:
        if args.uwFormat:
            r, e, l = map(int, sid.split(':'))
        else:
            r, l, e = map(int, sid.split(':'))

        # panda 004 has 32-bit event numbers
        e = e % 0x100000000

        eventIds.append((r, l, e))

    if cutflow[0][0] == 'all':
        cutflow = []
        tree.LoadTree(0)
        for branch in tree.GetListOfBranches():
            if branch.GetName() != 'runNumber' and branch.GetName() != 'lumiNumber' and branch.GetName() != 'eventNumber':
                cutflow.append((branch.GetName(),))

    results = {}
    for cuts in cutflow:
        for cut in cuts:
            bit = array.array('B', [0])
            tree.SetBranchAddress(cut, bit)
            results[cut] = bit

    sels = []
    for eventId in eventIds:
        sels.append('(runNumber == %d && lumiNumber == %d && eventNumber == %d)' % eventId)

    tree.Draw('>>elist', ' || '.join(sels), 'entrylist')
    elist = ROOT.gDirectory.Get('elist')

    if elist.GetN() == 0:
        print 'No event found:', eventIds
        sys.exit(1)

    outputLines = []

    tree.SetEntryList(elist)
    for iL in range(elist.GetN()):
        iEntry = tree.GetEntryNumber(iL)
        tree.GetEntry(iEntry)

        outputLines.append('=== %d:%d:%d ===' % (run[0], lumi[0], event[0]))
       
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
