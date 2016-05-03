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
from tp.efake_conf import outputDir, getBinning

dataType = sys.argv[1]
binningName = sys.argv[2]

binningTitle, binning, fitBins = getBinning(binningName)

sys.argv = []

toyUncert = True

import ROOT
ROOT.gROOT.SetBatch(True)

inputTree = ROOT.TChain('yields')
inputTree.Add(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')
inputTree.Add(outputDir + '/toys_' + dataType + '_' + binningName + '.root')

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

for altname in ['altbkg', 'altsig']:
    if os.path.exists(outputDir + '/fityields_' + dataType + '_' + binningName + '_' + altname + '.root'):
        print 'Alternative fit ' + altname + ' found'

        sysshift[altname] = {'ee': {}, 'eg': {}}

        source = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '_' + binningName + '_' + altname + '.root')
        inputTree = source.Get('yields')
        inputTree.SetBranchAddress('tpconf', vTPconf)
        inputTree.SetBranchAddress('binName', vBinName)
        inputTree.SetBranchAddress('nz', vNz)
        inputTree.SetBranchAddress('toyNumber', vToyNumber)

        iEntry = 0
        while inputTree.GetEntry(iEntry) > 0:
            iEntry += 1
        
            conf = 'ee' if vTPconf[0] == 0 else 'eg'

            for binName, cut in fitBins:
                if vBinName.tostring().startswith(binName):
                    break
            else:
                continue
        
            sysshift[altname][conf][binName] = vNz[0]

outputFile = ROOT.TFile.Open(outputDir + '/results_' + dataType + '_' + binningName + '.root', 'recreate')

if binningName == 'pt':
    binning[-1] = 150.

yields = {
    'ee': ROOT.TH1D('ee', '', len(binning) - 1, array.array('d', binning)),
    'eg': ROOT.TH1D('eg', '', len(binning) - 1, array.array('d', binning))
}

frate = ROOT.TH1D('frate', '', len(binning) - 1, array.array('d', binning))

toydists = {}

contents = []
staterrs = []
systerrs = []

for iBin, (binName, cut) in enumerate(fitBins):
    stat2 = 0.
    syst2 = 0.

    toydists[binName] = {}

    for conf in ['ee', 'eg']:
        nom = nominal[conf][binName]

        yields[conf].SetBinContent(iBin + 1, nom)

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
            yields[conf].SetBinError(iBin + 1, (errLow + errHigh) * 0.5)

            stat2 += math.pow((errLow + errHigh) * 0.5 / nom, 2.)

        try:
            sys = sysshift['altsig'][conf][binName] - nom
            syst2 += math.pow(sys / nom, 2.)
        except KeyError:
            pass

        try:
            sys = sysshift['altbkg'][conf][binName] - nom
            syst2 += math.pow(sys / nom, 2.)
        except KeyError:
            pass

    ratio = yields['eg'].GetBinContent(iBin + 1) / yields['ee'].GetBinContent(iBin + 1)
    frate.SetBinContent(iBin + 1, ratio)
    frate.SetBinError(iBin + 1, ratio * math.sqrt(stat2 + syst2))

    contents.append(ratio)
    staterrs.append(ratio * math.sqrt(stat2))
    systerrs.append(ratio * math.sqrt(syst2))

outputFile.cd()
frate.Write()
yields['ee'].Write()
yields['eg'].Write()

canvas = SimpleCanvas(lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi, sim = (dataType == 'mc'))
canvas.legend.setPosition(0.7, 0.8, 0.9, 0.9)
canvas.legend.add('frate', 'R_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
canvas.legend.apply('frate', frate)
canvas.ylimits = (0., 0.03)
canvas.addHistogram(frate, drawOpt = 'EP')

canvas.xtitle = binningTitle
canvas.printWeb('efake', 'frate_' + dataType + '_' + binningName, logy = False)

for iBin, (binName, cut) in enumerate(fitBins):
    print '%15s [%.3f +- %.3f (stat.) +- %.3f (syst.)] x 10^{-2}' % (binName, contents[iBin] * 100., staterrs[iBin] * 100., systerrs[iBin] * 100.)

if binningName == 'pt':
    binName = 'pt_100_6500'
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
        arrow = canvas.addLine(nominal[conf][binName], toydist.GetMaximum() * 0.2, nominal[conf][binName], 0., width = 2, cls = ROOT.TArrow)

        canvas.legend.apply('nominal', arrow)

        canvas.printWeb('efake', 'toys_' + dataType + '_' + conf + '_' + binName, logy = False)

outputFile.Close()
