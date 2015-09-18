import os
import sys
import ROOT
#ROOT.gROOT.SetBatch(True)


ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
ROOT.gROOT.LoadMacro(TemplateGeneratorPath)

sourcedirs = [
    '/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM'
    ,'/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/SingleMuon+Run2015C-PromptReco-v1+AOD'
    ,'/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM'
    ,'/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/SingleMuon+Run2015C-PromptReco-v1+AOD'
    ,'/scratch5/yiiyama/hist/simpletree2/t2mit/filefi/042/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM' ]

skims = [ 'TempSignal', 'TempBkgdData', 'TempBkgdMc', 'FitData', 'FitMc' ]
templateTypes = [ ROOT.kPhoton, ROOT.kBackground, ROOT.kBackground, ROOT.kPhoton, ROOT.kPhoton ]

for skim in xrange(0,5):
    print 'Starting skim:', skims[skim]
    inputTree = ROOT.TChain('events')
    
    print 'Adding files from:', sourcedirs[skim]
    for f in os.listdir(sourcedirs[skim]):
        print 'Adding file: ', str(f)
        inputTree.Add(sourcedirs[skim] + '/' + f)
        # break

    outname = '/scratch5/ballen/hist/purity/Skim'+skims[skim]+'.root'
    print 'Saving skim to:', outname
    generator = ROOT.TemplateGenerator(templateTypes[skim], ROOT.kSigmaIetaIeta, outname, True)

    generator.fillSkim(inputTree, ROOT.kChIso, ROOT.kLoose)
    generator.writeSkim()
