import os
import sys
from ROOT import *
#ROOT.gROOT.SetBatch(True)

# Fitting function
def FitTemplates(name,title,var,cut,datahist,sigtemp,bkgtemp):
    nEvents = datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(var), sigtemp, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(var), bkgtemp, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, 0., nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(datahist) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
    canvas = TCanvas()

    frame = var.frame()
    frame.SetTitle(title)

    datahist.plotOn(frame, RooFit.Name("data"))
    model.plotOn(frame, RooFit.Name("Fit"))
    # model.paramOn(frame)
    model.plotOn(frame, RooFit.Components('bkg'),RooFit.Name("fake"),RooFit.LineStyle(kDashed),RooFit.LineColor(kGreen))
    model.plotOn(frame, RooFit.Components('sig'),RooFit.Name("real"),RooFit.LineStyle(kDashed),RooFit.LineColor(kRed))
    #sigpdf.plotOn(frame, RooFit.Name("signal"))
    #bkgpdf.plotOn(frame, RooFit.Name("fake"))
    
    frame.Draw("goff")
    
    var.setRange("selection",0.0,cut)
    
    fReal = float(sigpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(sigpdf.createIntegral(RooArgSet(var)).getVal())
    fFake = float(bkgpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(bkgpdf.createIntegral(RooArgSet(var)).getVal())
    nReal = fReal * nsig.getVal()
    nFake = fFake * nbkg.getVal()

    # Calculate purity and print results
    print "Number of Real photons passing selection:", nReal
    print "Number of Fake photons passing selection:", nFake
    purity = float(nReal) / float(nReal + nFake)
    print "Purity of Photons is:", purity
    
    text = TText() #0.8,0.7,"Purity: "+str(round(purity,4)))
    text.DrawTextNDC(0.6,0.8,"Purity: "+str(round(purity,4)))

    leg = TLegend(0.6,0.6,0.85,0.75 );
    leg.SetFillColor(kWhite);
    leg.SetTextSize(0.03);
    # leg.SetHeader("templates LOWER<p_{T}<UPPER");
    leg.AddEntry(frame.findObject("data"), "data", "P");
    leg.AddEntry(frame.findObject("Fit"), "real+fake fit to data", "L");
    leg.AddEntry(frame.findObject("real"), "real", "L"); # model_Norm[sieie]_Comp[sig]
    leg.AddEntry(frame.findObject("fake"), "fake", "L"); # model_Norm[sieie]_Comp[bkg]
    leg.Draw();

    canvas.SaveAs(name+'.pdf')
    canvas.SetLogy()
    canvas.SaveAs(name+'_Logy.pdf')

    return purity

    # purity = float(nReal) / float(nReal + nFake)
    # purity = nsig / nEvents
    # return (nReal,nFake)

gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)

# Template info
# Wlike
#'''
skims = [ ('TempSignal','TempSignal',kPhoton,'Signal Template from MC') # (selection name, skim file to read from, template type, template title)
          ,('TempBkgdData','TempBkgdData',kBackground,'Background Template from Data')
          ,('TempBkgdMc','TempBkgdMc',kBackground,'Background Template from MC')
          ,('FitData','FitData',kPhoton,'Fit Template from Data')
          ,('FitMc','FitMc',kPhoton,'Fit Template from MC')
          ,('McTruthSignal','FitMc',kPhoton,'Signal Template from MC Truth')
          ,('McTruthBkgd','FitMc',kBackground,'Background Template from MC Truth') ]
'''
skims = [ ( 'TempSignalGJets','TempSignalGJets',kPhoton)
          ,('TempBkgdSinglePhoton','TempBkgdSinglePhoton',kBackground)
          ,('TempBkgdGJets','TempBkgdGJets',kBackground)
          ,('FitSinglePhoton','FitSinglePhoton',kPhoton)
          ,('FitGJets','TempSignalGJets',kPhoton)
          ,('GJetsTruthSignal','TempSignalGJets',kPhoton)
          ,('GJetsTruthBkgd','TempSignalGJets',kBackground) ] 
'''
# Additional selections to apply
cutEventWeight = '(weight) *'

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
cutMatchedToHadDecay = '((TMath::Abs(selPhotons.matchedGen) == 22) && (selPhotons.hadDecay))'

cutPhotonPt = [ ('PhotonPt20to60', '((selPhotons.pt > 20) && (selPhotons.pt < 60) )')
                ,('PhotonPt60to100', '((selPhotons.pt > 60) && (selPhotons.pt < 100) )')
                #    ,('PhotonPt100toInf', '((selPhotons.pt > 100))') ]
                ,('PhotonPt100to140', '((selPhotons.pt > 100) && (selPhotons.pt < 140) )')
                ,('PhotonPt140to180', '((selPhotons.pt > 140) && (selPhotons.pt < 180) )')
                ,('PhotonPt180toInf', '((selPhotons.pt > 180) )') ]

cutSingleMuon = '(muons.size == 1)'
cutElectronVeto = '(electrons.size == 0)'
cutTauVeto = '(ntau == 0)'
cutMet20 = '(t1Met.met > 20)'
cutWlike = '('+cutSingleMuon+' && '+cutElectronVeto+' && '+cutTauVeto+' && '+cutMet20+')'

selections = { 'medium_barrel_inclusive' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
               ,'medium_barrel_Wlike' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
               ,'vloose_barrel_Wlike' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')'  ] }

for cut in cutPhotonPt:
    cuts = [ cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
    selections['medium_barrel_Wlike_'+cut[0]] = cuts

for cut in cutPhotonPt:
    cuts = [ cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
    selections['medium_barrel_'+cut[0]] = cuts

# Make templates from skims
sieie = RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02)
cutSieie = 0.0100
# sel = 'vloose_barrel_Wlike'
# sels = ['medium_barrel_'+cut[0] for cut in cutPhotonPt]
sels = ['medium_barrel_Wlike'] #PhotonPt180toInf']
purities = [[],[],[],[]]
for sel in sels:
    templates = []
    for skim in xrange(0,len(skims)):
        print '\nStarting template:', skims[skim][0]
        
        inname = '/scratch5/ballen/hist/purity/simpletree3/Skim'+skims[skim][1]+'_Wlike.root'
        print 'Making template from:', inname
        generator = TemplateGenerator(skims[skim][2], kSigmaIetaIeta, inname)
        generator.setTemplateBinning(40, 0., 0.02)
        
        print 'Applying selection:', sel
        print selections[sel][skim], '\n'
        tempH = generator.makeTemplate(sel, selections[sel][skim])
        
        tempname = 'template_'+skims[skim][0]+'_'+sel
        temp = RooDataHist(tempname, tempname, RooArgList(sieie), tempH)
        
        # temp.Write()
        templates.append(temp)
        
        canvas = TCanvas()
        frame = sieie.frame()
        temp.plotOn(frame)
        
        frame.SetTitle(skims[skim][3])

        frame.Draw()
        
        canvas.SaveAs(tempname+'.pdf')


    # Fit for data
    dataTitle = "Photon Purity in SingleMuon DataSet"
    # (dataReal,dataFake) = FitTemplates("purity_data_"+sel, sieie, cutSieie, templates[3], templates[0], templates[1])
    dataPurity = FitTemplates("purity_data_"+sel, dataTitle,  sieie, cutSieie, templates[3], templates[0], templates[1])
    
    # Fit for MC
    mcTitle = "Photon Purity in WJets Monte Carlo"
    # (mcReal, mcFake) = FitTemplates("purity_mc_"+sel, sieie, cutSieie, templates[4], templates[0], templates[2])
    mcPurity = FitTemplates("purity_mc_"+sel, mcTitle, sieie, cutSieie, templates[4], templates[0], templates[2])

    # Fit for MC truth
    truthTitle = "Photon Purity in WJets MC Truth"
    # (truthReal, truthFake) = FitTemplates("purity_mcTruth_"+sel, sieie, cutSieie, templates[4], templates[5], templates[6])
    truthPurity = FitTemplates("purity_mcTruth_"+sel, truthTitle, sieie, cutSieie, templates[4], templates[5], templates[6])

    # Calculate purity and print results
    '''
    print "Number of Real photons passing selection in data:", dataReal
    print "Number of Fake photons passing selection in data:", dataFake
    dataPurity = float(dataReal) / float(dataReal + dataFake)
    '''
    print "Purity of Photons in Data is:", dataPurity
    purities[0].append(dataPurity)

    '''
    print "Number of Real photons passing selection in mc:", mcReal
    print "Number of Fake photons passing selection in mc:", mcFake
    mcPurity = float(mcReal) / float(mcReal + mcFake)
    '''
    print "Purity of Photons in MC is:", mcPurity
    purities[1].append(mcPurity)

    '''
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Fake photons passing selection in mcTruth:", truthFake
    truthPurity = float(truthReal) / float(truthReal + truthFake)
    '''
    print "Purity of Photons in truthFit is:", truthPurity
    purities[2].append(truthPurity)
    
    truthReal = templates[5].sumEntries('sieie < 0.0100')
    truthTotal = templates[4].sumEntries('sieie < 0.0100')
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Total photons passing selection in mcTruth:", truthTotal
    truthPurity = float(truthReal) / float(truthTotal)
    print "Purity of Photons in mcTruth is:", truthPurity
    purities[3].append(truthPurity)

# Plot purities
print "Purity of Photons in Data is:", purities[0]
print "Purity of Photons in MC is:", purities[1]
print "Purity of Photons in truthFit is:", purities[2]
print "Purity of Photons in mcTruth is:", purities[3]

