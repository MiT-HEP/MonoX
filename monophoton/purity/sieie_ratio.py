import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

if basedir not in sys.path:
    sys.path.append(basedir)

import config
from datasets import allsamples
from plotstyle import DataMCCanvas
import purity.selections as sel

outputFile = ROOT.TFile.Open('../data/sieie_ratio.root', 'recreate')

hmc = ROOT.TH1D('hmc', '', 44, 0.004, 0.015)
hdata = ROOT.TH1D('hdata', '', 44, 0.004, 0.015)

#selection = 'tp.mass > 80 && tp.mass < 100 && tp.mass + tp.mass2 < 185 && probes.hOverE < 0.0396 && probes.chIso < 0.441 && probes.nhIso < 2.725 && probes.phIso < 2.571'
#selection = 'tp.mass > 80 && tp.mass < 100 && probes.hOverE < 0.0396 && probes.chIso < 0.441 && probes.nhIso < 2.725 && probes.phIso < 2.571'
selection = 'Sum$(jets.pt_) > 220 && tp.mass > 80 && tp.mass < 100 && probes.hOverE < {hOverE} && probes.chIso < {chIso} && probes.nhIso < {nhIso} && probes.phIso < {phIso}'.format(**sel.AshimCuts)
# cut on HT to align data & MC phase space

# this is stupid - update once we have a proper weight branch in tpeg
for sname in ['dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600']:
    sample = allsamples[sname]

    source = ROOT.TFile(config.skimDir + '/' + sname + '_tpeg.root')
    tree = source.Get('events')
    outputFile.cd()
    tree.Draw('probes.sieie>>+hmc', '%f * (%s)' % (sample.crosssection / sample.sumw, selection), 'goff')

data = ROOT.TChain('events')
data.Add('/mnt/hadoop/scratch/yiiyama/monophoton/skim/sph-16*-m_tpeg.root')

outputFile.cd()
data.Draw('probes.sieie>>hdata', selection, 'goff')

hmc.Scale(hdata.GetSumOfWeights() / hmc.GetSumOfWeights())

ratio = hdata.Clone('ratio')
ratio.Divide(hmc)

line = ROOT.TF1('line', '[0] + [1] * x', 0.0085, 0.0105)
line.SetParameters(1.5, -100.)
ratio.Fit(line)

outputFile.cd()
hmc.Write()
hdata.Write()
ratio.Write()
line.Write('fit')

# visualize

canvas = DataMCCanvas(lumi = sum(s.lumi for s in allsamples.getmany('sph-16*-m')))
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

canvas.addStacked(hmc, title = 'MC', color = ROOT.kBlue, style = 3003)
canvas.addObs(hdata, title = 'Data')

canvas.printWeb('purity', 'sieie_ratio', logy = False)
