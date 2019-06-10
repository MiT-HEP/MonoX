# Trigger efficiency measurements
#   eff.py [measurement names (oname_mname ...)]

import os
import sys
import array
import importlib

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

from datasets import allsamples
import plotstyle
import config
import utils

tconf = importlib.import_module('configs.' + config.config + '.trigger')
measurements = tconf.measurements
confs = tconf.confs
fitconfs = tconf.fitconfs

ROOT.gStyle.SetNdivisions(510, 'X')
ROOT.gSystem.Load(config.libmultidraw)

REPLOT = False
FITEFFICIENCY = False

if len(sys.argv) > 1:
    omnames = [tuple(a.split('_')) for a in sys.argv[1:]]
else:
    omnames = measurements.keys()

outName = config.plotDir + '/trigger'
outDir = config.histDir + '/trigger'

if not REPLOT:
    ## FILL DISTRIBUTIONS AND GRAPHS
    for omname in omnames:
        oname = omname[0]
        mname = omname[1]
        print oname, mname

        snames, region, basesel, colname = measurements[(oname, mname)]

        try:
            os.makedirs(outDir)
        except OSError:
            pass

        outputFile = ROOT.TFile.Open(outDir + '/trigger_efficiency_%s_%s.root' % (oname, mname), 'recreate')

        # fill the histograms
        plotter = ROOT.multidraw.MultiDraw()
        plotter.setWeightBranch('')
        #plotter.setInputMultiplexing(4)
    
        for sample in allsamples.getmany(snames):
            plotter.addInputPath(utils.getSkimPath(sample.name, region))
    
        plotter.setFilter(basesel)
    
        # make an empty histogram for each (trigger, variable) combination
        histograms = []
        cuts = {'': ''}

        for tname, (passdef, commonsel, title, variables) in confs[oname].items():
            if len(omname) > 2 and tname != omname[2]:
                continue

            trigDir = outputFile.mkdir(tname)

            passdef = passdef.format(col = colname)
            commonsel = commonsel.format(col = colname)

            for vname, (vtitle, vexpr, denomdef, binning) in variables.items():
                denomdef = denomdef.format(col = colname)

                trigDir.cd()
                if type(vexpr) is str:
                    vexpr = vexpr.format(col = colname)
                    title = ';' + vtitle
                    
                    cls = ROOT.TH1D
                    if type(binning) is tuple:
                        args = binning
                    else:
                        args = (len(binning) - 1, array.array('d', binning))
                else:
                    xvexpr = vexpr[0].format(col = colname)
                    yvexpr = vexpr[1].format(col = colname)
                    title = ';'.join(('',) + vtitle)
                    
                    cls = ROOT.TH2D
                    args = tuple()
                    for bng in binning:
                        if type(bng) is tuple:
                            args += bng
                        else:
                            args += (len(bng) - 1, array.array('d', bng))

                hpass = cls(vname + '_pass', ';' + title, *args)
                hbase = cls(vname + '_base', ';' + title, *args)
    
                histograms.extend([hpass, hbase])
    
                # need basesel here because MultiDraw filter applies only at the event level
                # whereas we need to filter individual collection elements
                sels = [basesel]
                if commonsel:
                    sels.append(commonsel)
                if denomdef:
                    sels.append(denomdef)

                cut = ' && '.join(sels)
                try:
                    cutName = cuts[cut]
                except:
                    cutName = tname + '_' + vname
                    cuts[cut] = cutName
                    plotter.addCut(cutName, ' && '.join(sels))

                if hbase.GetDimension() == 1:
                    plotter.addPlot(hbase, vexpr, cutName)
                else:
                    plotter.addPlot2D(hbase, xvexpr, yvexpr, cutName)

                sels.append(passdef)

                cut = ' && '.join(sels)
                try:
                    cutName = cuts[cut]
                except:
                    cutName = tname + '_' + vname + '_pass'
                    cuts[cut] = cutName
                    plotter.addCut(cutName, ' && '.join(sels))

                if hpass.GetDimension() == 1:
                    plotter.addPlot(hpass, vexpr, cutName)
                else:
                    plotter.addPlot2D(hpass, xvexpr, yvexpr, cutName)
    
        plotter.execute()
    
        # make efficiency graphs and save
        for tname, (_, _, _, variables) in confs[oname].items():
            if len(omname) > 2 and tname != omname[2]:
                continue

            tdir = outputFile.GetDirectory(tname)

            print ' ', tname
            for vname, (_, vexpr, _, _) in variables.items():
                print '   ', vname

                tdir.cd()
                hpass = tdir.Get(vname + '_pass')
                hbase = tdir.Get(vname + '_base')
                hpass.Write()
                hbase.Write()
                
                if type(vexpr) is str:
                    eff = ROOT.TGraphAsymmErrors(hpass, hbase)
                    eff.Write(vname + '_eff')
                else:
                    eff = hpass.Clone(vname + '_eff')
                    eff.Divide(hbase)
                    eff.Write()

        outputFile.Close()
    
## PLOT GRAPHS

work = ROOT.RooWorkspace('work', 'work')
xvar = work.factory('x[-6500.,6500.]')

if FITEFFICIENCY:
    ROOT.gSystem.Load('libRooFit.so')
    ROOT.gSystem.Load('/home/yiiyama/cms/studies/fittools/libFitTools.so')
    fitter = ROOT.EfficiencyFitter.singleton()

canvas = plotstyle.SimpleCanvas()
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)
canvas2d = plotstyle.TwoDimCanvas()

for omname in omnames:
    oname = omname[0]
    mname = omname[1]
    print oname, mname

    source = ROOT.TFile.Open(outDir + '/trigger_efficiency_%s_%s.root' % (oname, mname))

    snames, region, probeSel, colname = measurements[(oname, mname)]

    canvas.lumi = sum(sample.lumi for sample in allsamples.getmany(snames))

    for tname, (_, _, title, variables) in confs[oname].items():
        if len(omname) > 2 and tname != omname[2]:
            continue

        print ' ', tname

        trigDir = source.GetDirectory(tname)

        for vname, (vtitle, vexpr, _, binning) in variables.items():
            print '   ', vname

            eff = trigDir.Get(vname + '_eff')

            if type(vexpr) is str:
                canvas.Clear()
                canvas.SetGrid()

                canvas.legend.Clear()
                if title:
                    canvas.legend.add('eff', title = title, opt = 'LP', color = ROOT.kBlack, mstyle = 8)
                    canvas.legend.apply('eff', eff)
                else:
                    eff.SetMarkerColor(ROOT.kBlack)
                    eff.SetMarkerStyle(8)

                canvas.addHistogram(eff, drawOpt = 'EP', clone = False)
                
                canvas.xtitle = vtitle
                canvas.ylimits = (0., 1.1)
                
                canvas.Update()
                
                if type(binning) is tuple:
                    eff.GetXaxis().SetLimits(binning[1], binning[2])
                    eff.GetXaxis().SetRangeUser(binning[1], binning[2])
                else:
                    eff.GetXaxis().SetLimits(binning[0], binning[-1])
                    eff.GetXaxis().SetRangeUser(binning[0], binning[-1])
                
                eff.GetYaxis().SetRangeUser(0., 1.2)
    
                canvas.printWeb(outName + '/' + oname + '_' + mname, tname + '_' + vname, logy = False)

            else:
                canvas2d.Clear()

                canvas2d.addHistogram(eff, drawOpt = 'COLZ', clone = False)
                
                canvas.xtitle = vtitle[0]
                canvas.ytitle = vtitle[1]
                canvas.zlimits = (0., 1.)
                
                canvas2d.Update()
                
                eff.GetZaxis().SetRangeUser(0., 1.)
    
                canvas2d.printWeb(outName + '/' + oname + '_' + mname, tname + '_' + vname, logy = False, logz = False)

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
