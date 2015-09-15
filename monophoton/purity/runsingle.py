import os
import sys
import ROOT
#ROOT.gROOT.SetBatch(True)

sourcedir = '/scratch5/yiiyama/hist/simpletree/t2mit/filefi/042/SingleMuon+Run2015C-PromptReco-v1+AOD'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro('TemplateGenerator.cc+')

generator = ROOT.TemplateGenerator(ROOT.kBackground, ROOT.kSigmaIetaIeta, '/tmp/background.root', True)

inputTree = ROOT.TChain('events')

for f in os.listdir(sourcedir):
    inputTree.Add(sourcedir + '/' + f)
    break

generator.fillSkim(inputTree)
generator.writeSkim()

generator.setTemplateBinning(40, 0., 0.02)
tempH = generator.makeTemplate('barrel_inclusive', 'TMath::Abs(selPhotons.eta) < 1.5')

x = ROOT.RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02)

temp = ROOT.RooDataHist('temp', 'template', ROOT.RooArgList(x), tempH)

frame = x.frame()
temp.plotOn(frame)

frame.Draw()

sys.stdin.readline()
