import os
from ROOT import *

gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)

# nTuple location
Version = 'simpletree4'
ntupledir = '/scratch5/yiiyama/hist/'+Version+'/t2mit/filefi/042/'

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

'''
                              ,('TempBkgdGJetsHt040to100',kBackground,23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdGJetsHt100to200',kBackground,9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdGJetsHt200to400',kBackground,2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdGJetsHt400to600',kBackground,273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              ,('TempBkgdGJetsHt600toInf',kBackground,94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
                              '''

# Skims for Purity Calculation
Measurement = { "Wlike_sieie_old" : [ ('TempSignal','TempSignal',kPhoton,'Signal Template from MC') # (selection name, skim file to read from, template type, template title)
                                      ,('TempBkgdData','TempBkgdData',kBackground,'Background Template from Data')
                                      ,('TempBkgdMc','TempBkgdMc',kBackground,'Background Template from MC')
                                      ,('FitData','FitData',kPhoton,'Fit Template from Data')
                                      ,('FitMc','FitMc',kPhoton,'Fit Template from MC')
                                      ,('McTruthSignal','FitMc',kPhoton,'Signal Template from MC Truth')
                                      ,('McTruthBkgd','FitMc',kBackground,'Background Template from MC Truth') ]
                ,"Wlike_sieie_new" : [ ('TempSignalWgPhotons','TempSignalWgPhotons',kPhoton,'Signal Template from W#gamma#rightarrow#ell#nu#gamma MC')
                                       ,('TempBkgdSingleMuon','TempBkgdSingleMuon',kBackground,'Background Template from SingleMuon Data')
                                       ,('TempBkgdWJetsToLNu','TempBkgdWJetsToLNu',kBackground,'Background Template from W+j#rightarrow#ell#nu MC')
                                       ,('FitSingleMuon','FitSingleMuon',kPhoton,'Fit Template from SingleMuon Data')
                                       ,('FitWJetsToLNu','FitWJetsToLNu',kPhoton,'Fit Template from W+jets#rightarrow#ell#nu MC')
                                       ,('WJetsTruthSignal','FitWJetsToLNu',kPhoton,'Signal Template from W+jets#rightarrow#ell#nu MC Truth')
                                       ,('WJetsTruthBkgd','FitWJetsToLNu',kBackground,'Background Template from W+jets#rightarrow#ell#nu MC Truth') ]
                ,"Monophoton_sieie" : [ ( 'TempSignalGJets','TempSignalGJets',kPhoton)
                                        ,('TempBkgdSinglePhoton','TempBkgdSinglePhoton',kBackground)
                                        ,('TempBkgdGJets','TempBkgdGJets',kBackground)
                                        ,('FitSinglePhoton','FitSinglePhoton',kPhoton)
                                        ,('FitGJets','TempSignalGJets',kPhoton)
                                        ,('GJetsTruthSignal','TempSignalGJets',kPhoton)
                                        ,('GJetsTruthBkgd','TempSignalGJets',kBackground) ] 
                ,"CompGammaE_phIso" : [ ( 'TempSignalWgPhotons','TempSignalWgPhotons',kPhoton)
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

Selections = { 'medium_barrel_inclusive' : [ 
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
    Selections['medium_barrel_Wlike_'+cut[0]] = cuts

for cut in cutPhotonPt:
    cuts = [ cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
    Selections['medium_barrel_'+cut[0]] = cuts
