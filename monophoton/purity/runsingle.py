import os
import sys
import ROOT
#ROOT.gROOT.SetBatch(True)

sourcedir = '/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/SingleMuon+Run2015C-PromptReco-v1+AOD'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
ROOT.gROOT.LoadMacro(TemplateGeneratorPath)

inputTree = ROOT.TChain('events')

for f in os.listdir(sourcedir):
    inputTree.Add(sourcedir + '/' + f)
    break

templateTypes = [ 'photon', 'background' ]
locations = [ 'barrel', 'endcap' ]
photonIds = [ 'loose', 'medium', 'tight' ] 
fakevars = [ 'chIso', 'nhIso', 'phIso', 'hOverE' ]

outfile = ROOT.TFile("photon_purity_templates.root", "RECREATE")

for templateType in xrange(0,ROOT.nTemplateTypes):
    for location in xrange(0,ROOT.nPhotonLocations):
        if (location > 0): continue
        for photonId in xrange(0,ROOT.nPhotonIds):
            for fakevar in xrange(0,ROOT.nFakeVars):
                if ((templateType == 0) and (fakevar > 0)): continue
                generator = ROOT.TemplateGenerator(templateType, ROOT.kSigmaIetaIeta, '/tmp/background.root', True)

                generator.fillSkim(inputTree, fakevar, photonId, location)
                generator.writeSkim()

                generator.setTemplateBinning(40, 0., 0.02)
                tempH = generator.makeTemplate('barrel_inclusive', '') 
                # 'TMath::Abs(selPhotons.eta) < 1.5')

                x = ROOT.RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02)

                temp = ROOT.RooDataHist('temp_'+templateTypes[templateType]+'_'+locations[location]+'_'+photonIds[photonId]+'_'+fakevars[fakevar], 'template_'+templateTypes[templateType]+'_'+locations[location]+'_'+photonIds[photonId]+'_'+fakevars[fakevar], ROOT.RooArgList(x), tempH)
                
                outfile.cd()
                temp.Write()
                
                canvas = ROOT.TCanvas()
                frame = x.frame()
                temp.plotOn(frame)
    
                frame.Draw()

                canvas.SaveAs('template_'+templateTypes[templateType]+'_'+locations[location]+'_'+photonIds[photonId]+'_'+fakevars[fakevar]+'_inclusive.pdf')

sys.stdin.readline()
