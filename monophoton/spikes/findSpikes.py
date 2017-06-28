#!/usr/bin/env python

"""
Find narrow high-pT barrel clusters and dump the source file name, event id, cluster position, and sigma ieta ieta into a text file.R
Resulting text file should be merged into a single list and used to fetch the AOD events.
"""

import os
import sys
import shutil
import array

test = False

if sys.argv[1] == 'skim':
    task = 'skim'
    sname = sys.argv[2]
    fileset = sys.argv[3]
    if len(sys.argv) > 4:
        test = True
else:
    task = 'submit'
    snames = sys.argv[1:]

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

if task == 'submit':
    try:
        os.makedirs(config.histDir + '/findSpikes')
    except OSError:
        pass

    sys.path.append('/home/yiiyama/lib')
    from condor_run import CondorRun
    
    submitter = CondorRun(os.path.realpath(__file__))
    submitter.logdir = '/local/' + os.environ['USER']
    submitter.hold_on_fail = True
    submitter.min_memory = 1

    for sname in snames:
        submitter.pre_args = 'skim ' + sname
    
        filesets = set()
        with open(basedir + '/data/spikes/catalog/' + sname + '.txt') as catalog:
            for line in catalog:
                filesets.add(line.split()[0])
    
        filesets = sorted(list(filesets))
    
        submitter.job_args = filesets
        submitter.job_names = ['%s_%s' % (sname, fileset) for fileset in filesets]
            
        submitter.submit(name = 'findSpikes')

elif task == 'skim':
    import ROOT

    tmpname = '/tmp/' + os.environ['USER'] + '/findSpikes_' + sname + '_' + fileset + '.txt'
    outfile = open(tmpname, 'w')
    
    datadir = '/mnt/hadoop/scratch/yiiyama/ftpanda'

    tree = ROOT.TChain('events')

    with open(basedir + '/data/spikes/catalog/' + sname + '.txt') as catalog:
        for line in catalog:
            if line.split()[0] == fileset:
                print line.split()[1]
                tree.Add(line.split()[1])

    aodname = dict()
    with open(basedir + '/data/spikes/aod/' + sname + '.txt') as aodlist:
        for line in aodlist:
            aodname[os.path.basename(line.strip())] = line.strip()

    tree.Draw('>>elist', 'superClustersFT.rawPt > 175 && TMath::Abs(superClustersFT.eta) < 1.4442 && (superClustersFT.sieie < 0.001 || (superClustersFT.sieie < 0.008 && superClustersFT.sipip < 0.008)) && superClustersFT.trackIso < 5.', 'entrylist')
    elist = ROOT.gDirectory.Get('elist')
    tree.SetEntryList(elist)

    runNumber = array.array('I', [0])
    lumiNumber = array.array('I', [0])
    eventNumber = array.array('I', [0])
    size = array.array('I', [0])
    rawPt = array.array('f', [0.] * 256)
    eta = array.array('f', [0.] * 256)
    phi = array.array('f', [0.] * 256)
    sieie = array.array('f', [0.] * 256)
    sipip = array.array('f', [0.] * 256)
    trackIso = array.array('f', [0.] * 256)

    tree.SetBranchAddress('runNumber', runNumber)
    tree.SetBranchAddress('lumiNumber', lumiNumber)
    tree.SetBranchAddress('eventNumber', eventNumber)
    tree.SetBranchAddress('superClustersFT.size', size)
    tree.SetBranchAddress('superClustersFT.rawPt', rawPt)
    tree.SetBranchAddress('superClustersFT.eta', eta)
    tree.SetBranchAddress('superClustersFT.phi', phi)
    tree.SetBranchAddress('superClustersFT.sieie', sieie)
    tree.SetBranchAddress('superClustersFT.sipip', sipip)
    tree.SetBranchAddress('superClustersFT.trackIso', trackIso)

    iEntry = 0
    while True:
        entryNumber = tree.GetEntryNumber(iEntry)
        iEntry += 1
        if entryNumber < 0:
            break

        tree.GetEntry(entryNumber)

        for iC in xrange(size[0]):
            if rawPt[iC] > 175. and abs(eta[iC]) < 1.4442 and (sieie[iC] < 0.001 or (sieie[iC] < 0.008 and sipip[iC] < 0.008)) and trackIso[iC] < 5.:
                outfile.write('%s %d:%d:%d %f %f %f\n' % (aodname[os.path.basename(tree.GetCurrentFile().GetName())], runNumber[0], lumiNumber[0], eventNumber[0], eta[iC], phi[iC], sieie[iC]))
                break

    outfile.close()

    if not test:
        print 'copying', tmpname
        shutil.copy(tmpname, config.histDir + '/findSpikes/' + sname + '_' + fileset + '.txt')
        os.remove(tmpname)
