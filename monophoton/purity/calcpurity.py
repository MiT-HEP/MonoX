import os
import sys
import ROOT
#ROOT.gROOT.SetBatch(True)


ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
ROOT.gROOT.LoadMacro(TemplateGeneratorPath)

skims = [ 'TempSignal', 'TempBkgdData', 'TempBkgdMc', 'FitData', 'FitMc' ]
templateTypes = [ ROOT.kPhoton, ROOT.kBackground, ROOT.kBackground, ROOT.kPhoton, ROOT.kPhoton ]

cutBarrel = '(TMath::Abs(selPhotons.eta) < 1.5)'
cutEndcap = '((TMath::Abs(selPhotons.eta) > 1.5) && (TMath::Abs(SelPhotons.eta) < 2.4))'
cutChIsoMedium = '(selPhotons.chIso < 1.31)'
cutMatchedToReal = '((TMath::Abs(selPhotons.matchedGen) == 22) && (!selPhotons.hadDecay))' 
selections = { 'medium_barrel_inclusive' : [ 
        cutBarrel+' && '+cutChIsoMedium+' && '+cutMatchedToReal 
        ,cutBarrel+' && !'+cutChIsoMedium
        ,cutBarrel+' && !'+cutChIsoMedium+' && !'+cutMatchedToReal
        ,cutBarrel+' && '+cutChIsoMedium
        ,cutBarrel+' && '+cutChIsoMedium ] }

templates = []

for skim in xrange(0,5):
    print 'Starting template:', skims[skim]
    
    inname = '/scratch5/ballen/hist/purity/Skim'+skims[skim]+'.root'
    generator = ROOT.TemplateGenerator(templateTypes[skim], ROOT.kSigmaIetaIeta, inname)
    generator.setTemplateBinning(40, 0., 0.02)
    
    sel = 'medium_barrel_inclusive'
    tempH = generator.makeTemplate(sel, selections[sel][skim])
    
    x = ROOT.RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02)

    tempname = 'template_'+skims[skim]+'_'+sel
    temp = ROOT.RooDataHist(tempname, tempname, ROOT.RooArgList(x), tempH)
                
    temp.Write()
    templates.append(temp)
    
    canvas = ROOT.TCanvas()
    frame = x.frame()
    temp.plotOn(frame)

    frame.Draw()

    canvas.SaveAs(tempname+'.pdf')


