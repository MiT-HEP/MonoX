import os
import ROOT

Version = 'simpletree5'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
ROOT.gROOT.LoadMacro(TemplateGeneratorPath)

hOverECuts  = [[]] * 2
sieieCuts = [[]] * 2
chIsoCuts = [[]] * 2
nhIsoCuts = [[]] * 2
phIsoCuts = [[]] * 2

ROOT.gROOT.ProcessLine("double cut;")
for iLoc in xrange(0,2):
    for iCut in xrange(0,3):
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::hOverECuts["+str(iLoc)+"]["+str(iCut)+"];")
        # print ROOT.cut
        hOverECuts[iLoc].append(ROOT.cut)
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::sieieCuts["+str(iLoc)+"]["+str(iCut)+"];")
        # print ROOT.cut
        sieieCuts[iLoc].append(ROOT.cut)
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::chIsoCuts["+str(iLoc)+"]["+str(iCut)+"];")
        # print ROOT.cut
        chIsoCuts[iLoc].append(ROOT.cut)
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::nhIsoCuts["+str(iLoc)+"]["+str(iCut)+"];")
        # print ROOT.cut
        nhIsoCuts[iLoc].append(ROOT.cut)
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::phIsoCuts["+str(iLoc)+"]["+str(iCut)+"];")
        # print ROOT.cut
        phIsoCuts[iLoc].append(ROOT.cut)

from ROOT import *

# nTuple location
ntupledir = '/scratch5/yiiyama/hist/'+Version+'/t2mit/filefi/042/'

# Variables and associated properties
# variable Enum, sideband Enum, selection Enum, roofit variable, cut for purity
# [0][1] = barrel medium
Variables = { "sieie"  : (kSigmaIetaIeta,kChIso,kLoose,RooRealVar('sieie', '#sigma_{i#etai#eta}', 0.004, 0.016), 24, sieieCuts[0][1]) # simpletree.Photon.sieieCuts[0][1])
             ,"phIso" : (kPhotonIsolation,kSieie,kLoose,RooRealVar('phIso', 'Ph Iso (GeV)', 0., 10.0), 100, phIsoCuts[0][1]) } # simpletree.Photon.phIsoCuts[0][1]) } 

# Samples for skimming
Regions = { "Wgamma" : [ ( 'TempSignalWgPhotons',kPhoton,405.271,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                         ,('TempBkgdSingleMuon',kBackground,-1,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD')
                         ,('TempBkgdWJetsToLNu',kBackground,60290,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                         ,('FitSingleMuon',kPhoton,-1,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD')
                         ,('FitWJetsToLNu',kPhoton,60290,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM' ) ]
            
            ,"Monophoton" : [ ( 'TempSignalGJets',kPhoton, [ 
                ( 'TempSignalGJetsHt040to100',23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempSignalGJetsHt100to200',9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempSignalGJetsHt200to400',2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempSignalGJetsHt400to600',273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempSignalGJetsHt600toInf',94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM') ] )
                              ,('TempBkgdSinglePhoton',kBackground, [ 
                ( 'TempBkgdSinglePhotonD',-1,ntupledir+'SinglePhoton+Run2015D-PromptReco-v3+AOD')               
                #,('TempBkgdSinglePhotonC',-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD') 
                ] )
                              ,('TempBkgdQCD',kBackground, [ 
                ( 'TempBkgdQCDHt200to300',1735000,ntupledir+'QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                ,('TempBkgdQCDHt300to500',366800,ntupledir+'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                ,('TempBkgdQCDHt500to700',29370,ntupledir+'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdQCDHt700to1000',6524,ntupledir+'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdQCDHt1000to1500',1064,ntupledir+'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM') ] )
                              ,( 'TempBkgdGJets',kBackground, [ 
                ( 'TempBkgdGJetsHt040to100',23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdGJetsHt100to200',9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdGJetsHt200to400',2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdGJetsHt400to600',273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('TempBkgdGJetsHt600toInf',94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM') ] )
                              ,('FitSinglePhoton',kPhoton, [ 
                ( 'FitSinglePhotonD',-1,ntupledir+'SinglePhoton+Run2015D-PromptReco-v3+AOD')
                #,('FitSinglePhotonC',-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD') 
                ] )
                              ,('FitQCD',kPhoton, [ 
                ( 'FitQCDHt200to300',1735000,ntupledir+'QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                ,('FitQCDHt300to500',366800,ntupledir+'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM')
                ,('FitQCDHt500to700',29370,ntupledir+'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('FitQCDHt700to1000',6524,ntupledir+'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                ,('FitQCDHt1000to1500',1064,ntupledir+'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM') ] ) ]
            
            ,"ElectronIso" : [ ( 'TempSignalWgPhotons',kPhoton,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                               ,('TempSignalWgElectrons',kElectron,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM') ] }
               
# Function for making templates!
def HistExtractor(_var,_skim,_sel,_skimDir):
    print '\nStarting template:', _skim[0]
        
    inName = os.path.join(_skimDir,_skim[1]+'.root')
    print 'Making template from:', inName
    generator = TemplateGenerator(_skim[2], _var[0], inName)
    generator.setTemplateBinning(_var[4], _var[3].getMin(), _var[3].getMax())
    
    print 'Applying selection:'
    print _sel, '\n'
    tempH = generator.makeTemplate(_skim[0], _sel)

    return tempH
        
def HistToTemplate(_hist,_var,_skim,_selName,_plotDir):
    tempname = 'template_'+_skim[0]+'_'+_selName
    temp = RooDataHist(tempname, tempname, RooArgList(_var[3]), _hist)
    
    canvas = TCanvas()
    frame = _var[3].frame()
    temp.plotOn(frame)
        
    print _skim[3]
    frame.SetTitle(_skim[3])
        
    frame.Draw()
        
    outName = os.path.join(_plotDir,tempname)
    canvas.SaveAs(outName+'.pdf')
    canvas.SaveAs(outName+'.png')
    canvas.SaveAs(outName+'.C')

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
    text.DrawLatexNDC(0.525,0.8,"Purity: "+str(round(purity,3))+'#pm'+str(round(aveSig,3))) 

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
    canvas.SaveAs(name+'.png')
    canvas.SaveAs(name+'.C')
    
    # canvas.SetLogy()
    # canvas.SaveAs(name+'_Logy.pdf')

    return (purity, aveSig)

# Names for plots for Purity Calculation
PlotNames = { "Wlike" : ("Photon Purity in SingleMuon DataSet","Photon Purity in WJets Monte Carlo","Photon Purity in WJets MC Truth")
              ,"Monophoton" : ("Photon Purity in SinglePhoton DataSet","Photon Purity in #gamma+jets and QCD MC","Photon Purity in #gamma+jets and QCD MC Truth","Photon Purity in SinglePhoton DataSet using Low chIso Sideband","Photon Purity in SinglePhoton DataSet using Medium chIso Sideband","Photon Purity in SinglePhoton DataSet using High chIso Sideband","Photon Purity in Low Sideband Region in SinglePhoton Dataset") }
             
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
                                  ,('FitSinglePhoton','FitSinglePhoton',kPhoton,'Fit Template from SinglePhoton Data')
                                  ,('FitGJetsQCD','FitGJetsQCD',kPhoton,r'Fit Template from #gamma+jets and QCD MC')
                                  ,('GJetsQCDTruthSignal','TempSignalGJets',kPhoton,r'Truth Signal from #gamma+jets MC Truth')
                                  ,('GJetsQCDTruthBkgd','FitQCD',kBackground,r'Truth Background from QCD MC Truth') 
                                  ,('TempBkgdSinglePhoton','TempBkgdSinglePhoton',kBackground,'Background Template from SinglePhoton Data')
                                  #,('TempBkgdSinglePhotonSbLow','TempBkgdSinglePhoton',kBackground,'Low SideBand Background Template from SinglePhoton Data')
                                  #,('TempBkgdSinglePhotonSbMed','TempBkgdSinglePhoton',kBackground,'Medium SideBand Background Template from SinglePhoton Data') 
                                  #,('TempBkgdSinglePhotonSbHii','TempBkgdSinglePhoton',kBackground,'High SideBand Background Template from SinglePhoton Data')
                                  ,('TempBkgdGJetsQCD','TempBkgdGJetsQCD',kBackground,'Background Template from QCD MC')
                                  #,('TempBkgdGJetsQCDSbLow','FitGJetsQCD',kBackground,'Low SideBand Background Template from #gamma+jets and QCD MC')
                                  #,('TempBkgdGJetsQCDSbMed','FitGJetsQCD',kBackground,'Medium SideBand Background Template from #gamma+jets and QCD MC') 
                                  #,('TempBkgdGJetsQCDSbHii','FitGJetsQCD',kBackground,'High SideBand Background Template from #gamma+jets and QCD MC') 
                                  ] 
                ,"MonophotonBkgdComp" : [ ( 'BackCompTotal','FitGJetsQCD',kBackground,'Total Background from QCD MC')
                                          ,('BackCompTrue','FitGJetsQCD',kBackground,'True Photons in Sideband from QCD MC')
                                          ,('BackCompFake','FitGJetsQCD',kBackground,"Fake Photons in Sideband from QCD MC") ]
                ,"CompGammaE" : [ ( 'TempSignalWgPhotons','TempSignalWgPhotons',kPhoton)
                                  ,('TempSignalWgElectrons','TempSignalWgElectrons',kElectron) ] }

# Selections for Purity Calculation
locationSels = []
locationSels.append('(TMath::Abs(selPhotons.eta) < 1.5)')
locationSels.append('((TMath::Abs(selPhotons.eta) > 1.5) && (TMath::Abs(SelPhotons.eta) < 2.4))')

hOverESels  = [[]] * 2
sieieSels = [[]] * 2
chIsoSels = [[]] * 2
nhIsoSels = [[]] * 2
phIsoSels = [[]] * 2
SigmaIetaIetaSels = [[]] * 2
PhotonIsolationSels = [[]] * 2
PogSels = [[]] *2

for iLoc in xrange(0,2):
    for iSel in xrange(0,3):
        hOverESel = '(selPhotons.hOverE < '+str(hOverECuts[iLoc][iSel])+')'
        sieieSel = '(selPhotons.sieie < '+str(sieieCuts[iLoc][iSel])+')'
        chIsoSel = '(selPhotons.chIso < '+str(chIsoCuts[iLoc][iSel])+')'
        nhIsoSel = '(selPhotons.nhIso < '+str(nhIsoCuts[iLoc][iSel])+')'
        phIsoSel = '(selPhotons.phIso < '+str(phIsoCuts[iLoc][iSel])+')'
        hOverESels[iLoc].append(hOverESel)
        sieieSels[iLoc].append(sieieSel)
        chIsoSels[iLoc].append(chIsoSel)
        nhIsoSels[iLoc].append(nhIsoSel)
        phIsoSels[iLoc].append(phIsoSel)
        SigmaIetaIetaSel = '('+locationSels[iLoc]+' && '+hOverESel+' && '+nhIsoSel+' && '+phIsoSel+')'
        PhotonIsolationSel = '('+locationSels[iLoc]+' && '+hOverESel+' && '+chIsoSel+' && '+nhIsoSel+')'
        SigmaIetaIetaSels[iLoc].append(SigmaIetaIetaSel)
        PhotonIsolationSels[iLoc].append(PhotonIsolationSel)

cutChIsoBarrelVLoose = '(selPhotons.chIso < 4.44)'
cutChIsoBarrelSLoose = '(selPhotons.chIso < 8.44)'
        
cutIsLoose = '(selPhotons.loose)'
cutIsMedium = '(selPhotons.medium)'
cutIsTight = '(selPhotons.tight)'

cutMatchedToPhoton = '(TMath::Abs(selPhotons.matchedGen) == 22)'
cutMatchedToReal = '('+cutMatchedToPhoton+' && (!selPhotons.hadDecay) && (selPhotons.drParton > 0.5))' 
# cutMatchedToHadDecay = '('+cutMatchedToPhoton+' && (selPhotons.hadDecay))'

cutPhotonPtLow = range(20,220,40)
cutPhotonPtHigh = [150]+range(200,301,50)+[500] # [150, 200, 300, 400] #range(150,351,100) # 
PhotonPtSels = [ [ ('PhotonPt'+str(cutPhotonPtHigh[0])+'toInf', '((selPhotons.pt > '+str(cutPhotonPtHigh[0])+'))') ]
                 + [ ('PhotonPt'+str(low)+'to'+str(high), '((selPhotons.pt > '+str(low)+') && (selPhotons.pt < '+str(high)+'))') for low, high in zip(cutPhotonPtHigh, cutPhotonPtHigh[1:]) ] 
                 + [ ('PhotonPt'+str(cutPhotonPtHigh[-1])+'toInf', '((selPhotons.pt > '+str(cutPhotonPtHigh[-1])+'))') ]
                 ,[ ( 'PhotonPt20to60', '((selPhotons.pt > 20) && (selPhotons.pt < 60) )')
                    ,('PhotonPt60to100', '((selPhotons.pt > 60) && (selPhotons.pt < 100) )')
                    ,('PhotonPt100to140', '((selPhotons.pt > 100) && (selPhotons.pt < 140) )')
                    ,('PhotonPt140to180', '((selPhotons.pt > 140) && (selPhotons.pt < 180) )')
                    ,('PhotonPt180toInf', '((selPhotons.pt > 180) )') ] ]

cutMet = [000,100,250]
MetSels = [ ('Met'+str(cutMet[0])+'toInf', '((t1Met.met > '+str(cutMet[0])+'))') ] 
MetSels = MetSels + [ ('Met'+str(low)+'to'+str(high),'((t1Met.met  >'+str(low)+') && (t1Met.met < '+str(high)+'))') for low, high in zip(cutMet,cutMet[1:]) ]
MetSels = MetSels + [ ('Met'+str(cutMet[-1])+'toInf', '((t1Met.met > '+str(cutMet[-1])+'))') ]

cutChIsoSb = range(3,11,2)
ChIsoSbSels = [ ('ChIso'+str(low)+'to'+str(high), '((selPhotons.chIso > '+str(low)+') && (selPhotons.chIso < '+str(high)+'))') for low, high in zip(cutChIsoSb, cutChIsoSb[1:]) ]

cutSingleMuon = '(muons.size == 1)'
cutElectronVeto = '(electrons.size == 0)'
cutTauVeto = '(ntau == 0)'
cutMet20 = '(t1Met.met > 20)'
cutWlike = '('+cutSingleMuon+' && '+cutElectronVeto+' && '+cutTauVeto+' && '+cutMet20+')'

Selections = { }
Locations = [ 'barrel', 'endcap' ]
PhotonIds = [ 'loose', 'medium', 'tight' ]

for iLoc in xrange(0,2):
    for iSel in xrange(0,3):
        for ChIsoSbSel in ChIsoSbSels:
            sigSel = SigmaIetaIetaSels[iLoc][iSel]+' && '+chIsoSels[iLoc][iSel]
            sbSel = SigmaIetaIetaSels[iLoc][iSel]+' && '+ChIsoSbSel[1]
            
            Selections[Locations[iLoc]+'_'+PhotonIds[iSel]+'_inclusive'] = [ 
                sigSel+' && '+cutMatchedToReal
                ,sbSel
                ,sbSel
                ,sigSel
                ,sigSel
                ,sigSel+' && '+cutMatchedToReal
                ,sigSel+' && !'+cutMatchedToReal ]
               
            Selections[Locations[iLoc]+'_'+PhotonIds[iSel]+'_Wlike'] = [ 
                sigSel+' && '+cutWlike+' && '+cutMatchedToReal
                ,sbSel+' && '+cutWlike
                ,sbSel+' && '+cutWlike
                ,sigSel+' && '+cutWlike
                ,sigSel+' && '+cutWlike
                ,sigSel+' && '+cutWlike+' && '+cutMatchedToReal
                ,sigSel+' && '+cutWlike+' && !'+cutMatchedToReal ]
            
            Selections[Locations[iLoc]+'_'+PhotonIds[iSel]+'_Wlike_vloose'] = [ 
                sigSel+' && '+cutWlike+' && '+cutMatchedToReal
                ,sbSel+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose
                ,sbSel+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose
                ,sigSel+' && '+cutWlike
                ,sigSel+' && '+cutWlike
                ,sigSel+' && '+cutWlike+' && '+cutMatchedToReal
                ,sigSel+' && '+cutWlike+' && !'+cutMatchedToReal  ]

                

            sigSels = [ sigSel+' && '+cutMatchedToReal
                        ,sigSel
                        ,sigSel
                        ,sigSel # +' && '+cutMatchedToReal
                        ,sigSel # +' && !'+cutMatchedToReal
                        ]
            
            sbSels = [ sbSel+' && !'+cutChIsoBarrelVLoose
                       ,sbSel+' && '+cutChIsoBarrelVLoose
                       ,sbSel+' && !'+cutChIsoBarrelVLoose+' && '+cutChIsoBarrelSLoose
                       ,sbSel+' && !'+cutChIsoBarrelSLoose ]
            
            bkgSels = [ sbSel, sbSel]

            baseSels = sigSels+bkgSels  # +sbSels+sbSels
            baseKey = Locations[iLoc]+'_'+PhotonIds[iSel]+'_'+ChIsoSbSel[0]
            
            compNames = [ 'real', 'low', 'med', 'high' ]
            compMatch = ['',' && '+cutMatchedToReal,' && !'+cutMatchedToReal]
        
            for ptCut in PhotonPtSels[0]:
                ptSels = [sel+' && '+ptCut[1] for sel in baseSels]
                ptKey = baseKey+'_'+ptCut[0]
                Selections[ptKey] = ptSels
              
                compSels = [sbSel+' && '+ptCut[1]+sel for sel in compMatch]
                compKey = ptKey+'_comp'
                Selections[compKey] = compSels

                for metCut in MetSels:
                    metSels = [sel+' && '+metCut[1] for sel in ptSels]
                    metKey = ptKey+'_'+metCut[0]
                    Selections[metKey] = metSels
            
                    compSels = [sbSel+' && '+ptCut[1]+' && '+metCut[1]+sel for sel in compMatch]
                    compKey = metKey+'_comp'
                    Selections[compKey] = compSels
                
            for cut in PhotonPtSels[1]:
                cuts = [ sigSel+' && '+cut[1]+' && '+cutWlike+' && '+cutMatchedToReal
                         ,sbSel+' && '+cut[1]+' && '+cutWlike
                         ,sbSel+' && '+cut[1]+' && '+cutWlike
                         ,sigSel+' && '+cut[1]+' && '+cutWlike
                         ,sigSel+' && '+cut[1]+' && '+cutWlike
                         ,sigSel+' && '+cut[1]+' && '+cutWlike+' && '+cutMatchedToReal
                         ,sigSel+' && '+cut[1]+' && '+cutWlike+' && !'+cutMatchedToReal ]
                Selections[Locations[iLoc]+'_'+PhotonIds[iSel]+'_'+cut[0]+'_Wlike'] = cuts
