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

# PRODUCT = 'frate'
PRODUCT = 'eff'
ADDFIT = True

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

if PRODUCT == 'frate':
    meas = ('ee', 'eg')
else:
    meas = ('pass', 'fail')

### Set up output

outputFile = ROOT.TFile.Open(outputDir + '/' + PRODUCT + '_' + dataType + '_' + binningName + '.root', 'recreate')

yields = dict((m, ROOT.TH1D(m, '', len(binning) - 1, array.array('d', binning))) for m in meas)
result = ROOT.TH1D(PRODUCT, '', len(binning) - 1, array.array('d', binning))
if dataType == 'mc':
    trueYields = dict((m, ROOT.TH1D(m + '_truth', '', len(binning) - 1, array.array('d', binning))) for m in meas)
    trueResult = ROOT.TH1D(PRODUCT + '_truth', '', len(binning) - 1, array.array('d', binning))

if binLabels:
    allhistograms = yields.values() + [result]
    if dataType == 'mc':
        allhistograms.extend(trueYields.values())
        allhistograms.append(trueResult)

    for h in allhistograms:
        for ibin in range(1, len(fitBins) + 1):
            h.GetXaxis().SetBinLabel(ibin, fitBins[ibin - 1][0])

### Compute

toydists = {}

staterrs = []
systerrs = []

for iBin, (bin, _) in enumerate(fitBins):
    stat2 = 0.

    toydists[bin] = {}

    sigshift = {}
    bkgshift = {}

    for conf in meas:
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
        sigshift[conf] = 0.
        bkgshift[conf] = 0.

        if uncSource:
            # compute uncertainties from distributions of nZ-normalized difference of toy yields

            toydist = uncSource.Get('pull_nominal_' + suffix)
            toydists[bin][conf] = toydist

            err2 += math.pow(toydist.GetRMS() * nZ, 2.)
            stat2 += math.pow(toydist.GetRMS(), 2.)

            altsig = uncSource.Get('pull_altsig_' + suffix)
            altbkg = uncSource.Get('pull_altbkg_' + suffix)

            if altsig:
                sigshift[conf] = altsig.GetMean()
            if altbkg:
                bkgshift[conf] = altbkg.GetMean()

        err2 += math.pow(max(abs(sigshift[conf]), abs(bkgshift[conf])) * nZ, 2.)

        yields[conf].SetBinError(iBin + 1, math.sqrt(err2))

        if dataType == 'mc':
            htarg = source.Get('target_' + suffix)
            hbkg = source.Get('mcbkg_' + suffix)
            hsig = htarg.Clone('hsig')
            hsig.Add(hbkg, -1.)

            compBinning = work.var('mass').getBinning('compWindow')

            ilow = htarg.FindFixBin(compBinning.lowBound())
            ihigh = htarg.FindFixBin(compBinning.highBound())
            if compBinning.highBound() == htarg.GetXaxis().GetBinLowEdge(ihigh):
                ihigh -= 1

            integral = 0.
            err2 = 0.
            while ilow <= ihigh:
                integral += hsig.GetBinContent(ilow)
                err2 += math.pow(htarg.GetBinError(ilow), 2.) # using htarg error
                ilow += 1

            trueYields[conf].SetBinContent(iBin + 1, integral)
            trueYields[conf].SetBinError(iBin + 1, math.sqrt(err2))


    ratio = yields[meas[1]].GetBinContent(iBin + 1) / yields[meas[0]].GetBinContent(iBin + 1)

    if PRODUCT == 'frate':
        central = ratio
    else:
        central = 1. / (1. + ratio)

    result.SetBinContent(iBin + 1, central)

    # re-evaluate shift uncertainties for ratios (cancels uncertainty if shape is correlated)
    sig = (1. + sigshift[meas[1]]) / (1. + sigshift[meas[0]])
    bkg = (1. + bkgshift[meas[1]]) / (1. + sigshift[meas[0]])
    syst2 = math.pow(max(abs(sig - 1.), abs(bkg - 1.)), 2.)

    result.SetBinError(iBin + 1, ratio * math.sqrt(stat2 + syst2))

    staterrs.append(ratio * math.sqrt(stat2))
    systerrs.append(ratio * math.sqrt(syst2))

    if dataType == 'mc':
        larger = trueYields[meas[0]].GetBinContent(iBin + 1) # ee or pass
        smaller = trueYields[meas[1]].GetBinContent(iBin + 1) # eg or fail
        elarger = trueYields[meas[0]].GetBinError(iBin + 1)
        esmaller = trueYields[meas[1]].GetBinError(iBin + 1)

        if PRODUCT == 'frate':
            central = smaller / larger
        else:
            central = larger / (smaller + larger)

        trueResult.SetBinContent(iBin + 1, central)
        trueResult.SetBinError(iBin + 1, central * math.sqrt(math.pow(elarger / larger, 2.) + math.pow(esmaller / smaller, 2.)))

outputFile.cd()
result.Write()
yields[meas[0]].Write()
yields[meas[1]].Write()
if dataType == 'mc':
    trueResult.Write()
    trueYields[meas[0]].Write()
    trueYields[meas[1]].Write()

### Visualize

lumi = sum(allsamples[s].lumi for s in lumiSamples)

result.SetMaximum(0.05)

canvas = SimpleCanvas(lumi = lumi, sim = (dataType == 'mc'))
canvas.SetGrid(False, True)
canvas.legend.setPosition(0.7, 0.8, 0.9, 0.9)
if PRODUCT == 'frate':
    canvas.legend.add(PRODUCT, 'R_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.ylimits = (0., 0.05)
else:
    canvas.legend.add(PRODUCT, '#epsilon_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.ylimits = (0., 1.05)

if dataType == 'mc':
    canvas.legend.add(PRODUCT + '_truth', 'MC truth', opt = 'LP', color = ROOT.kGreen, mstyle = 4)

canvas.legend.apply(PRODUCT, result)
canvas.addHistogram(result, drawOpt = 'EP')
if dataType == 'mc':
    canvas.legend.apply(PRODUCT + '_truth', trueResult)
    canvas.addHistogram(trueResult, drawOpt = 'EP')

if ADDFIT:
    # exclude bins 42 < pT < 48
    errors = {}
    ibin = result.FindFixBin(42.)
    while ibin <= result.FindFixBin(48.):
        errors[ibin] = result.GetBinError(ibin)
        result.SetBinError(ibin, 1.e+6)
        ibin += 1

    power = ROOT.TF1('power', '[0] + [1] / (x - [2])', result.GetXaxis().GetXmin(), result.GetXaxis().GetXmax())
    power.SetParameters(0.02, 1., 0.)
    result.Fit(power)
    canvas.addObject(power)

    for ibin, err in errors.items():
        result.SetBinError(ibin, err)

    text = 'f = %.4f + #frac{%.3f}{p_{T}' % (power.GetParameter(0), power.GetParameter(1))
    if power.GetParameter(2) >= 0.:
        text += ' - %.2f}' % power.GetParameter(2)
    else:
        text += ' + %.2f}' % (-power.GetParameter(2))

    canvas.addText(text, 0.3, 0.3, 0.5, 0.2)

canvas.xtitle = binningTitle
canvas.printWeb('efake', PRODUCT + '_' + dataType + '_' + binningName, logy = False)

for iBin, (bin, _) in enumerate(fitBins):
    if dataType == 'mc':
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2} (mc %.3f)' % (bin, result.GetBinContent(iBin + 1) * 100., staterrs[iBin] * 100., systerrs[iBin] * 100., trueResult.GetBinContent(iBin + 1) * 100.)
    else:
        print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2}' % (bin, result.GetBinContent(iBin + 1) * 100., staterrs[iBin] * 100., systerrs[iBin] * 100.)

if uncSource:
    for conf in meas:
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
