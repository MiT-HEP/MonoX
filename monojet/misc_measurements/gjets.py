#! /usr/bin/env python

from ROOT import *
from colors import *
colors = defineColors()

lumi = 1.0

######################################################

dataDir = "eos/cms/store/user/zdemirag/MonoJet/Full/V003/"
#"eos/cms/store/user/zdemirag/FrozenMonoJet/"

physics_processes = {
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
        }

tmp = {}
for p in physics_processes: 
	if physics_processes[p]['ordering']>-1: tmp[p] = physics_processes[p]['ordering']
ordered_physics_processes = []

for key, value in sorted(tmp.iteritems(), key=lambda (k,v): (v,k)):
	ordered_physics_processes.append(key)

def makeTrees(process,tree):
	Trees={}
	Trees[process] = TChain(tree)
	for sample in  physics_processes[process]['files']:
		Trees[process].Add(sample)
		#Trees[process].AddFriend("type",sample)
		#print process, sample
	return Trees[process]

######################################################
