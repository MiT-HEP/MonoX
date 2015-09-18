import os
import sys
from ROOT import *
#ROOT.gROOT.SetBatch(True)


gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)

# Template info
skims = [ 'TempSignal', 'TempBkgdData', 'TempBkgdMc', 'FitData', 'FitMc' ]
templateTypes = [ kPhoton, kBackground, kBackground, kPhoton, kPhoton ]

# Additional selections to apply
cutBarrel = '(TMath::Abs(selPhotons.eta) < 1.5)'
cutEndcap = '((TMath::Abs(selPhotons.eta) > 1.5) && (TMath::Abs(SelPhotons.eta) < 2.4))'
cutEoverH = '(selPhotons.hOverE < 0.05)'

cutChIsoBarrelVLoose = '(selPhotons.chIso < 4.44)'

cutSieieBarrelMedium = '(selPhotons.sieie < 0.0100)'
cutChIsoBarrelMedium = '(selPhotons.chIso < 1.31)'
cutNhIsoBarrelMedium = '(selPhotons.nhIso < (0.60 + TMath::Exp(0.0044*selPhotons.pt+0.5809)))'
cutPhIsoBarrelMedium = '(selPhotons.phIso < (1.33 + 0.0043*selPhotons.pt))'
cutSelBarrelMedium = '('+cutBarrel+' && '+cutEoverH+' && '+cutNhIsoBarrelMedium+' && '+cutPhIsoBarrelMedium+')'

cutMatchedToReal = '((TMath::Abs(selPhotons.matchedGen) == 22) && (!selPhotons.hadDecay))' 

cutSingleMuon = '(muons.size == 1)'
cutElectronVeto = '(electrons.size == 0)'
cutTauVeto = '(ntau == 0)'
cutMet20 = '(t1Met.met > 20)'
cutWlike = '('+cutSingleMuon+' && '+cutElectronVeto+' && '+cutTauVeto+' && '+cutMet20+')'

selections = { 'medium_barrel_inclusive' : [ 
        cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal 
        ,cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium ]
               ,'medium_barrel_Wlike' : [ 
        cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal 
        ,cutSelBarrelMedium+' &&'+cutWlike+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' &&'+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal
        ,cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium ]
               ,'vloose_barrel_Wlike' : [ 
        cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal 
        ,cutSelBarrelMedium+' &&'+cutWlike+' && !'+cutChIsoBarrelVLoose
        ,cutSelBarrelMedium+' &&'+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal
        ,cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' &&'+cutWlike+' && '+cutChIsoBarrelMedium ] }

# Make templates from skims
templates = []
sieie = RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02)
sel = 'vloose_barrel_Wlike'
for skim in xrange(0,5):
    print 'Starting template:', skims[skim]
    
    inname = '/scratch5/ballen/hist/purity/Skim'+skims[skim]+'.root'
    generator = TemplateGenerator(templateTypes[skim], kSigmaIetaIeta, inname)
    generator.setTemplateBinning(40, 0., 0.02)
    

    tempH = generator.makeTemplate(sel, selections[sel][skim])
    
    tempname = 'template_'+skims[skim]+'_'+sel
    temp = RooDataHist(tempname, tempname, RooArgList(sieie), tempH)
                
    # temp.Write()
    templates.append(temp)
    
    canvas = TCanvas()
    frame = sieie.frame()
    temp.plotOn(frame)

    frame.Draw()

    if (skim < 5): canvas.SaveAs(tempname+'.pdf')

# Fitting function
def FitTemplates(name,var,cut,datahist,sigtemp,bkgtemp):
    nEvents = datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(var), sigtemp, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(var), bkgtemp, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, 0., nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(datahist) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
    canvas = TCanvas()

    frame = var.frame()
    
    datahist.plotOn(frame, RooFit.Name("data"))
    model.plotOn(frame, RooFit.Name("Fit"))
    # model.paramOn(frame)
    model.plotOn(frame, RooFit.Components('bkg'),RooFit.LineStyle(kDashed),RooFit.LineColor(kGreen))
    model.plotOn(frame, RooFit.Components('sig'),RooFit.LineStyle(kDashed),RooFit.LineColor(kRed))
    #sigpdf.plotOn(frame, RooFit.Name("signal"))
    #bkgpdf.plotOn(frame, RooFit.Name("fake"))
    
    frame.Draw("goff")
    canvas.SaveAs(name+'.pdf')
    canvas.SetLogy()
    canvas.SaveAs(name+'_Logy.pdf')
    
    var.setRange("selection",0.0,cut)
    
    fReal = float(sigpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(sigpdf.createIntegral(RooArgSet(var)).getVal())
    fFake = float(bkgpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(bkgpdf.createIntegral(RooArgSet(var)).getVal())
    nReal = fReal * nsig.getVal()
    nFake = fFake * nbkg.getVal()
    # purity = float(nReal) / float(nReal + nFake)
    # purity = nsig / nEvents
    return (nReal,nFake)

# Fit for data
cutSieie = 0.0100
(dataReal,dataFake) = FitTemplates("purity_data_"+sel, sieie, cutSieie, templates[3], templates[0], templates[1])

# Fit for MC
(mcReal, mcFake) = FitTemplates("purity_mc_"+sel, sieie, cutSieie, templates[4], templates[0], templates[2])

# Calculate purity and print results
print "Number of Real photons passing selection in data:", dataReal
print "Number of Fake photons passing selection in data:", dataFake
dataPurity = float(dataReal) / float(dataReal + dataFake)
print "Purity of Photons in Data is:", dataPurity

print "Number of Real photons passing selection in mc:", mcReal
print "Number of Fake photons passing selection in mc:", mcFake
mcPurity = float(mcReal) / float(mcReal + mcFake)
print "Purity of Photons in MC is:", mcPurity

# Check 
