import os
from ROOT import *

gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)

# nTuple location
Version = 'simpletree4'
ntupledir = '/scratch5/yiiyama/hist/'+Version+'/t2mit/filefi/042/'

# Plot output location


# Variables and associated properties
Variables = { "sieie"  : (kSigmaIetaIeta,kChIso,kLoose,RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02),0.0100) # (variable to fit to, sideband variable, selection)
             ,"phIso" : (kPhotonIsolation,kSieie,kLoose,RooRealVar('phIso', 'Ph Iso (GeV)', 0., 0.02),1.33) } # cut is actually a function of pT) }

# Samples for skimming
Regions = { "Wgamma" : [ ( 'TempSignalWgPhotons',kPhoton,405.271,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                         ,('TempBkgdSingleMuon',kBackground,-1,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD')
                         ,('TempBkgdWJetsToLNu',kBackground,60290,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                         ,('FitSingleMuon',kPhoton,-1,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD')
                         ,('FitWJetsToLNu',kPhoton,60290,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM' ) ]
            
            ,"Monophoton" : [ ( 'TempSignalGJetsHt040to100',kPhoton,23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempSignalGJetsHt100to200',kPhoton,9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempSignalGJetsHt200to400',kPhoton,2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempSignalGJetsHt400to600',kPhoton,273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempSignalGJetsHt600toInf',kPhoton,94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdSinglePhoton',kBackground,-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD')               
                              ,('TempBkgdQCDHt200to300',kBackground,1735000,ntupledir+'QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                              ,('TempBkgdQCDHt300to500',kBackground,366800,ntupledir+'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                              ,('TempBkgdQCDHt500to700',kBackground,29370,ntupledir+'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdQCDHt700to1000',kBackground,6524,ntupledir+'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdQCDHt1000to1500',kBackground,1064,ntupledir+'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                              ,('FitSinglePhoton',kPhoton,-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD') ]
            
            ,"ElectronIso" : [ ( 'TempSignalWgPhotons',kPhoton,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                               ,('TempSignalWgElectrons',kElectron,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM') ] }

# Names for plots for Purity Calculation
PlotNames = { "Wlike" : ("Photon Purity in SingleMuon DataSet","Photon Purity in WJets Monte Carlo","Photon Purity in WJets MC Truth")
              ,"Monophoton" : ("Photon Purity in SinglePhoton DataSet","Photon Purity in #gamma+jets and QCD MC","Photon Purity in #gamma+jets and QCD MC Truth") }
               
# Function for making templates!
def TemplateMaker(_var,_skim,_sel,_selName,_skimDir,_plotDir):
    print '\nStarting template:', _skim[0]
        
    inName = os.path.join(_skimDir,'Skim'+_skim[1]+'.root')
    print 'Making template from:', inName
    generator = TemplateGenerator(_skim[2], _var[0], inName)
    generator.setTemplateBinning(40, 0., 0.02)
    
    print 'Applying selection:', _selName
    print _sel, '\n'
    tempH = generator.makeTemplate(_skim[3], _sel)
        
    tempname = 'template_'+_skim[0]+'_'+_selName
    temp = RooDataHist(tempname, tempname, RooArgList(_var[3]), tempH)
    
    canvas = TCanvas()
    frame = _var[3].frame()
    temp.plotOn(frame)
        
    print _skim[3]
    frame.SetTitle(_skim[3])
        
    frame.Draw()
        
    outName = os.path.join(_plotDir,tempname+'.pdf')
    canvas.SaveAs(outName)

    return temp

# Fitting function
def FitTemplates(name,title,var,cut,datahist,sigtemp,bkgtemp):
    nEvents = datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(var), sigtemp) #, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(var), bkgtemp) #, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, 0., nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(datahist) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
    canvas = TCanvas()

    frame = var.frame()
    frame.SetTitle(title)

    datahist.plotOn(frame, RooFit.Name("data"))
    model.plotOn(frame, RooFit.Name("Fit"))
    model.plotOn(frame, RooFit.Components('bkg'),RooFit.Name("fake"),RooFit.LineStyle(kDashed),RooFit.LineColor(kGreen))
    model.plotOn(frame, RooFit.Components('sig'),RooFit.Name("real"),RooFit.LineStyle(kDashed),RooFit.LineColor(kRed))

    
    frame.Draw("goff")
    
    var.setRange("selection",0.0,cut)
    
    fReal = float(sigpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(sigpdf.createIntegral(RooArgSet(var)).getVal())
    fFake = float(bkgpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(bkgpdf.createIntegral(RooArgSet(var)).getVal())
    nReal = fReal * nsig.getVal()
    nFake = fFake * nbkg.getVal()

    # Calculate purity and print results
    print "Number of Real photons passing selection:", nReal
    print "Number of Fake photons passing selection:", nFake
    nTotal = nReal + nFake;
    purity = float(nReal) / float(nTotal)
    print "Purity of Photons is:", purity
    
    upper = TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,True)
    lower = TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,False)

    upSig = upper - purity;
    downSig = purity - lower;
    aveSig = float(upSig + downSig) / 2.0;

    text = TLatex() #0.8,0.7,"Purity: "+str(round(purity,4)))
    text.DrawLatexNDC(0.525,0.8,"Purity: "+str(round(purity,2))+'#pm'+str(round(aveSig,2))) 

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
    # canvas.SetLogy()
    # canvas.SaveAs(name+'_Logy.pdf')

    return (purity, aveSig)

             
# Skims for Purity Calculation
Measurement = { "Wlike_old" : [ ('TempSignal','TempSignal',kPhoton,'Signal Template from MC') # (selection name, skim file to read from, template type, template title)
                                ,('TempBkgdData','TempBkgdData',kBackground,'Background Template from Data')
                                ,('TempBkgdMc','TempBkgdMc',kBackground,'Background Template from MC')
                                ,('FitData','FitData',kPhoton,'Fit Template from Data')
                                ,('FitMc','FitMc',kPhoton,'Fit Template from MC')
                                ,('McTruthSignal','FitMc',kPhoton,'Signal Template from MC Truth')
                                ,('McTruthBkgd','FitMc',kBackground,'Background Template from MC Truth') ]
                ,"Wlike" : [ ('TempSignalWgPhotons','TempSignalWgPhotons',kPhoton,r'Signal Template from W#gamma#rightarrowl#nu#gamma MC')
                             ,('TempBkgdSingleMuon','TempBkgdSingleMuon',kBackground,'Background Template from SingleMuon Data')
                             ,('TempBkgdWJetsToLNu','TempBkgdWJetsToLNu',kBackground,r'Background Template from W+jets#rightarrowl#nu MC')
                             ,('FitSingleMuon','FitSingleMuon',kPhoton,'Fit Template from SingleMuon Data')
                             ,('FitWJetsToLNu','FitWJetsToLNu',kPhoton,r'Fit Template from W+jets#rightarrowl#nu MC')
                             ,('WJetsTruthSignal','FitWJetsToLNu',kPhoton,r'Signal Template from W+jets#rightarrowl#nu MC Truth')
                             ,('WJetsTruthBkgd','FitWJetsToLNu',kBackground,r'Background Template from W+jets#rightarrowl#nu MC Truth') ]
                ,"Monophoton" : [ ( 'TempSignalGJets','TempSignalGJets',kPhoton,r'Signal Template from #gamma+jets MC')
                                  ,('TempBkgdSinglePhoton','TempBkgdSinglePhoton',kBackground,'Background Template from SinglePhoton Data')
                                  ,('TempBkgdQCD','TempBkgdQCD',kBackground,'Background Template from QCD MC')
                                  ,('FitSinglePhoton','FitSinglePhoton',kPhoton,'Fit Template from SinglePhoton Data')
                                  ,('FitGJetsQCD','FitGJetsQCD',kPhoton,r'Fit Template from #gamma+jets and QCD MC')
                                  ,('GJetsQCDTruthSignal','FitGJetsQCD',kPhoton,r'Signal Template from #gamma+jets and QCD MC Truth')
                                  ,('GJetsQCDTruthBkgd','FitGJetsQCD',kBackground,r'Background Template from #gamma+jets and QCD MC Truth') ] 
                ,"MonophotonBkgdComp" : [ ( 'BackCompTotQCD','TempBkgdQCD',kBackground,'Total Background from QCD MC')
                                          ,('BackCompTruQCD','TempBkgdQCD',kBackground,'True Photon Background from QCD MC')
                                          ,('BackCompHadQCD','TempBkgdQCD',kBackground,'Hadron Decay Background from QCD MC')
                                          ,('BackCompMisQCD','TempBkgdQCD',kBackground,"Mis-Reco'd Background from QCD MC") ]
                ,"CompGammaE" : [ ( 'TempSignalWgPhotons','TempSignalWgPhotons',kPhoton)
                                  ,('TempSignalWgElectrons','TempSignalWgElectrons',kElectron) ] }

# Selections for Purity Calculation
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

cutMatchedToPhoton = '(TMath::Abs(selPhotons.matchedGen) == 22)'
cutMatchedToReal = '('+cutMatchedToPhoton+' && (!selPhotons.hadDecay))' 
cutMatchedToHadDecay = '('+cutMatchedToPhoton+' && (selPhotons.hadDecay))'

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

Selections = { 'medium_barrel_inclusive' : [ 
        cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && !'+cutMatchedToReal ]
               ,'medium_barrel_Wlike' : [ 
        cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && !'+cutMatchedToReal ]
               ,'vloose_barrel_Wlike' : [ 
        cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose
        ,cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
        ,cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && !'+cutMatchedToReal  ] }

for cut in cutPhotonPt:
    cuts = [ cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && !'+cutMatchedToReal ]
    Selections['medium_barrel_Wlike_'+cut[0]] = cuts

for cut in cutPhotonPt:
    cuts = [ cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
             ,cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal
             ,cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && !'+cutMatchedToReal ]
    Selections['medium_barrel_'+cut[0]] = cuts

Selections['MonophotonBkgdComp'] = [ cutSelBarrelMedium+' && '+cutPhotonPt[-1][1]+' && !'+cutChIsoBarrelMedium
                                     ,cutSelBarrelMedium+' && '+cutPhotonPt[-1][1]+' && !'+cutChIsoBarrelMedium+' && '+cutMatchedToReal
                                     ,cutSelBarrelMedium+' && '+cutPhotonPt[-1][1]+' && !'+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay
                                     ,cutSelBarrelMedium+' && '+cutPhotonPt[-1][1]+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToPhoton ]

