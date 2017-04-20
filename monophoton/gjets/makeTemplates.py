import sys
import os
import array
import math
import time
import ROOT
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
import config
from datasets import allsamples

ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('/home/yiiyama/cms/studies/RooFit/libCommonRooFit.so')
ROOT.gROOT.LoadMacro('metTree.cc+')

photonData = ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h'] # ['sph-16c-r'] #

lumi = 0.
for sname in photonData:
    lumi += allsamples[sname].lumi

# direct smear

outputName = config.histDir + '/gjets/fitTemplates.root'
outputFile = ROOT.TFile.Open(outputName, 'recreate')

space = ROOT.RooWorkspace('space', 'space')

dsource = ROOT.TChain('events')
bsource = ROOT.TChain('events')
for sname in photonData:
    dsource.Add(config.skimDir + '/' + sname + '_monoph.root')
    bsource.Add(config.skimDir + '/' + sname + '_hfake.root')
    bsource.Add(config.skimDir + '/' + sname + '_efake.root')

bmcsource = ROOT.TChain('events')
bmcsource.Add(config.skimDir + '/wglo_monoph.root') # inclusive sample - wg130 canno be used because we go lower in MET
bmcsource.Add(config.skimDir + '/wlnu-*_monoph.root')
bmcsource.Add(config.skimDir + '/ttg_monoph.root')
bmcsource.Add(config.skimDir + '/znng-40_monoph.root') 
bmcsource.Add(config.skimDir + '/znng-130_monoph.root') 
bmcsource.Add(config.skimDir + '/zllg-130_monoph.root') 

# znnsource = ROOT.TChain('events')
# znnsource.Add(config.skimDir + '/zg_dimu.root')  # need to replace with new sample

mcsource = ROOT.TChain('events')
mcsource.Add(config.skimDir + '/gj04-40_monoph.root')
mcsource.Add(config.skimDir + '/gj04-100_monoph.root')
mcsource.Add(config.skimDir + '/gj04-200_monoph.root')
mcsource.Add(config.skimDir + '/gj04-400_monoph.root')
mcsource.Add(config.skimDir + '/gj04-600_monoph.root')

binning = array.array('d', [4. * x for x in range(101)])
sel = '(photons.scRawPt[0] > 175. && t1Met.minJetDPhi < 0.5 && t1Met.photonDPhi > 2.)'

dname = 'dmet'
dmet = ROOT.TH1D(dname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
dmet.Sumw2()
start = time.time()
print 'starting drawing data met'
dsource.Draw('t1Met.met>>'+dname, sel, 'goff')
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed
outputFile.cd()
dmet.Write()

start = time.time()
print 'starting making bkgd tree'
btree = ROOT.TTree('btree', 'met')
ROOT.metTree(bsource, btree, sel)
ROOT.metTree(bmcsource, btree, sel, lumi)
# ROOT.metTree(znnsource, btree, sel, lumi * 6.122)
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed

counter = ROOT.TH1D('counter', '', 1, 0., 1.)
start = time.time()
print 'starting drawing bkgd counter'
btree.Draw('0.5>>counter', 'weight', 'goff')
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed
outputFile.cd()
counter.Write()

start = time.time()
print 'starting making mc tree'
mctree = ROOT.TTree('mctree', 'met')
ROOT.metTree(mcsource, mctree, sel)
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed

met = space.factory('met[0., 400.]')
met.setUnit('GeV')
met.setBins(100)

start = time.time()
print 'starting making data hist'
ddata = ROOT.RooDataHist('ddata', 'ddata', ROOT.RooArgList(met), dmet)
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed
outputFile.cd()
ddata.Write()

start = time.time()
print 'starting making bkgd pdf'
bpdf = ROOT.KeysShape('bpdf', 'bpdf', met, btree, 'weight', 0.5, 8)
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed
outputFile.cd()
bpdf.Write()

start = time.time()
print 'Constructing KeysShape from', mcsource.GetEntries(), 'events.'
mcname = 'mcmetLow'
mcpdf = ROOT.KeysShape('mcpdf', 'mcpdf', met, mctree, 'weight', 0.5, 8)
elapsed = time.time() - start
print 'finished. took %i seconds' % elapsed
outputFile.cd()
mcpdf.Write()
 
outputFile.Close()
print 'wrote fit templates to', outputName
