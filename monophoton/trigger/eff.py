# Trigger efficiency measurements
#   eff.py [measurement names (oname_mname ...)]

import os
import sys
import array

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetNdivisions(510, 'X')

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
import config
config.skimDir = '/mnt/hadoop/scratch/yiiyama/monophoton/skim'
config.localSkimDir = '/local/yiiyama/monophoton/skim'
import utils

from trigger.confs import measurements, confs, fitconfs

ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

REPLOT = False
FITEFFICIENCY = False

if len(sys.argv) > 1:
    omnames = [tuple(a.split('_')) for a in sys.argv[1:]]
else:
    omnames = measurements.keys()

outName = 'trigger'
outDir = config.histDir + '/trigger'

if not REPLOT:
    ## FILL DISTRIBUTIONS AND GRAPHS
    for oname, mname in omnames:
        print oname, mname

        snames, region, basesel = measurements[(oname, mname)]

        outputFile = ROOT.TFile.Open(outDir + '/trigger_efficiency_%s_%s.root' % (oname, mname), 'recreate')

        # fill the histograms
        plotter = ROOT.MultiDraw()
        plotter.setWeightBranch('')
    
        for sample in allsamples.getmany(snames):
            plotter.addInputPath(utils.getSkimPath(sample.name, region))
    
        plotter.setBaseSelection(basesel)
    
        # make an empty histogram for each (trigger, variable) combination
        histograms = []

        for tname, (passdef, commonsel, title, variables) in confs[oname].items():
            trigDir = outputFile.mkdir(tname)

            for vname, (vtitle, vexpr, denomdef, binning),  in variables.items():
                if type(binning) is tuple:
                    template = ROOT.TH1D('template', ';' + vtitle, *binning)
                else:
                    template = ROOT.TH1D('template', ';' + vtitle, len(binning) - 1, array.array('d', binning))
    
                trigDir.cd()
                hpass = template.Clone(vname + '_pass')
                hbase = template.Clone(vname + '_base')
                histograms.extend([hpass, hbase])
    
                sels = []
                if commonsel:
                    sels.append(commonsel)
                if denomdef:
                    sels.append(denomdef)
    
                plotter.addPlot(hbase, vexpr, ' && '.join(sels), True)

                sels.append(passdef)

                plotter.addPlot(hpass, vexpr, ' && '.join(sels), True)
    
                template.Delete()
    
        plotter.fillPlots()
    
        # make efficiency graphs and save
        for tname, (_, _, _, variables) in confs[oname].items():
            print ' ', tname
            for vname in variables:
                print '   ', vname

                hpass = outputFile.Get(tname + '/' + vname + '_pass')
                hbase = outputFile.Get(tname + '/' + vname + '_base')
                eff = ROOT.TGraphAsymmErrors(hpass, hbase)
                outputFile.GetDirectory(tname).cd()
                hpass.Write()
                hbase.Write()
                eff.Write(vname + '_eff')

        outputFile.Close()
    
## PLOT GRAPHS

work = ROOT.RooWorkspace('work', 'work')
xvar = work.factory('x[-6500.,6500.]')

if FITEFFICIENCY:
    ROOT.gSystem.Load('libRooFit.so')
    ROOT.gSystem.Load('/home/yiiyama/cms/studies/fittools/libFitTools.so')
    fitter = ROOT.EfficiencyFitter.singleton()

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)

for oname, mname in omnames:
    print oname, mname

    source = ROOT.TFile.Open(outDir + '/trigger_efficiency_%s_%s.root' % (oname, mname))

    snames, region, probeSel = measurements[(oname, mname)]

    canvas.lumi = sum(sample.lumi for sample in allsamples.getmany(snames))

    for tname, (_, _, title, variables) in confs[oname].items():
        print ' ', tname

        trigDir = source.GetDirectory(tname)

        for vname, (vtitle, _, _, binning) in variables.items():
            print '   ', vname

            eff = trigDir.Get(vname + '_eff')

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
            
            canvas.printWeb(outName, oname + '_' + mname + '_' + tname + '_' + vname, logy = False)

    source.Close()

# TO BE FIXED
#    func = None
#    marker = 0.
#    
#    if (vname, tname) in fitconfs[oname]:
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
