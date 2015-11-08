#! /usr/bin/env python

from ROOT import *
from colors import *
colors = defineColors()

lumi = 1.0

######################################################

dataDir = "eos/cms/store/user/zdemirag/FrozenMonoJetSlim/"

physics_processes = {
        'Zll': { 'label':'Z#rightarrow ll',
                 'datacard':'Zll',
                 'color' : colors.keys()[0],
                 'ordering': 0,                  
                 'xsec' : 6025.2,
                 'files':[dataDir+'monojet_DYJetsToLL_M-50.root',],
                 },
        'Zvv':{ 'label':'Z#rightarrow#nu#nu', 
                    'datacard':'Zvv', 
                    'color' : colors.keys()[4], 
                    'ordering': 4,
                    'xsec' : 15866., 
                    'files':[dataDir+'monojet_DYJetsToNuNu.root',], 
                },
        'Wlv': { 'label':'W#rightarrow  l#nu',
                 'datacard':'Wlv',
                 'color' : colors.keys()[2],
                 'ordering': 1,                  
                 'xsec' : 61527.,
                 'files':[dataDir+'monojet_WJetsToLNu.root',],
                 },
        'others': { 'label':'top + diboson',
                    'datacard':'others',
                    'color' : colors.keys()[3],
                    'ordering': 1,                  
                    'xsec' : 831.76,
                    'files':[dataDir+'monojet_TTJets.root',],
                    },
        'WW' : { 'label':'top + diboson',
                 'datacard':'others',
                 'color':colors.keys()[3],
                 'ordering': 1,
                 'xsec' : 63.21,
                 'files':[dataDir+'monojet_WW.root',],
                 },
        'ZZ' : { 'label':'top + diboson',
                 'datacard':'others',
                 'color':colors.keys()[3],
                 'ordering': 1,
                 'xsec' : 10.32,
                 'files':[dataDir+'monojet_ZZ.root',],
                 },
        'WZ' : { 'label':'top + diboson',
                 'datacard':'others',
                 'color':colors.keys()[3],
                 'ordering': 1,
                 'xsec' : 22.82,
                 'files':[dataDir+'monojet_WZ.root',],
                 },
        'QCD_200To300': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          'xsec' : 1735000.0,
                          'files':[dataDir+'monojet_QCD_HT200to300.root'],
                          },
        'QCD_300To500': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          'xsec' : 366800.0,
                          'files':[dataDir+'monojet_QCD_HT300to500.root'],
                          },
        'QCD_500To700': { 'label':'QCD',
                          'datacard':'qcd',
                          'color' : colors.keys()[1],
                          'ordering': 1,
                          'xsec' : 29370.0,
                          'files':[dataDir+'monojet_QCD_HT500to700.root'],
                          },
        'QCD_700To1000': { 'label':'QCD',
                           'datacard':'qcd',
                           'color' : colors.keys()[1],
                           'ordering': 1,
                           'xsec' : 6524.0,
                           'files':[dataDir+'monojet_QCD_HT700to1000.root'],
                           },
        'QCD_1000To1500': { 'label':'QCD',
                            'datacard':'qcd',
                            'color' : colors.keys()[1],
                            'ordering': 1,
                            'xsec' : 1064.0,
                            'files':[dataDir+'monojet_QCD_HT1000to1500.root'],
                            },
        'GJets_40To100': { 'label':'#gamma + jets',
                           'datacard': 'gjets',
                           'color' :  colors.keys()[6],
                           'ordering': 2,
                           'xsec' : 23080.0,
                           'files':[dataDir+'monojet_GJets_HT-40To100.root'],
                           },
        'GJets_100To200': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 9110.0,
                            'files':[dataDir+'monojet_GJets_HT-100To200.root'],
                            },
        'GJets_200To400': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 2281.0,
                            'files':[dataDir+'monojet_GJets_HT-200To400.root'],
                           },
        'GJets_400To600': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 273.0,
                            'files':[dataDir+'monojet_GJets_HT-400To600.root'],
                            },
        'GJets_600ToInf': { 'label':'#gamma + jets',
                            'datacard': 'gjets',
                            'color' :  colors.keys()[6],
                            'ordering': 2,
                            'xsec' : 94.5,
                            'files':[dataDir+'monojet_GJets_HT-600ToInf.root'],
                            },
        #991.600 fb--> 0.991 * 10 pb  
        'signal_dm': { 'label':'AV (2TeV)',
                          'datacard':'signal',
                          'color' : 1,
                          'ordering': 6,
                          'xsec' : 9.91,
                          'files':[dataDir+'monojet_POWHEG_DMV_NNPDF30_13TeV_Axial_2000_1.root',],
                          },
        'data': { 'label':'data',
                  'datacard':'data',
                  'color': 1,
                  'ordering': 5,    
                  'xsec' : 1.0,
                  'files':[dataDir+'monojet_SinglePhoton+Run2015D.root',],
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
		#Trees[process].AddFriend("type",sample)
		#print process, sample
	return Trees[process]

######################################################
