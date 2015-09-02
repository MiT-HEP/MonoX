#! /usr/bin/env python

from ROOT import *
from colors import *
colors = defineColors()

lumi = 1.0

######################################################

dataDir = "/afs/cern.ch/work/z/zdemirag/work/run2/monojet/monojet13TeV/slimmer/eos/cms/store/user/zdemirag/nero_skim/"

physics_processes = {
        'Zll': { 'label':'Z#rightarrow ll',
                 'color' : colors.keys()[0],
                 'ordering': 1,                  
                 'xsec' : 6025.2,
                 'files':[dataDir+'monojet_dy.root',],
                 },
        'Zvv_ht100': { 'label':'Z#rightarrow#nu#nu',
                       'color' : colors.keys()[4],
                       #'color': ROOT.kAzure+4,
                       'ordering': 4,                  
                       'xsec' : 280.47,
                       'files':[dataDir+'monojet_zvvht100.root',],
                       },
        'Zvv_ht200': { 'label':'Z#rightarrow#nu#nu',
                       'color' : colors.keys()[4],
                       #'color': ROOT.kAzure+4,
                       'ordering': 4,                  
                       'xsec' : 78.36,
                       'files':[dataDir+'monojet_zvvht200.root',],
                       },
        'Zvv_ht400': { 'label':'Z#rightarrow#nu#nu',
                       'color' : colors.keys()[4],
                       #'color': ROOT.kAzure+4,
                       'ordering': 4,                  
                       'xsec' : 10.94,
                       'files':[dataDir+'monojet_zvvht400.root',],
                       },
        'Zvv_ht600': { 'label':'Z#rightarrow#nu#nu',
                       'color' : colors.keys()[4],
                       #'color': ROOT.kAzure+4,
                       'ordering': 4,                  
                       'xsec' : 4.20,
                       'files':[dataDir+'monojet_zvvht600.root',],
                       },
        'Wlv': { 'label':'W#rightarrow  l#nu',
             'color' : colors.keys()[2],
                 #'color': ROOT.kYellow+2,
                 'ordering': 3,                  
                 'xsec' : 61526.7,
                 'files':[dataDir+'monojet_wlv.root',],
                 },
        'others': { 'label':'top',
                    'color' : colors.keys()[1],
                    'ordering': 2,                  
                    'xsec' : 831.76,
                    'files':[dataDir+'monojet_ttbar.root',],
                    },
        #   'QCD': { 'label':'QCD',
        #	    'color' : colors.keys()[3],
        #            'ordering': 0,                  
        #            'xsec' : 831.76,
        #            'files':[dataDir+'monojet_qcd.root',],
        #            },
        'signal_higgs': { 'label':'Higgs',
                          'color' : 1,
                          'ordering': 6,
                          'xsec' : 0.0,
                          'files':[dataDir+'monojet_met_jsn.root',],
                          },
        'data': { 'label':'data',
                  'color': 1,
                  'ordering': 5,    
                  'xsec' : 1.0,
                  'files':[dataDir+'monojet_met_jsn.root',],
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
		Trees[process].AddFriend("type",sample)
		#print process, sample
	return Trees[process]

######################################################
