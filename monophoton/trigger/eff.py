# Trigger efficiency measurement using X+photon events

import os
import sys
import array

import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas

sourceDir = '/scratch5/yiiyama/studies/monophoton16'

vconf = [
    ('pt', 'p_{T}^{#gamma} (GeV)', 'probes.pt[]', '1', array.array('d', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(6)])),
    ('hOverE', 'H/E', 'probes.hOverE[]', 'probes.pt[] > 100', array.array('d', [0. + 0.002 * x for x in range(25)])),
    ('hcalE', 'E^{HCAL} (GeV)', 'probes.pt[] * TMath::CosH(probes.eta[]) * probes.hOverE[]', 'probes.pt[] > 100', array.array('d', [0. + 0.2 * x for x in range(25)]))
]

lumi = 1700.

canvas = SimpleCanvas(lumi = lumi)
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)
canvas.legend.add('eff', title = '', opt = 'LP', color = ROOT.kBlack, mstyle = 8)

# matchL1[2] -> SEG34IorSEG40IorSJet200
# matchHLT[2] -> Ph165HE10

for eventType in ['diphoton', 'dielectron', 'muonphoton']:
    for vname, vtitle, vexpr, baseline, binning in vconf:
        for name, passdef, denomdef, title in [
            ('hlt', 'probes.matchHLT[][2]', 'probes.matchL1[][2] > 0. && probes.matchL1[][2] < 0.3', 'HLT/L1'),
            ('l1', 'probes.matchL1[][2] > 0. && probes.matchL1[][2] < 0.3', '1', 'L1 seed'),
            ('l1eg', 'probes.matchL1[][5] > 0. && probes.matchL1[][5] < 0.3', '1', 'L1 seed'),
        ]:
            canvas.Clear()
    
            source = ROOT.TFile.Open(sourceDir + '/trigger_' + eventType + '.root')
            tree = source.Get('triggerTree')
    
            passing = ROOT.TH1D('passing', ';' + vtitle, len(binning) - 1, binning)
            denom = ROOT.TH1D('denom', ';' + vtitle, len(binning) - 1, binning)
    
            tree.Draw(vexpr + '>>denom', '(%s) && (%s)' % (baseline, denomdef))
            tree.Draw(vexpr + '>>passing', '(%s) && (%s) && (%s)' % (baseline, denomdef, passdef))
            
            print passing.GetEntries(), denom.GetEntries()
            
            eff = ROOT.TGraphAsymmErrors(passing, denom)
            
            canvas.SetGrid()
            
            canvas.legend.entries['eff'].SetLabel(title)
            canvas.legend.apply('eff', eff)
            
            canvas.addHistogram(eff, drawOpt = 'EP')
            canvas.addLine(0., 1., 300., 1.)
            eff.GetXaxis().SetLimits(0., 300.)
            
            canvas.xtitle = vtitle
            canvas.ylimits = (0., 1.2)
            
            canvas.printWeb('trigger', vname + '_' + name + '_' + eventType, logy = False)
