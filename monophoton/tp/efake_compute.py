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
from tp.efake_conf import lumiSamples, outputDir, roofitDictsDir, getBinning

dataType = sys.argv[1]
binningName = sys.argv[2]

ADDFIT = False

binningTitle, binning, fitBins = getBinning(binningName)

if binningName == 'pt':
    binning[-1] = binning[-2] + 20.

binLabels = False
if len(binning) == 0:
    binLabels = True
    binning = range(len(fitBins) + 1)

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

ROOT.gStyle.SetNdivisions(510, 'X')

source = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')
work = source.Get('work')
nomparams = work.data('params_nominal')

uncSource = None
if os.path.exists(outputDir + '/tpsyst_' + dataType + '_' + binningName + '.root'):
    uncSource = ROOT.TFile.Open(outputDir + '/tpsyst_' + dataType + '_' + binningName + '.root')

### Set up output

outputFile = ROOT.TFile.Open(outputDir + '/results_' + dataType + '_' + binningName + '.root', 'recreate')

yields = {
    'ee': ROOT.TH1D('ee', '', len(binning) - 1, array.array('d', binning)),
    'eg': ROOT.TH1D('eg', '', len(binning) - 1, array.array('d', binning))
}

frate = ROOT.TH1D('frate', '', len(binning) - 1, array.array('d', binning))

if binLabels:
    for h in [yields['ee'], yields['eg'], frate]:
        for ibin in range(1, len(fitBins) + 1):
            h.GetXaxis().SetBinLabel(ibin, fitBins[ibin - 1][0])

### Compute

toydists = {}

centrals = []
staterrs = []
systerrs = []
mctruth = []

for iBin, (bin, _) in enumerate(fitBins):
    stat2 = 0.

    toydists[bin] = {}

    sigshift = {}
    bkgshift = {}

    for conf in ['ee', 'eg']:
        suffix = conf + '_' + bin

        for ip in range(nomparams.numEntries()):
            nompset = nomparams.get(ip)
            if nompset.find('tpconf').getLabel() == conf and nompset.find('binName').getLabel() == bin:
                break
        else:
            raise RuntimeError('Nom pset for ' + suffix + ' not found')

        nZ = nompset.find('nZ').getVal()
        
        yields[conf].SetBinContent(iBin + 1, nZ)

        err2 = 0.
        if uncSource:
            # compute uncertainties from distributions of nZ-normalized difference of toy yields

            toydist = uncSource.Get('pull_nominal_' + suffix)
            toydists[bin][conf] = toydist

            err2 += math.pow(toydist.GetRMS() * nZ, 2.)
            stat2 += math.pow(toydist.GetRMS(), 2.)

            altsig = uncSource.Get('pull_altsig_' + suffix)
            altbkg = uncSource.Get('pull_altbkg_' + suffix)

            sigshift[conf] = altsig.GetMean()
            bkgshift[conf] = altbkg.GetMean()

            err2 += math.pow(max(abs(sigshift[conf]), abs(bkgshift[conf])) * nZ, 2.)

        yields[conf].SetBinError(iBin + 1, math.sqrt(err2))

    ratio = yields['eg'].GetBinContent(iBin + 1) / yields['ee'].GetBinContent(iBin + 1)
    frate.SetBinContent(iBin + 1, ratio)

    # re-evaluate shift uncertainties for ratios (cancels uncertainty if shape is correlated)
    sig = (1. + sigshift['eg']) / (1. + sigshift['ee'])
    bkg = (1. + bkgshift['eg']) / (1. + sigshift['ee'])
    syst2 = math.pow(max(abs(sig - 1.), abs(bkg - 1.)), 2.)

    frate.SetBinError(iBin + 1, ratio * math.sqrt(stat2 + syst2))

    centrals.append(ratio)
    staterrs.append(ratio * math.sqrt(stat2))
    systerrs.append(ratio * math.sqrt(syst2))

    if dataType == 'mc':
        eehist = source.Get('target_ee_' + bin)
        eghist = source.Get('target_eg_' + bin)
        eehist.Add(source.Get('mcbkg_ee_' + bin), -1.)
        eghist.Add(source.Get('mcbkg_eg_' + bin), -1.)

        ratio = eghist.Integral(61, 120) / eehist.Integral(61, 120)
        mctruth.append(ratio)

outputFile.cd()
frate.Write()
yields['ee'].Write()
yields['eg'].Write()

### Visualize

lumi = sum(allsamples[s].lumi for s in lumiSamples)

frate.SetMaximum(0.05)

canvas = SimpleCanvas(lumi = lumi, sim = (dataType == 'mc'))
canvas.legend.setPosition(0.7, 0.8, 0.9, 0.9)
canvas.legend.add('frate', 'R_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
canvas.legend.apply('frate', frate)
canvas.ylimits = (0., 0.05)
canvas.SetGrid(False, True)
canvas.addHistogram(frate, drawOpt = 'EP')

if ADDFIT:
    power = ROOT.TF1('power', '[0] + [1] / (x - [2])', frate.GetXaxis().GetXmin(), frate.GetXaxis().GetXmax())
    power.SetParameters(0.02, 1., 0.)
    frate.Fit(power)
    canvas.addObject(power)

    text = 'f = %.4f + #frac{%.3f}{p_{T}' % (power.GetParameter(0), power.GetParameter(1))
    if power.GetParameter(2) >= 0.:
        text += ' - %.2f}' % power.GetParameter(2)
    else:
        text += ' + %.2f}' % (-power.GetParameter(2))

    canvas.addText(text, 0.3, 0.3, 0.5, 0.2)

canvas.xtitle = binningTitle
canvas.printWeb('efake', 'frate_' + dataType + '_' + binningName, logy = False)

for iBin, (bin, _) in enumerate(fitBins):
    if dataType == 'mc':
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2} (mc %.3f)' % (bin, centrals[iBin] * 100., staterrs[iBin] * 100., systerrs[iBin] * 100., mctruth[iBin] * 100.)
    else:
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2}' % (bin, centrals[iBin] * 100., staterrs[iBin] * 100., systerrs[iBin] * 100.)

if uncSource:
    for conf in ['ee', 'eg']:
        for bin, _ in fitBins:
            canvas.Clear(full = True)
            canvas.ylimits = (0., 0.05)
            canvas.xtitle = 'N_{Z}'
    
            canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
            canvas.legend.add('toys', title = 'Toys', opt = 'LF', color = ROOT.kBlue - 7, lwidth = 2, fstyle = 3003)
            canvas.legend.add('nominal', title = 'Nominal', opt = 'L', color = ROOT.kBlack, lwidth = 2)

            for ip in range(nomparams.numEntries()):
                nompset = nomparams.get(ip)
                if nompset.find('tpconf').getLabel() == conf and nompset.find('binName').getLabel() == bin:
                    break
            else:
                raise RuntimeError('Nom pset for ' + suffix + ' not found')

            nZ = nompset.find('nZ').getVal()

            toydist = toydists[bin][conf]
            toydist.Scale(1. / toydist.GetSumOfWeights())
    
            canvas.legend.apply('toys', toydist)
    
            canvas.addHistogram(toydist, drawOpt = 'HIST')
            canvas.Update(logy = False)
            arrow = canvas.addLine(nZ, toydist.GetMaximum() * 0.2, nZ, 0., width = 2, cls = ROOT.TArrow)
            arrow.SetArrowSize(0.1)
    
            canvas.legend.apply('nominal', arrow)
    
            canvas.printWeb('efake/toys_' + binningName, dataType + '_' + conf + '_' + bin, logy = False)

outputFile.Close()
