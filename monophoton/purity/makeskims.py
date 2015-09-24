import os
import sys
from ROOT import *
#gROOT.SetBatch(True)


gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)

ntupledir = '/scratch5/yiiyama/hist/simpletree3/t2mit/filefi/042/'
#SkimVars = (kSigmaIetaIeta,kChIso,kLoose) # (variable to fit to, sideband variable, selection)
SkimVars = (kPhotonIsolation,kSieie,kLoose) # (variable to fit to, sideband variable, selection)

# Wgamma events
'''
sourcedirs = [
    ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM'
    ,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD'
    ,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM'
    ,ntupledir+'SingleMuon+Run2015C-PromptReco-v1+AOD'
    ,ntupledir+'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM' ]

skims = [ 'TempSignal', 'TempBkgdData', 'TempBkgdMc', 'FitData', 'FitMc' ]
templateTypes = [ kPhoton, kBackground, kBackground, kPhoton, kPhoton ]

'''
# SinglePhoton PD

skims = [ ( 'TempSignalGJetsHt040to100',kPhoton,23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempSignalGJetsHt100to200',kPhoton,9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempSignalGJetsHt200to400',kPhoton,2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempSignalGJetsHt400to600',kPhoton,273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempSignalGJetsHt600toInf',kPhoton,94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempBkgdSinglePhoton',kBackground,-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD')
          ,('TempBkgdGJetsHt040to100',kBackground,23080,ntupledir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempBkgdGJetsHt100to200',kBackground,9110,ntupledir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempBkgdGJetsHt200to400',kBackground,2281,ntupledir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempBkgdGJetsHt400to600',kBackground,273,ntupledir+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempBkgdGJetsHt600toInf',kBackground,94.5,ntupledir+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('FitSinglePhoton',kPhoton,-1,ntupledir+'SinglePhoton+Run2015C-PromptReco-v1+AOD') ]


# Electron iso studies
'''
skims = [ ( 'TempSignalWgPhotons',kPhoton,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM')
          ,('TempSignalWgElectrons',kElectron,-1,ntupledir+'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM') ]
'''
for skim in skims:
    print 'Starting skim:', skim[0]
    inputTree = TChain('events')
    
    print 'Adding files from:', skim[-1]
    for f in os.listdir(skim[-1]):
        print 'Adding file: ', str(f)
        inputTree.Add(skim[-1] + '/' + f)
        break

    outname = '/scratch5/ballen/hist/purity/simpletree3/Skim'+skim[0]+'.root'
    print 'Saving skim to:', outname
    generator = TemplateGenerator(skim[1], SkimVars[0], outname, True)
    generator.fillSkim(inputTree, SkimVars[1], SkimVars[2], skim[2])
    generator.writeSkim()
