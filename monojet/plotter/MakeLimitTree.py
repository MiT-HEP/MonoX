#! /usr/bin/python

from LimitTreeMaker import newLimitTreeMaker
import cuts
import os
from FileList import theFiles

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160212/'

ltm = newLimitTreeMaker('limits/MonoJetInclusiveLimitsTrees.root')

ltm.SetTreeName('events')
ltm.AddKeepBranch('met')
ltm.AddKeepBranch('genBos_pt')
ltm.AddKeepBranch('jet1Pt')
ltm.AddWeightBranch('mcFactors')
ltm.SetAllHistName('htotal')
ltm.SetOutputWeightBranch('scaleMC_w')
ltm.SetLuminosity(cuts.Luminosity)
    
ltm.AddRegion('Zmm',cuts.ZmmMJ_inc)
ltm.AddRegion('Wmn',cuts.WmnMJ_inc)
ltm.AddRegion('signal',cuts.signalMJ_inc_unblinded)
ltm.AddRegion('Wen',cuts.WenMJ_inc + ' && ' + cuts.ETrigger)
ltm.AddRegion('Zee',cuts.ZeeMJ_inc + ' && ' + cuts.ETrigger)
ltm.AddRegion('gjets',cuts.gjetMJ_inc + ' && ' +  cuts.GTrigger)

for aFile in theFiles:
    if os.path.exists(directory + aFile[0]):
        ltm.AddFile(directory + aFile[0],aFile[1],aFile[2])
    ##
##

ltm.AddExceptionDataCut('Zmm',cuts.METTrigger)
ltm.AddExceptionWeightBranch('Zmm','METTrigger')
ltm.AddExceptionDataCut('Wmn',cuts.METTrigger)
ltm.AddExceptionWeightBranch('Wmn','METTrigger')
ltm.AddExceptionDataCut('signal',cuts.METTrigger)
ltm.AddExceptionWeightBranch('signal','METTrigger')


ltm.ExceptionSkip('gjets','QCD_200To300')
ltm.ExceptionSkip('gjets','QCD_300To500')
ltm.ExceptionSkip('gjets','QCD_500To700')
ltm.ExceptionSkip('gjets','QCD_700To1000')
ltm.ExceptionSkip('gjets','QCD_1000To1500')
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-40To100.root','QCD_40To100',23080.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-100To200.root','QCD_100To200',9235.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-200To400.root','QCD_200To400',2298.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-400To600.root','QCD_400To600',277.6)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-600ToInf.root','QCD_600ToInf',93.47)

ltm.MakeTrees()

ltmJ = newLimitTreeMaker('limits/MonoJetLimitsTrees.root')

ltmJ.SetTreeName('events')
ltmJ.AddKeepBranch('met')
ltmJ.AddKeepBranch('genBos_pt')
ltmJ.AddKeepBranch('jet1Pt')
ltmJ.AddWeightBranch('mcFactors')
ltmJ.SetAllHistName('htotal')
ltmJ.SetOutputWeightBranch('scaleMC_w')
ltmJ.SetLuminosity(cuts.Luminosity)
    
ltmJ.AddRegion('Zmm',cuts.ZmmMJ)
ltmJ.AddRegion('Wmn',cuts.WmnMJ)
ltmJ.AddRegion('signal',cuts.signalMJ_unblinded)
ltmJ.AddRegion('Wen',cuts.WenMJ + ' && ' + cuts.ETrigger)
ltmJ.AddRegion('Zee',cuts.ZeeMJ + ' && ' + cuts.ETrigger)
ltmJ.AddRegion('gjets',cuts.gjetMJ + ' && ' +  cuts.GTrigger)

for aFile in theFiles:
    if os.path.exists(directory + aFile[0]):
        ltmJ.AddFile(directory + aFile[0],aFile[1],aFile[2])
    ##
##

ltmJ.AddExceptionDataCut('Zmm',cuts.METTrigger)
ltmJ.AddExceptionWeightBranch('Zmm','METTrigger')
ltmJ.AddExceptionDataCut('Wmn',cuts.METTrigger)
ltmJ.AddExceptionWeightBranch('Wmn','METTrigger')
ltmJ.AddExceptionDataCut('signal',cuts.METTrigger)
ltmJ.AddExceptionWeightBranch('signal','METTrigger')


ltmJ.ExceptionSkip('gjets','QCD_200To300')
ltmJ.ExceptionSkip('gjets','QCD_300To500')
ltmJ.ExceptionSkip('gjets','QCD_500To700')
ltmJ.ExceptionSkip('gjets','QCD_700To1000')
ltmJ.ExceptionSkip('gjets','QCD_1000To1500')
ltmJ.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-40To100.root','QCD_40To100',23080.0)
ltmJ.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-100To200.root','QCD_100To200',9235.0)
ltmJ.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-200To400.root','QCD_200To400',2298.0)
ltmJ.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-400To600.root','QCD_400To600',277.6)
ltmJ.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-600ToInf.root','QCD_600ToInf',93.47)

ltmJ.MakeTrees()

ltmV = newLimitTreeMaker('limits/MonoVLimitsTrees.root')

ltmV.SetTreeName('events')
ltmV.AddKeepBranch('met')
ltmV.AddKeepBranch('genBos_pt')
ltmV.AddKeepBranch('jet1Pt')
ltmV.AddWeightBranch('mcFactors')
ltmV.SetAllHistName('htotal')
ltmV.SetOutputWeightBranch('scaleMC_w')
ltmV.SetLuminosity(cuts.Luminosity)
    
ltmV.AddRegion('Zmm',cuts.ZmmMV)
ltmV.AddRegion('Wmn',cuts.WmnMV)
ltmV.AddRegion('signal',cuts.signalMV_unblinded)
ltmV.AddRegion('Wen',cuts.WenMV + ' && ' + cuts.ETrigger)
ltmV.AddRegion('Zee',cuts.ZeeMV + ' && ' + cuts.ETrigger)
ltmV.AddRegion('gjets',cuts.gjetMV + ' && ' +  cuts.GTrigger)

for aFile in theFiles:
    if os.path.exists(directory + aFile[0]):
        ltmV.AddFile(directory + aFile[0],aFile[1],aFile[2])
    ##
##

ltmV.AddExceptionDataCut('Zmm',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('Zmm','METTrigger')
ltmV.AddExceptionDataCut('Wmn',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('Wmn','METTrigger')
ltmV.AddExceptionDataCut('signal',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('signal','METTrigger')


ltmV.ExceptionSkip('gjets','QCD_200To300')
ltmV.ExceptionSkip('gjets','QCD_300To500')
ltmV.ExceptionSkip('gjets','QCD_500To700')
ltmV.ExceptionSkip('gjets','QCD_700To1000')
ltmV.ExceptionSkip('gjets','QCD_1000To1500')
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-40To100.root','QCD_40To100',23080.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-100To200.root','QCD_100To200',9235.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-200To400.root','QCD_200To400',2298.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-400To600.root','QCD_400To600',277.6)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-600ToInf.root','QCD_600ToInf',93.47)

ltmV.MakeTrees()
