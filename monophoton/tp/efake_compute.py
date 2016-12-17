#!/usr/bin/env python

import sys
import os
import array
import math
import collections

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
from tp.efake_conf import lumiSamples, outputDir, getBinning

dataType = sys.argv[1]
binningName = sys.argv[2]

binningTitle, binning, fitBins = getBinning(binningName)

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

inputTree = ROOT.TChain('yields')
inputTree.Add(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')
if os.path.exists(outputDir + '/toys_' + dataType + '_' + binningName + '.root'):
    inputTree.Add(outputDir + '/toys_' + dataType + '_' + binningName + '.root')
    toyUncert = True
else:
    toyUncert = False

vTPconf = array.array('i', [0])
vBinName = array.array('c', '\0' * 128)
vNz = array.array('d', [0.])
vToyNumber = array.array('i', [0])

inputTree.SetBranchAddress('tpconf', vTPconf)
inputTree.SetBranchAddress('binName', vBinName)
inputTree.SetBranchAddress('nz', vNz)
inputTree.SetBranchAddress('toyNumber', vToyNumber)

# 0 -> ee, 1 -> eg
nominal = {'ee': {}, 'eg': {}}
sysshift = {}
toys = {'ee': collections.defaultdict(list), 'eg': collections.defaultdict(list)}

iEntry = 0
while inputTree.GetEntry(iEntry) > 0:
    iEntry += 1

    conf = 'ee' if vTPconf[0] == 0 else 'eg'

    for binName, cut in fitBins:
        if vBinName.tostring().startswith(binName):
            break
    else:
        continue

    if vToyNumber[0] == -1:
        nominal[conf][binName] = vNz[0]
    else:
        toys[conf][binName].append(vNz[0])

if os.path.exists(outputDir + '/tpsyst_' + dataType + '_' + binningName + '.root'):
    source = ROOT.TFile.Open(outputDir + '/tpsyst_' + dataType + '_' + binningName + '.root')
    for altname in ['bkg', 'sig']:
        sysshift[altname] = {}
        for conf in ['ee', 'eg']:
            sysshift[altname][conf] = {}
            for binName, cut in fitBins:
                h = source.Get('pull_' + conf + '_' + altname + '_' + binName)
                if h:
                    print 'Alternative fit', altname, conf, binName, 'found'
                    sysshift[altname][conf][binName] = h.GetMean()

if dataType == 'mc':
    # for mc truth background
    histSource = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')

outputFile = ROOT.TFile.Open(outputDir + '/results_' + dataType + '_' + binningName + '.root', 'recreate')

if binningName == 'pt':
    binning[-1] = binning[-2] + 20.

binLabels = False
if len(binning) == 0:
    binLabels = True
    binning = range(len(fitBins) + 1)

yields = {
    'ee': ROOT.TH1D('ee', '', len(binning) - 1, array.array('d', binning)),
    'eg': ROOT.TH1D('eg', '', len(binning) - 1, array.array('d', binning))
}

frate = ROOT.TH1D('frate', '', len(binning) - 1, array.array('d', binning))

if binLabels:
    for h in [yields['ee'], yields['eg'], frate]:
        for ibin in range(1, len(fitBins) + 1):
            h.GetXaxis().SetBinLabel(ibin, fitBins[ibin - 1][0])

toydists = {}

contents = []
staterrs = []
systerrs = []
mctruth = []

for iBin, (binName, cut) in enumerate(fitBins):
    stat2 = 0.

    toydists[binName] = {}

    for conf in ['ee', 'eg']:
        nom = nominal[conf][binName]

        yields[conf].SetBinContent(iBin + 1, nom)

        err2 = 0.
        if toyUncert:
            tvals = toys[conf][binName]

            tvals.sort()

            outputFile.cd()
            toydist = ROOT.TH1D('toys_' + conf + '_' + binName, '', 100, tvals[0] - (tvals[-1] - tvals[0]) * 0.05, tvals[-1] + (tvals[-1] - tvals[0]) * 0.05)
            for tval in tvals:
                toydist.Fill(tval)

            toydists[binName][conf] = toydist

            outputFile.cd()
            toydist.Write()

            quant = 0
            while quant != len(tvals):
                if tvals[quant] > nom:
                    break
        
                quant += 1

            errLow = nom - tvals[int(0.32 * quant)]
            errHigh = tvals[int((len(tvals) - quant) * 0.32) + quant] - nom

            err2 += math.pow((errLow + errHigh) * 0.5, 2.)
            stat2 += math.pow((errLow + errHigh) * 0.5 / nom, 2.)

        try:
            err2 += math.pow(max(sysshift['sig'][conf][binName], sysshift['bkg'][conf][binName]) * nom, 2.)
        except:
            pass

        yields[conf].SetBinError(iBin + 1, math.sqrt(err2))

    ratio = yields['eg'].GetBinContent(iBin + 1) / yields['ee'].GetBinContent(iBin + 1)
    frate.SetBinContent(iBin + 1, ratio)
    syst2 = 0.
    try:
        sigshift = (1. + sysshift['sig']['eg'][binName]) / (1. + sysshift['sig']['ee'][binName])
        bkgshift = (1. + sysshift['bkg']['eg'][binName]) / (1. + sysshift['bkg']['ee'][binName])
        syst2 = math.pow(max(abs(sigshift - 1.), abs(bkgshift - 1.)), 2.)
    except:
        pass

    frate.SetBinError(iBin + 1, ratio * math.sqrt(stat2 + syst2))

    contents.append(ratio)
    staterrs.append(ratio * math.sqrt(stat2))
    systerrs.append(ratio * math.sqrt(syst2))

    if dataType == 'mc':
        eehist = histSource.Get('target_ee_' + binName)
        eghist = histSource.Get('target_eg_' + binName)
        eehist.Add(histSource.Get('mcbkg_ee_' + binName), -1.)
        eghist.Add(histSource.Get('mcbkg_eg_' + binName), -1.)

        ratio = eghist.Integral(61, 120) / eehist.Integral(61, 120)
        mctruth.append(ratio)

outputFile.cd()
frate.Write()
yields['ee'].Write()
yields['eg'].Write()

lumi = sum(allsamples[s].lumi for s in lumiSamples)

frate.SetMaximum(0.05)

canvas = SimpleCanvas(lumi = lumi, sim = (dataType == 'mc'))
canvas.legend.setPosition(0.7, 0.8, 0.9, 0.9)
canvas.legend.add('frate', 'R_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
canvas.legend.apply('frate', frate)
canvas.ylimits = (0., 0.05)
canvas.SetGrid(True, True)
canvas.addHistogram(frate, drawOpt = 'EP')

canvas.xtitle = binningTitle
canvas.printWeb('efake', 'frate_' + dataType + '_' + binningName, logy = False)

for iBin, (binName, cut) in enumerate(fitBins):
    if dataType == 'mc':
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2} (mc %.3f)' % (binName, contents[iBin] * 100., staterrs[iBin] * 100., systerrs[iBin] * 100., mctruth[iBin] * 100.)
    else:
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2}' % (binName, contents[iBin] * 100., staterrs[iBin] * 100., systerrs[iBin] * 100.)

if toyUncert and binningName == 'highpt':
    binName = 'pt_175_6500'
    for conf in ['ee', 'eg']:
        canvas.Clear(full = True)
        canvas.ylimits = (0., 0.05)
        canvas.xtitle = 'N_{Z}'

        toydist = toydists[binName][conf]
        toydist.Scale(1. / toydist.GetSumOfWeights())

        canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
        canvas.legend.add('toys', title = 'Toys', opt = 'LF', color = ROOT.kBlue - 7, lwidth = 2, fstyle = 3003)
        canvas.legend.add('nominal', title = 'Nominal', opt = 'L', color = ROOT.kBlack, lwidth = 2)

        canvas.legend.apply('toys', toydist)

        canvas.addHistogram(toydist, drawOpt = 'HIST')
        canvas.Update(logy = False)
        arrow = canvas.addLine(nominal[conf][binName], toydist.GetMaximum() * 0.2, nominal[conf][binName], 0., width = 2, cls = ROOT.TArrow)
        arrow.SetArrowSize(0.1)

        arrow = ROOT.TArrow(nominal[conf][binName], toydist.GetMaximum() * 0.2, nominal[conf][binName], 0.)
        arrow.Draw()

        canvas.legend.apply('nominal', arrow)

        canvas.printWeb('efake', 'toys_' + dataType + '_' + conf + '_' + binName, logy = False)

outputFile.Close()
