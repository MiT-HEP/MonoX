# Trigger efficiency measurement using X+photon events
#   eff.py object sname vname tname [output name]

import os
import sys
import array

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
import config
import utils

ROOT.gStyle.SetNdivisions(510, 'X')
ROOT.gSystem.Load('libPandaTreeObjects.so')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

REPLOT = False
FITEFFICIENCY = False

measurements = [
    ('photon', 'sel', 'sel-16c-m', 'tpeg', 'probes.medium && !probes.pixelVeto'),
    ('electron', 'sel', 'sel-16*-m', 'tp2e', 'probes.tight'),
    ('muon', 'smu', 'smu-16*', 'tp2m', 'probes.tight')
]

## SETUP

outName = 'trigger'
outFileName = basedir + '/data/trigger_efficiency.root'

vconfs = {}
tconfs = {}

vconfs['photon'] = {
    'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(10)]),
    'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
    'hOverE': ('H/E', 'probes.hOverE', 'probes.pt_ > 175.', (25, 0., 0.05)),
    'hcalE': ('E^{HCAL} (GeV)', 'probes.pt_ * TMath::CosH(probes.eta_) * probes.hOverE', 'probes.pt_ > 175.', (25, 0., 5)),
    'run': ('Run', 'runNumber', 'probes.pt_ > 175.', (26, 271050., 284050.))
}
vconfs['electron'] = {
    'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', (50, 0., 50.)),
    'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
    'hOverE': ('H/E', 'probes.hOverE', 'probes.pt_ > 200.', (25, 0., 0.05)),
    'hcalE': ('E^{HCAL} (GeV)', 'probes.pt_ * TMath::CosH(probes.eta_) * probes.hOverE', 'probes.pt_ > 200.', (25, 0., 5)),
    'run': ('Run', 'runNumber', 'probes.pt_ > 200.', (350, 271000., 274500.)),
    'leppt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)]),
}
vconfs['muon'] = {
    'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', (50, 0., 50.)),
    'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
    'run': ('Run', 'runNumber', 'probes.pt_ > 200.', (350, 271000., 274500.)),
    'leppt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)]),
}

ROOT.gROOT.ProcessLine('int val;')
def getEnum(cls, name):
    ROOT.gROOT.ProcessLine('val = panda::' + cls + '::TriggerObject::' + name + ';')
    return ROOT.val

tconfs['photon'] = {
    'l1eg40': ('probes.triggerMatch[][%d]' % getEnum('Photon', 'fSEG34IorSEG40'), '', 'L1 seed'),
    'sph165abs': ('probes.triggerMatch[][%d]' % getEnum('Photon', 'fPh165HE10'), '', 'L1&HLT')
}
tconfs['electron'] = {
    'el27': ('probes.triggerMatch[][%d]' % getEnum('Electron', 'fEl27Tight'), '', 'HLT'),
}
tconfs['muon'] = {
    'mu24ortrk24': ('probes.triggerMatch[][%d] || probes.triggerMatch[][%d]' % (getEnum('Muon', 'fIsoMu24'), getEnum('Muon', 'fIsoTkMu24')), '', 'HLT'),
}

# TTree output for fitting
vtconfs = {}
vtconfs['photon'] = []
vtconfs['electron'] = [
    ('ptzoom', 'el27')
]
vtconfs['muon'] = []


if not REPLOT:
    ## FILL DISTRIBUTIONS AND GRAPHS

    outputFile = ROOT.TFile.Open(outFileName, 'recreate')
    
    for oname, mname, snames, region, probeSel in measurements:
        print oname, mname

        measDir = outputFile.mkdir(oname + '_' + mname)
    
        baseSelection = 'tp.mass > 60. && tp.mass < 120. && ' + probeSel
    
        # fill the histograms
        plotter = ROOT.MultiDraw()
        plotter.setWeightBranch('')
    
        for sample in allsamples.getmany(snames):
            plotter.addInputPath(utils.getSkimPath(sample.name, region))
    
        plotter.setBaseSelection(baseSelection)
    
        # make empty histograms for all (variable, trigger) combination
        histograms = []
    
        for vname, (vtitle, vexpr, baseline, binning) in vconfs[oname].items():
            outDir = measDir.mkdir(vname)
    
            if type(binning) is tuple:
                template = ROOT.TH1D('template', ';' + vtitle, *binning)
            else:
                template = ROOT.TH1D('template', ';' + vtitle, len(binning) - 1, array.array('d', binning))
    
            for tname, (passdef, denomdef, title) in tconfs[oname].items():
                outDir.cd()
                hpass = template.Clone(tname + '_pass')
                hbase = template.Clone(tname + '_base')
                histograms.extend([hpass, hbase])
    
                sels = [passdef]
                if baseline:
                    sels.append(baseline)
                if denomdef:
                    sels.append(denomdef)
    
                plotter.addPlot(hpass, vexpr, ' && '.join(sels), True)
    
                sels = []
                if baseline:
                    sels.append(baseline)
                if denomdef:
                    sels.append(denomdef)
    
                plotter.addPlot(hbase, vexpr, ' && '.join(sels), True)
    
            template.Delete()
    
        plotter.fillPlots()
    
        # make efficiency graphs and save
        for vname in vconfs[oname]:
            print ' ', vname

            for tname in tconfs[oname]:
                print '   ', tname

                hpass = measDir.Get(vname + '/' + tname + '_pass')
                hbase = measDir.Get(vname + '/' + tname + '_base')
                eff = ROOT.TGraphAsymmErrors(hpass, hbase)
                measDir.GetDirectory(vname).cd()
                eff.Write(tname + '_eff')
    
        # save the distributions
        for hist in histograms:
            hist.GetDirectory().cd()
            hist.Write()

else:
    outputFile = ROOT.TFile.Open(outFileName)


## PLOT GRAPHS

work = ROOT.RooWorkspace('work', 'work')
xvar = work.factory('x[-6500.,6500.]')

if FITEFFICIENCY:
    ROOT.gSystem.Load('libRooFit.so')
    ROOT.gSystem.Load('/home/yiiyama/cms/studies/fittools/libFitTools.so')
    fitter = ROOT.EfficiencyFitter.singleton()

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)

for oname, mname, snames, region, probeSel in measurements:
    print oname, mname

    measDir = outputFile.GetDirectory(oname + '_' + mname)

    canvas.lumi = sum(sample.lumi for sample in allsamples.getmany(snames))

    for vname, (vtitle, vexpr, baseline, binning) in vconfs[oname].items():
        print ' ', vname

        outDir = measDir.GetDirectory(vname)

        for tname, (passdef, denomdef, title) in tconfs[oname].items():
            print '   ', tname

            eff = outDir.Get(tname + '_eff')

            canvas.Clear()
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
            
            canvas.printWeb(outName, oname + '_' + mname + '_' + vname + '_' + tname, logy = False)

# TO BE FIXED
#    func = None
#    marker = 0.
#    
#    if (vname, tname) in vtconfs[oname]:
#        func = work.factory('FormulaVar::func("(@0 < @1) * @2 * (1. + TMath::Erf((@3 - @2) * @4 / @2 * (@0 - @1))) + (@0 > @1) * (@2 + (@3 - @2) * TMath::Erf(@4 * (@0 - @1)))", {x, turn[170.,0.,300.], norm1[0.5,0.,1.], norm[0.9,0.,1.], rise2[0.1,0.,1.]})')
#        params = ROOT.RooArgList(work.arg('turn'), work.arg('norm1'), work.arg('norm'), work.arg('rise2'))
#        fitmin = 150.
#        fitmax = 250.
#    
#        marker = 175.
#    
#        reduced = tree.CopyTree('({baseline}) && ({denomdef})'.format(baseline = baseline, denomdef = denomdef))
#    
#        xvar.setRange(fitmin, fitmax)
#        
#        fitter.setXRange(fitmin, fitmax)
#        fitter.setTarget(reduced, passdef, vexpr)
#        fitter.setLikelihood(func, params, xvar)
#    
#        fitter.fit()
#    
#        tf1 = func.asTF(ROOT.RooArgList(xvar))
#        tf1.SetNpx(1000)
#    
#        canvas.Clear()
#        canvas.legend.add('fit', title = 'Fit', opt = 'L', color = ROOT.kRed, lwidth = 2)
#        canvas.legend.apply('fit', tf1)
#    
#        canvas.SetGrid()
#    
#        canvas.addHistogram(eff, drawOpt = 'EP')
#        canvas.addHistogram(tf1, drawOpt = '')
#        
#        if type(binning) is tuple:
#            canvas.addLine(binning[1], 1., binning[2], 1.)
#            eff.GetXaxis().SetLimits(binning[1], binning[2])
#            tf1.SetRange(binning[1], binning[2])
#        else:
#            canvas.addLine(binning[0], 1., binning[-1], 1.)
#            eff.GetXaxis().SetLimits(binning[0], binning[-1])
#            tf1.SetRange(binning[0], binning[-1])
#        
#        canvas.xtitle = vtitle
#        canvas.ylimits = (0., 1.2)
#    
#        if marker > 0.:
#            canvas.addLine(marker, 0., marker, 1.2, color = ROOT.kRed)
#        
#        canvas.printWeb('trigger', vname + '_' + tname + '_' + sname + '_fit', logy = False)
