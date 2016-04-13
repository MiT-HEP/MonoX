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
from tp.efake_conf import binningName, fitBins, binning

dataType = sys.argv[1]

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

source = ROOT.TFile.Open('/scratch5/yiiyama/studies/egfake/fityields_' + dataType + '.root')

vTPconf = array.array('i', [0])
vBinName = array.array('c', '\0' * 128)
vNz = array.array('d', [0.])
vToyNumber = array.array('i', [0])

sourceYields = source.Get('yields')
sourceYields.SetBranchAddress('tpconf', vTPconf)
sourceYields.SetBranchAddress('binName', vBinName)
sourceYields.SetBranchAddress('nz', vNz)
sourceYields.SetBranchAddress('toyNumber', vToyNumber)

# 0 -> ee, 1 -> eg
nominal = {'ee': {}, 'eg': {}}
toys = {'ee': collections.defaultdict(list), 'eg': collections.defaultdict(list)}

iEntry = 0
while sourceYields.GetEntry(iEntry) > 0:
    iEntry += 1

    conf = 'ee' if vTPconf[0] == 0 else 'eg'

    for binName, cut in fitBins:
        if vBinName.tostring().startswith(binName):
            break
    else:
        raise RuntimeError('Unknown bin ' + vBinName.tostring())

    if vToyNumber[0] == -1:
        nominal[conf][binName] = vNz[0]
    else:
        toys[conf][binName].append(vNz[0])

source.Close()

outputFile = ROOT.TFile.Open('/scratch5/yiiyama/studies/egfake/results_' + dataType + '.root', 'update')

binning[-1] = 150.

yields = {
    'ee': ROOT.TH1D(binningName + '_ee', '', len(binning) - 1, array.array('d', binning)),
    'eg': ROOT.TH1D(binningName + '_eg', '', len(binning) - 1, array.array('d', binning))
}

frate = ROOT.TH1D(binningName + '_frate', '', len(binning) - 1, array.array('d', binning))

for iBin, (binName, cut) in enumerate(fitBins):
    err2 = 0.

    for conf in ['ee', 'eg']:
        nom = nominal[conf][binName]
        tvals = toys[conf][binName]

        tvals.sort()
        quant = 0
        while quant != len(tvals):
            if tvals[quant] > nom:
                break
    
            quant += 1
    
        errLow = nom - tvals[int(0.32 * quant)]
        errHigh = tvals[int((len(tvals) - quant) * 0.32) + quant] - nom

        yields[conf].SetBinContent(iBin + 1, nom)
        yields[conf].SetBinError(iBin + 1, (errLow + errHigh) * 0.5)

        err2 += math.pow((errLow + errHigh) * 0.5 / nom, 2.)

    ratio = yields['eg'].GetBinContent(iBin + 1) / yields['ee'].GetBinContent(iBin + 1)
    frate.SetBinContent(iBin + 1, ratio)
    frate.SetBinError(iBin + 1, ratio * math.sqrt(err2))

outputFile.cd()
frate.Write()
yields['ee'].Write()
yields['eg'].Write()

canvas = SimpleCanvas(lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi, sim = (dataType == 'mc'))
canvas.legend.add('frate', 'R_{e}', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
canvas.legend.apply('frate', frate)
canvas.ylimits = (0., 0.03)
canvas.addHistogram(frate, drawOpt = 'EP')
canvas.printWeb('efake', 'frate_' + dataType, logy = False)

outputFile.Close()
