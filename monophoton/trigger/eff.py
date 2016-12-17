# Trigger efficiency measurement using X+photon events
#   eff.py object sname vname tname [output name]
# can use wildcard for any of the three

import os
import sys
import array

import ROOT
ROOT.gROOT.SetBatch(True)

# ROOT.gSystem.Load('libRooFit.so')
# ROOT.gSystem.Load('/home/yiiyama/cms/studies/fittools/libFitTools.so')

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
import config

oname = sys.argv[1]
sname = sys.argv[2]
vname = sys.argv[3]
tname = sys.argv[4]
try:
    outname = sys.argv[5]
except IndexError:
    outname = ''

ROOT.gStyle.SetNdivisions(510, 'X')

samplesConf = {
    'sph': ['sph-*'],
    'sel': ['sel-16c-r'],
    'smu': ['smu-*']
}

snames = samplesConf[sname]

## SETUP

workDir = config.histDir + '/trigger'

if outname:
    outputFile = ROOT.TFile.Open(outname, 'recreate')

if oname == 'photon':
    vconf = {
        'pt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(10)])),
        'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)])),
        'hOverE': ('H/E', 'probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 0.05)),
        'hcalE': ('E^{HCAL} (GeV)', 'probe.pt[0] * TMath::CosH(probe.eta[0]) * probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 5)),
        'run': ('Run', 'run', 'probe.pt[0] > 200.', (350, 271000., 274500.)),
        'leppt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)])),
    }

    tconf = {
        'hlt': ('probe.matchHLT[0][2]', 'probe.matchL1[0][2] > 0. && probe.matchL1[0][2] < 0.3', 'HLT/L1'),
        'l1': ('probe.matchL1[0][2] > 0. && probe.matchL1[0][2] < 0.3', '1', 'L1 seed'),
        'l1eg': ('probe.matchL1[0][5] > 0. && probe.matchL1[0][5] < 0.3', '1', 'L1 seed'),
        'l1hlt': ('probe.matchL1[0][2] > 0. && probe.matchL1[0][2] < 0.3 && probe.matchHLT[0][2]', '1', 'L1&HLT'),
        'lephlt': ('probe.matchHLT[0][0]', '1', 'HLT')
    }

elif oname == 'muon':
    vconf = {
        'pt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', (50, 0., 50.)),
        'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)])),
        'hOverE': ('H/E', 'probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 0.05)),
        'hcalE': ('E^{HCAL} (GeV)', 'probe.pt[0] * TMath::CosH(probe.eta[0]) * probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 5)),
        'run': ('Run', 'run', 'probe.pt[0] > 200.', (350, 271000., 274500.)),
        'leppt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)])),
    }

    tconf = {
        'hlt': ('probe.matchHLT[0][0] || probe.matchHLT[0][1]', '1', ''),
    }

elif oname == 'electron':
    vconf = {
        'pt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', (50, 0., 50.)),
        'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)])),
        'hOverE': ('H/E', 'probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 0.05)),
        'hcalE': ('E^{HCAL} (GeV)', 'probe.pt[0] * TMath::CosH(probe.eta[0]) * probe.hOverE[0]', 'probe.pt[0] > 200.', (25, 0., 5)),
        'run': ('Run', 'run', 'probe.pt[0] > 200.', (350, 271000., 274500.)),
        'leppt': ('p_{T}^{#gamma} (GeV)', 'probe.pt[0]', '1', array.array('d', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)])),
    }

    tconf = {
        'hlt': ('probe.matchHLT[0][1]', '1', ''),
    }

vtitle, vexpr, baseline, binning = vconf[vname]

passdef, denomdef, title = tconf[tname]

if sname == 'jht' and vname == 'pt' and (tname == 'l1' or tname == 'l1hlt'):
    binning = array.array('d', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(14)])

## SOURCE

tree = ROOT.TChain('triggerTree')
lumi = 0.
for sample in allsamples.getmany(snames):
    lumi += sample.lumi
    print 'adding', workDir + '/trigger_' + sample.name + '_' + oname + '.root'
    tree.Add(workDir + '/trigger_' + sample.name + '_' + oname + '.root')

canvas = SimpleCanvas(lumi = lumi)
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)

# matchL1[2] -> SEG34IorSEG40IorSJet200
# matchHLT[2] -> Ph165HE10

work = ROOT.RooWorkspace('work', 'work')
xvar = work.factory('x[-6500.,6500.]')

# fitter = ROOT.EfficiencyFitter.singleton()
tmpfile = ROOT.TFile.Open('/tmp/trigeff_tmp.root', 'recreate')

canvas.Clear()

if type(binning) is tuple:
    passing = ROOT.TH1D('passing', ';' + vtitle, *binning)
    denom = ROOT.TH1D('denom', ';' + vtitle, *binning)
else:
    passing = ROOT.TH1D('passing', ';' + vtitle, len(binning) - 1, binning)
    denom = ROOT.TH1D('denom', ';' + vtitle, len(binning) - 1, binning)

tree.Draw(vexpr + '>>denom', '(%s) && (%s)' % (baseline, denomdef))
tree.Draw(vexpr + '>>passing', '(%s) && (%s) && (%s)' % (baseline, denomdef, passdef))

print passing.GetEntries(), denom.GetEntries()

eff = ROOT.TGraphAsymmErrors(passing, denom)

if outname:
    outputFile.cd()
    eff.Write(vname + '_' + tname + '_' + sname)

canvas.SetGrid()

canvas.legend.Clear()
if title:
    canvas.legend.add('eff', title = title, opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.legend.apply('eff', eff)
else:
    eff.SetMarkerColor(ROOT.kBlack)
    eff.SetMarkerStyle(8)

canvas.addHistogram(eff, drawOpt = 'EP')

canvas.xtitle = vtitle
canvas.ylimits = (0., 1.2)

canvas.Update()

if type(binning) is tuple:
    canvas.addLine(binning[0], 1., binning[2], 1.)
    eff.GetXaxis().SetLimits(binning[1], binning[2])
else:
    canvas.addLine(binning[0], 1., binning[-1], 1.)
    eff.GetXaxis().SetLimits(binning[0], binning[-1])

eff.GetYaxis().SetRangeUser(0., 1.2)

canvas.printWeb('trigger', vname + '_' + tname + '_' + sname + '_' + oname, logy = False)

func = None
marker = None

if vname == 'pt' and (tname == 'l1' or tname == 'l1hlt') and sname == 'jht':
    func = work.factory('PolyVar::func(x, {intercept[1.04,0.,2.], slope[-0.001,-0.01,0.]})')
    params = ROOT.RooArgList(work.arg('intercept'), work.arg('slope'))
    fitmin = 300.
    fitmax = 1000.
    
elif vname == 'ptzoom' and tname == 'hlt' and sname == 'sel':
    func = work.factory('FormulaVar::func("(@0 < @1) * @2 * (1. + TMath::Erf((@3 - @2) * @4 / @2 * (@0 - @1))) + (@0 > @1) * (@2 + (@3 - @2) * TMath::Erf(@4 * (@0 - @1)))", {x, turn[170.,0.,300.], norm1[0.5,0.,1.], norm[0.9,0.,1.], rise2[0.1,0.,1.]})')
    params = ROOT.RooArgList(work.arg('turn'), work.arg('norm1'), work.arg('norm'), work.arg('rise2'))
    fitmin = 150.
    fitmax = 250.

    marker = 175.

if func:
    tmpfile.cd()
    reduced = tree.CopyTree('({baseline}) && ({denomdef})'.format(baseline = baseline, denomdef = denomdef))

    xvar.setRange(fitmin, fitmax)
    
    fitter.setXRange(fitmin, fitmax)
    fitter.setTarget(reduced, passdef, vexpr)
    fitter.setLikelihood(func, params, xvar)

    fitter.fit()

    tf1 = func.asTF(ROOT.RooArgList(xvar))
    tf1.SetNpx(1000)

    canvas.Clear()
    canvas.legend.add('fit', title = 'Fit', opt = 'L', color = ROOT.kRed, lwidth = 2)
    canvas.legend.apply('fit', tf1)

    canvas.SetGrid()

    canvas.addHistogram(eff, drawOpt = 'EP')
    canvas.addHistogram(tf1, drawOpt = '')
    
    if type(binning) is tuple:
        canvas.addLine(binning[1], 1., binning[2], 1.)
        eff.GetXaxis().SetLimits(binning[1], binning[2])
        tf1.SetRange(binning[1], binning[2])
    else:
        canvas.addLine(binning[0], 1., binning[-1], 1.)
        eff.GetXaxis().SetLimits(binning[0], binning[-1])
        tf1.SetRange(binning[0], binning[-1])
    
    canvas.xtitle = vtitle
    canvas.ylimits = (0., 1.2)

    if marker is not None:
        canvas.addLine(marker, 0., marker, 1.2, color = ROOT.kRed)
    
    canvas.printWeb('trigger', vname + '_' + tname + '_' + sname + '_fit', logy = False)
