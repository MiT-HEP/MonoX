#! /usr/bin/env python

from ROOT import *
from colors import *
colors = defineColors()

lumi = 1.0

######################################################

#dataDir = "eos/cms/store/user/zdemirag/FrozenMonoJetSlim/"
#dataDir = "/afs/cern.ch/work/d/dabercro/public/Winter15/forZeynep_hadd/"
#dataDir = "/afs/cern.ch/work/z/zdemirag/public/slim_Nov9_new/"

#dataDir = "/tmp/zdemirag/slim_Nov11/"

#dataDir = "/afs/cern.ch/work/z/zdemirag/public/slim_Nov17/"
#dataDir_2 = "/afs/cern.ch/work/z/zdemirag/public/slim_Nov26/"

dataDir = "/afs/cern.ch/work/z/zdemirag/public/slim_unblind/"
dataDir_2 = "/afs/cern.ch/work/z/zdemirag/public/slim_unblind/"
dataDir_eos = "eos/cms/store/user/zdemirag/slim_nov17_bkp/slim_Nov17/"


physics_processes = {
        'QCD_200To300': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          'xsec' : 23080.0,
                          #'xsec' : 1735000.0,
                          'files':[dataDir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                          #'files':[dataDir+'QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                          },
        'QCD_300To500': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          #'xsec' : 366800.0,
                          #'files':[dataDir+'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                          'xsec' : 9235.0,
                          'files':[dataDir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                          },
        'QCD_500To700': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          #'xsec' : 29370.0,
                          #'files':[dataDir+'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                          'xsec' : 2298.0,
                          'files':[dataDir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root']
                          },
        'QCD_700To1000': { 'label':'QCD',
                           'datacard':'qcd',
                           'color' : colors.keys()[1],
                           'ordering': 1,
                           #'xsec' : 6524.0,
                           #'files':[dataDir+'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                           'xsec' : 277.6,
                           'files':[dataDir_2+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                           },
        'QCD_1000To1500': { 'label':'QCD',
                            'datacard':'qcd',
                            'color' : colors.keys()[1],
                            'ordering': 1,
                            #'xsec' : 1064.0,
                            #'files':[dataDir+'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                            'xsec' : 93.47,
                            'files':[dataDir_2+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                            },
        'GJets_40To100': { 'label':'#gamma + jets',
                           'datacard': 'gjets',
                           'color' :  colors.keys()[6],
                           'ordering': 2,
                           'xsec' : 23080.0,
                           'files':[dataDir+'GJets_HT-40To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                           },
        'GJets_100To200': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 9235.0,
                            'files':[dataDir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root'],
                            #'files':[dataDir+'GJets_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                            },
        'GJets_200To400': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 2298.0,
                            'files':[dataDir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2+AODSIM.root']
                            #'files':[dataDir+'GJets_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                           },
        'GJets_400To600': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 277.6,
                            #'files':['/afs/cern.ch/work/z/zdemirag/work/MiniAOD_Monojet/slimmer/GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.root'],
                            'files':[dataDir_2+'GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                            },
        'GJets_600ToInf': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 93.47,
                            #'files':['/afs/cern.ch/work/z/zdemirag/work/MiniAOD_Monojet/slimmer/GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.root'],
                            'files':[dataDir_2+'GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                            },

        #991.600 fb--> 0.991 * 10 pb  
        'signal_dm': { 'label':'AV (2 TeV)',
                          'datacard':'signal',
                          'color' : 1,
                          'ordering': 5,
                          'xsec' : 1.,
                       #  'files':[dataDir+'POWHEG_DMV_NNPDF30_13TeV_Axial_2000_1+dmytro-RunIISpring15DR74-1443420076-108ae665ec5ce369aaa85823c807edf1+USER.root',],
                          'files':[dataDir+'DMV_NNPDF30_Axial_Mphi-2000_Mchi-1_gSM-0p25_gDM-1p0_13TeV-powheg+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root'],
                          },
        'data': { 'label':'Data',
                  'datacard':'data',
                  'color': 1,
                  'ordering': 6,    
                  'xsec' : 1.0,
                  'files':[dataDir_2+'monojet_SinglePhoton+Run2015D.root',],
                  }
        }

tmp = {}
for p in physics_processes: 
	if physics_processes[p]['ordering']>-1: tmp[p] = physics_processes[p]['ordering']
ordered_physics_processes = []

for key, value in sorted(tmp.iteritems(), key=lambda (k,v): (v,k)):
	ordered_physics_processes.append(key)

def makeTrees(process,tree,channel):
	Trees={}
	Trees[process] = TChain(tree)
	for sample in  physics_processes[process]['files']:
		Trees[process].Add(sample)
	return Trees[process]

######################################################
