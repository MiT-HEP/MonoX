#! /usr/bin/python

from CrombieTools.AnalysisTools.LimitTreeMaker import *
import CrombieTools.LoadConfig
import os

ltm = newLimitTreeMaker()

ltm.SetTreeName('events')
ltm.AddKeepBranch('met')
ltm.AddKeepBranch('genBos_pt')
ltm.AddKeepBranch('jet1Pt')
ltm.SetAllHistName('htotal')
ltm.SetOutputWeightBranch('scaleMC_w')
ltm.SetReportFrequency(20)

directory = os.environ['CrombieInFilesDir']
if not directory.endswith('/'):
    directory = directory + '/'

ltm.ExceptionSkip('gjets','QCD_100To200')
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

SetupFromEnv(ltm)
ltm.ReadMCConfig(os.environ['CrombieMCConfig'])
ltm.ReadMCConfig(os.environ['CrombieSigConfig'])

if __name__ == '__main__':
    ltm.SetOutFileName('MonoJetIncLimitsTrees.root')
    SetCuts(ltm,'monoJet_inc')
    ltm.MakeTrees()
