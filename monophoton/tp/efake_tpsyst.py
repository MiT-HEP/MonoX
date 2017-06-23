#!/usr/bin/env python

"""
Throw toys with nominal and alternative models to evaluate uncertainties.
"""

DEBUG = False

import os
import sys
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from tp.efake_conf import outputDir, roofitDictsDir
import tp.efake_plot as efake_plot

import ROOT

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

dataType = sys.argv[1]
binningName = sys.argv[2] # see efake_conf
bin = sys.argv[3]
conf = sys.argv[4] # ee or eg
alt = sys.argv[5] # nominal, altsig, or altbkg
nToys = int(sys.argv[6])
seed = int(sys.argv[7])

outBaseName = '_'.join([
    'tpsyst',
    dataType,
    conf,
    alt,
    binningName,
    bin,
    str(seed)
]) + '.root'

suffix = conf + '_' + bin

outputName = outputDir + '/' + outBaseName

tmpOutName = '/tmp/' + os.environ['USER'] + '/efake/' + outBaseName
try:
    os.makedirs(os.path.dirname(tmpOutName))
except OSError:
    pass

efake_plot.plotDir = 'efake/debug_' + binningName

output = ROOT.TFile.Open(tmpOutName, 'recreate')

source = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')

work = source.Get('work')
htarg = source.Get('target_' + suffix)

nomparams = work.data('params_nominal')

for ip in range(nomparams.numEntries()):
    nompset = nomparams.get(ip)
    if nompset.find('tpconf').getLabel() == conf and nompset.find('binName').getLabel() == bin:
        break
else:
    raise RuntimeError('Nom pset for ' + suffix + ' not found')

if alt == 'nominal':
    altpset = nompset
else:
    altparams = work.data('params_' + alt)
    
    for ip in range(altparams.numEntries()):
        altpset = altparams.get(ip)
        if altpset.find('tpconf').getLabel() == conf and altpset.find('binName').getLabel() == bin:
            break
    else:
        raise RuntimeError('Alt pset for ' + suffix + ' not found')

mass = work.arg('mass')

ROOT.RooRandom.randomGenerator().SetSeed(seed)

output.cd()
outhist = ROOT.TH1D('pull_' + alt + '_' + suffix, '', 100, -0.5, 0.5)

model = work.pdf('model_' + suffix)

if alt == 'nominal':
    altModel = model
elif alt == 'altsig':
    altModel = work.pdf('model_altsig_' + suffix)
elif alt == 'altbkg':
    altModel = work.pdf('model_altbkg_' + suffix)

for _ in range(nToys):
    # initialize
    itr = altpset.fwdIterator()
    while True:
        param = itr.next()
        if not param:
            break

        if param.IsA() == ROOT.RooRealVar.Class():
            print 'Setting', param.GetName(), 'value to', param.getVal()
            work.var(param.GetName()).setVal(param.getVal())

    if DEBUG:
        print 'Alt model'
        altModel.Print()

    print 'Generating', nompset.find('ntarg').getVal(), 'events'
    # for MC, ntarg is the effective number of entries != htarg integral
    altData = altModel.generate(ROOT.RooArgSet(mass), nompset.find('ntarg').getVal())

    # perform binned fit

    #upcast to call TH1 version of createHistogram()
    altAbsData = ROOT.RooDataSet.Class().DynamicCast(ROOT.RooAbsData.Class(), altData)

    altHist = altAbsData.createHistogram('altData', mass, ROOT.RooFit.Binning('fitWindow'))
    data = ROOT.RooDataHist('altDataHist', 'altDataHist', ROOT.RooArgList(mass), altHist)

    # unbinned fit - need to translate from RooDataSet on "mass" from alt workspace to "mass" in nom workspace
#    data = ROOT.RooDataSet('data', 'data', massSet)
#    for iEntry in range(altData.numEntries()):
#        mass.setVal(altData.get(iEntry)['mass'].getVal())
#        data.add(massSet)

    itr = nompset.fwdIterator()
    while True:
        param = itr.next()
        if not param:
            break

        if param.IsA() == ROOT.RooRealVar.Class():
            print 'Initializing', param.GetName(), 'value to', param.getVal()
            work.var(param.GetName()).setVal(param.getVal())

    if DEBUG:
        print 'Nominal model'
        model.Print()
        work.pdf('sigModel_' + bin).Print()
        work.pdf('bkgModel_' + suffix).Print()

    model.fitTo(data)

    if DEBUG:
        efake_plot.plotFit(mass, data, model, 'data', suffix, plotName = 'debug_tpsyst')

    normYield = work.var('nsignal').getVal() / nompset.find('ntarg').getVal()
    normOriginal = nompset.find('nsignal').getVal() / htarg.GetSumOfWeights()

    outhist.Fill((normYield - normOriginal) / normOriginal)

    altHist.Delete()

output.cd()
outhist.Write()

output.Close()

shutil.copy(tmpOutName, outputName)
