import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

ROOT.gROOT.LoadMacro('Skimmer.cc+')

#tree = ROOT.TChain('events')
#tree.Add(config.ntuplesDir + 'filefi/044/SinglePhoton+Run2016B-PromptReco-v2+AOD/*.root')
#
#ROOT.skim(tree, ROOT.kDiphoton, '/scratch5/yiiyama/studies/monophoton16/trigger/trigger_diphoton.root')

#tree = ROOT.TChain('events')
#tree.Add(config.ntuplesDir + 'filefi/044/SingleElectron+Run2016B-PromptReco-v2+AOD/*.root')
#
#ROOT.skim(tree, ROOT.kDielectron, '/scratch5/yiiyama/studies/monophoton16/trigger/trigger_dielectron.root')

#tree = ROOT.TChain('events')
#tree.Add(config.ntuplesDir + 'filefi/044/SingleMuon+Run2016B-PromptReco-v2+AOD/*.root')
#
#ROOT.skim(tree, ROOT.kMuonPhoton, '/scratch5/yiiyama/studies/monophoton16/trigger/trigger_muonphoton.root')

tree = ROOT.TChain('events')
tree.Add(config.ntuplesDir + 'filefi/044/JetHT+Run2016B-PromptReco-v2+AOD/*.root')

ROOT.skim(tree, ROOT.kJetHT, '/scratch5/yiiyama/studies/monophoton16/trigger/trigger_jetht.root')
