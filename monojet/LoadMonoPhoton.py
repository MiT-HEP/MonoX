#! /usr/bin/env python

from ROOT import *
from colors import *
colors = defineColors()

lumi = 1.0

######################################################

#dataDir = "/data/blue/dmdata/V0001/miniaod2nero/monojet/"
dataDir = "/afs/cern.ch/work/d/dabercro/public/Winter15/monojetData/"

physics_processes = {
        'GJets_40To100': { 'label':'#gamma + jets',
                           'color' : colors.keys()[0],
                           'ordering': 1,                  
                           'xsec' : 23080,
                           'files':[dataDir+'monojet_GJets_HT-40To100.root'],
                           },
        'GJets_100To200': { 'label':'#gamma + jets',
                           'color' : colors.keys()[0],
                           'ordering': 1,                  
                           'xsec' : 9110,
                           'files':[dataDir+'monojet_GJets_HT-100To200.root'],
                           },
        'GJets_200To400': { 'label':'#gamma + jets',
                           'color' : colors.keys()[0],
                           'ordering': 1,                  
                           'xsec' : 2281,
                           'files':[dataDir+'monojet_GJets_HT-200To400.root'],
                           },
        'GJets_400To600': { 'label':'#gamma + jets',
                           'color' : colors.keys()[0],
                           'ordering': 1,                  
                           'xsec' : 273,
                           'files':[dataDir+'monojet_GJets_HT-400To600.root'],
                           },
        'GJets_600ToInf': { 'label':'#gamma + jets',
                           'color' : colors.keys()[0],
                           'ordering': 1,                  
                           'xsec' : 94.5,
                           'files':[dataDir+'monojet_GJets_HT-600ToInf.root'],
                           },
        'signal_higgs': { 'label':'Higgs',
                          'color' : 1,
                          'ordering': 6,
                          'xsec' : 0.0,
                          'files':[dataDir+'monojet_SinglePhoton_Run2015C.root',],
                          },
        'data': { 'label':'data',
                  'color': 1,
                  'ordering': 5,    
                  'xsec' : 1.0,
                  'files':[dataDir+'monojet_SinglePhoton_Run2015C.root',],
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
