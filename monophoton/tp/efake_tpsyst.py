#!/usr/bin/env python

"""
Fit with alternative models to evaluate fit-related uncertainties.
"""

import os
import sys
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from tp.efake_conf import skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning

ROOT.gSystem.Load('libRooFit.so')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

binningName = sys.argv[1] # see efake_conf
binName = sys.argv[2]
alt = sys.argv[3]
nToys = int(sys.argv[4])
seed = int(sys.argv[5])

output = ROOT.TFile.Open(outputDir + '/tpsyst_data_' + alt + '_' + binningName + '_' + binName + '_' + str(seed) + '.root', 'recreate')

nomSource = ROOT.TFile.Open(outputDir + '/fityields_data_' + binningName + '.root')
altSource = ROOT.TFile.Open(outputDir + '/fityields_data_' + binningName + '_alt' + alt + '.root')

nomWork = nomSource.Get('work')
altWork = altSource.Get('work')

paramList = ['nbkg', 'nsignal']
if alt == 'sig':
    paramList += ['mZ', 'gammaZ']
elif alt == 'bkg':
    paramList.append('slope')

mass = nomWork.arg('mass')
massSet = ROOT.RooArgSet(mass)
nsig = nomWork.arg('nsignal')

altMass = altWork.arg('mass')
params = dict([(n, altWork.arg(n)) for n in paramList])

tree = altSource.Get('yields')
vTPconf = array.array('i', [0])
vBinName = array.array('c', '\0' * 128)
vRaw = array.array('d', [0.])
vParams = dict([(name, array.array('d', [0.])) for name in paramList])

tree.SetBranchAddress('tpconf', vTPconf)
tree.SetBranchAddress('binName', vBinName)
tree.SetBranchAddress('raw', vRaw)
for name in paramList:
    tree.SetBranchAddress(name, vParams[name])

ROOT.RooRandom.randomGenerator().SetSeed(seed)

for conf, iconf in [('ee', 0), ('eg', 1)]:
    output.cd()
    outhist = ROOT.TH1D('pull_' + conf + '_' + alt + '_' + binName, '', 100, -0.5, 0.5)

    model = nomWork.pdf('model_' + conf + '_' + binName)
    altModel = altWork.pdf('model_' + conf + '_' + binName)

    iEntry = 0
    while True:
        if tree.GetEntry(iEntry) < 0:
            raise RuntimeError('entry not found')

        if vTPconf[0] == iconf and vBinName.tostring().startswith(binName):
            break

        iEntry += 1

    for name, p in vParams.items():
        params[name].setVal(p[0])

    for iToy in range(nToys):
        altData = altModel.generate(ROOT.RooArgSet(altMass), vRaw[0])
        data = ROOT.RooDataSet('data', 'data', massSet)
        for iEntry in range(altData.numEntries()):
            mass.setVal(altData.get(iEntry)['mass'].getVal())
            data.add(massSet)
        
        model.fitTo(data)

        diff = nsig.getVal() - params['nsignal'].getVal()
        outhist.Fill(diff / params['nsignal'].getVal())

    output.cd()
    outhist.Write()

output.Close()
