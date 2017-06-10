#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
import os
import math
import re

def fillPlots(plotConfig, group, plotdefs, sourceDir, outFile, lumi = 0., postscale = 1., printLevel = 0, altSourceDir = ''):
    if group.region:
        region = group.region
    else:
        region = plotConfig.name

    # run the Plotter for each sample
    for sample in group.samples:
        dname = sample.name + '_' + region

        print '   ', dname

        sourceName = sourceDir + '/' + dname + '.root'
        
        if altSourceDir:
            altName = altSourceDir + '/' + dname + '.root'
            if not os.path.exists(altName) and os.stat(altName).st_mtime > os.stat(sourceName).st_mtime:
                sourceName = altName

        elif not os.path.exists(sourceName):
            raise RuntimeError('Cannot open file ' + sourceName)
    
        histograms = []
   
        plotter = ROOT.MultiDraw(sourceName)
        plotter.setPrintLevel(printLevel)

        cuts = []
        if plotConfig.baseline.strip():
            cuts.append('(' + plotConfig.baseline.strip() + ')')
        if group.cut.strip():
            cuts.append('(' + group.cut + ')')

        baseSel = ' && '.join(cuts)

        if printLevel > 0:
            print '      Baseline selection:', baseSel
            print '      Full selection:', plotConfig.fullSelection.strip()

        plotter.setBaseSelection(baseSel)
        plotter.setFullSelection(plotConfig.fullSelection.strip())

        if not sample.data:
            plotter.setLuminosity(lumi)

        if group == plotConfig.obs:
            plotter.setPrescale(plotConfig.prescales[sample])
    
        for plotdef in plotdefs:
            if not outFile.GetDirectory(plotdef.name):
                outFile.mkdir(plotdef.name)

            outDir = outFile.GetDirectory(plotdef.name + '/samples')
            if not outDir:
                outDir = outFile.GetDirectory(plotdef.name).mkdir('samples')

            hist = plotdef.makeHist(dname, outDir = outDir)
            histograms.append(hist)

            # nominal distribution
            plotter.addPlot(
                hist,
                plotdef.formExpression(),
                plotdef.cut.strip(),
                plotdef.applyBaseline,
                plotdef.applyFullSel
            )
    
            # systematic variations
            for variation in group.variations:
                for iv, direction in [(0, 'Up'), (1, 'Down')]:
                    hist = plotdef.makeHist(dname + '_' + variation.name + direction, outDir = outDir)
                    histograms.append(hist)
    
                    if type(variation.reweight) is str:
                        reweight = 'reweight_' + variation.reweight + direction
                    elif type(variation.reweight) is float:
                        reweight = str(1. + variation.reweight * (1. - 2. * iv))
                    else:
                        reweight = ''

                    if variation.cuts is not None:
                        # variation cuts override the plotdef cut
                        cut = variation.cuts[iv].strip()
                    else:
                        cut = plotdef.cut.strip()

                    if variation.replacements is not None:
                        expr = plotdef.formExpression(variation.replacements[iv])
                    else:
                        expr = plotdef.formExpression()
                    

                    plotter.addPlot(
                        hist,
                        expr,
                        cut,
                        plotdef.applyBaseline,
                        plotdef.applyFullSel,
                        reweight
                    )

        # setup complete. Fill all plots in one go
        plotter.fillPlots()
    
        for hist in histograms:
            # ad-hoc scaling
            hist.Scale(group.scale)

            if sample.data and group != plotConfig.obs:
                # this is a data-driven background sample
                hist.Scale(postscale)

            # zero out negative bins (save the original as _orig)
            horig = None
            for iX in range(1, hist.GetNbinsX() + 1):
                if hist.GetBinContent(iX) < 0.:
                    if horig is None:
                        print '      Adjusting bin contents of', hist.GetDirectory().GetMotherDir().GetName(), hist.GetName(), 'to be non-negative'
                        horig = hist.Clone(hist.GetName() + '_original')

                    hist.SetBinContent(iX, 0.)
                    hist.SetBinError(iX, 0.)

                elif hist.GetBinContent(iX) - hist.GetBinError(iX) < 0.:
                    if horig is None:
                        print '      Adjusting bin errors of', hist.GetDirectory().GetMotherDir().GetName(), hist.GetName(), 'to be non-negative'
                        horig = hist.Clone(hist.GetName() + '_original')

                    hist.SetBinError(iX, hist.GetBinContent(iX))

            writeHist(hist)

            if horig is not None:
                horig.SetDirectory(hist.GetDirectory())
                writeHist(horig)

    # aggregate group plots

    # not for signal
    if group in plotConfig.sigGroups:
        return

    for plotdef in plotdefs:
        outDir = outFile.GetDirectory(plotdef.name)

        # simple sum of samples
        ghist = plotdef.makeHist(group.name, outDir = outDir)

        for sample in group.samples:
            shist = outDir.Get('samples/' + sample.name + '_' + region)
            ghist.Add(shist)

        writeHist(ghist)

        if group == plotConfig.obs:
            # take care of masking
            if plotdef.blind is not None:
                for iBin in range(1, obshist.GetNbinsX()+1):
                    binCenter = obshist.GetBinCenter(iBin)
                    if plotdef.fullyBlinded() or (binCenter > plotdef.blind[0] and (plotdef.blind[1] == 'inf' or binCenter < plotdef.blind[1])):
                        obshist.SetBinContent(iBin, 0.)
                        obshist.SetBinError(iBin, 0.)

        else:
            # write a group total histogram with systematic uncertainties added in quadrature (for display purpose only)
            outDir.cd()
            ghistSyst = ghist.Clone(group.name + '_syst')
    
            # variation Ups and Downs
            for variation in group.variations:
                uphist = plotdef.makeHist(group.name + '_' + variation.name + 'Up', outDir = outDir)
                downhist = plotdef.makeHist(group.name + '_' + variation.name + 'Down', outDir = outDir)
    
                for sample in group.samples:
                    suphist = outDir.Get('samples/' + sample.name + '_' + region + '_' + variation.name + 'Up')
                    sdownhist = outDir.Get('samples/' + sample.name + '_' + region + '_' + variation.name + 'Down')
                    uphist.Add(suphist)
                    downhist.Add(sdownhist)
    
                writeHist(uphist)
                writeHist(downhist)
                
                # add the average variation as systematics
                uphist.Add(downhist, -1.)
                uphist.Scale(0.5)
    
                for iX in range(1, hist.GetNbinsX() + 1):
                    err = math.sqrt(math.pow(ghistSyst.GetBinError(iX), 2.) + math.pow(uphist.GetBinContent(iX), 2.))
                    if err > ghistSyst.GetBinContent(iX):
                        err = ghistSyst.GetBinContent(iX)

                    ghistSyst.SetBinError(iX, err)
    
            writeHist(ghistSyst)


# python deletes histograms when variables are overwritten unless someone references the object
objectstore = []
def writeHist(hist):
    if not hist.GetDirectory() or not hist.GetDirectory().GetFile():
        # we don't have a persistent storage
        objectstore.append(hist)
        return

    gd = ROOT.gDirectory
    hist.GetDirectory().cd()
    hist.Write()
    gd.cd()


def formatHist(hist, plotdef):
    # Label the axes and normalize bin contents by width
    if plotdef.ndim() == 1:
        for iX in range(1, hist.GetNbinsX() + 1):
            cont = hist.GetBinContent(iX)
            err = hist.GetBinError(iX)
            w = hist.GetXaxis().GetBinWidth(iX)
            if plotdef.unit:
                hist.SetBinContent(iX, cont / w)
                hist.SetBinError(iX, err / w)
            else:
                if iX == 1:
                    wnorm = w

                hist.SetBinContent(iX, cont / (w / wnorm))
                hist.SetBinError(iX, err / (w / wnorm))

    hist.GetXaxis().SetTitle(plotdef.xtitle())
    hist.GetYaxis().SetTitle(plotdef.ytitle(binNorm = True))

    if plotdef.ndim() != 1:
        hist.GetZaxis().SetTitle('Events')
        hist.SetMinimum(0.)


def unformatHist(hist, plotdef):
    # Recompute raw bin contents
    if plotdef.ndim() == 1:
        for iX in range(1, hist.GetNbinsX() + 1):
            cont = hist.GetBinContent(iX)
            err = hist.GetBinError(iX)
            w = hist.GetXaxis().GetBinWidth(iX)
            if plotdef.unit:
                hist.SetBinContent(iX, cont * w)
                hist.SetBinError(iX, err * w)
            else:
                if iX == 1:
                    wnorm = w

                hist.SetBinContent(iX, cont * (w / wnorm))
                hist.SetBinError(iX, err * (w / wnorm))


def printCounts(counters, plotConfig):
    prec = '%.2f'

    # Print out the predictions and yield
    bkgTotal = 0.
    bkgTotalErr2 = 0.

    print 'Yields for ' + ' && '.join([plotConfig.baseline, plotConfig.fullSelection])

    for group in reversed(plotConfig.bkgGroups):
        counter = counters[group.name]
        count = counter.GetBinContent(1)
        err = counter.GetBinError(1)

        bkgTotal += count
        bkgTotalErr2 += math.pow(err, 2.)

        print ('%+12s  ' + prec + ' +- ' + prec) % (group.name, count, err)
    
    print '---------------------'
    print ('%+12s  ' + prec + ' +- ' + prec) % ('bkg', bkgTotal, math.sqrt(bkgTotalErr2))
    
    print '====================='
    
    for sspec in plotConfig.signalPoints:
        counter = counters[sspec.name]
        print ('%+12s  ' + prec + ' +- ' + prec) % (sspec.name, counter.GetBinContent(1), counter.GetBinError(1))
        # print ('%+12s  ' + prec + ' +- ' + prec + '  S/sqrt(B): ' + prec) % (sspec.name, counter.GetBinContent(1), counter.GetBinError(1), counter.GetBinContent(1) / math.sqrt(bkgTotal) )

    if 'data_obs' in counters:
        print '====================='
        print '%+12s  %d' % ('data_obs', int(counters['data_obs'].GetBinContent(1)))
    

def printBinByBin(stack, plotdef, plotConfig, precision = '.2f'):
    obs = stack['data_obs']
    nBins = obs.GetNbinsX()

    boundaries = []
    for iX in range(1, nBins + 1):
        boundaries.append('%12s' % ('[%.0f, %.0f]' % (obs.GetXaxis().GetBinLowEdge(iX), obs.GetXaxis().GetBinUpEdge(iX))))
    boundaries.append('%12s' % 'total')

    print 'Bin-by-bin yield for plot', plotdef.name
    print '           ' + ' '.join(boundaries)
    print '===================================================================================='

    bkgTotal = [0.] * nBins

    for group in reversed(plotConfig.bkgGroups):
        yields = []
        for iX in range(1, nBins + 1):
            cont = stack[group.name].GetBinContent(iX) * obs.GetXaxis().GetBinWidth(iX)
            yields.append(cont)
            bkgTotal[iX - 1] += cont

        print ('%+12s' % group.name), ' '.join([('%12' + precision) % y for y in yields]), (('%12' + precision) % sum(yields))

    print '------------------------------------------------------------------------------------'
    print ('%+12s' % 'total'), ' '.join([('%12' + precision) % b for b in bkgTotal]), (('%12' + precision) % sum(bkgTotal))
    print '===================================================================================='
    print ('%+12s' % 'data_obs'), ' '.join(['%12d' % int(round(obs.GetBinContent(iX)  * obs.GetXaxis().GetBinWidth(iX))) for iX in range(1, nBins + 1)]), ('%12d' % int(round(obs.Integral('width'))))


def printChi2(stack, plotdef, plotConfig, precision = '.2f'):
    obs = stack['data_obs']
    nBins = obs.GetNbinsX()

    residuals = [0.] * nBins
    err2s = [0.] * nBins
    for iX in range(1, nBins + 1):
        o = obs.GetBinContent(iX) * obs.GetXaxis().GetBinWidth(iX)
        residuals[iX - 1] = o
        err2s[iX - 1] = o
        
        for group in plotConfig.bkgGroups:
            x = stack[group.name].GetBinContent(iX) * obs.GetXaxis().GetBinWidth(iX)
            e = stack[group.name].GetBinError(iX) * obs.GetXaxis().GetBinWidth(iX)

            residuals[iX - 1] -= x
            err2s[iX - 1] += e * e

    chi2 = 0.
    for iR, res in enumerate(residuals):
        if err2s[iR] == 0.:
            continue

        chi2 += res * res / err2s[iR]

    print 'Chi2 for plot ' + plotdef.name + ': ' + str(chi2 / (nBins - 1))


def printCanvas(canvas, plotdef, plotConfig):
    """
    Print the canvas content as pdf and png.
    """

    eil = ROOT.gErrorIgnoreLevel
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    canvas.xtitle = plotdef.xtitle()
    canvas.ytitle = plotdef.ytitle(binNorm = True)

    canvas.selection = plotdef.formSelection(plotConfig)

    if plotdef.logy is None:
        logy = True
        addLinear = True
    else:
        logy = plotdef.logy
        addLinear = False

    canvas.ylimits = (plotdef.ymin, plotdef.ymax)
    canvas.Update(logy = logy, ymax = plotdef.ymax)

    if plotdef.fullyBlinded():
        # remove ratio pad. Hack to use SimpleCanvas interface
        simple = SimpleCanvas(lumi = canvas.lumi)

        garbage = []
        cnv = ROOT.TCanvas('tmp', 'tmp', 600, 600)
        cnv.cd()

        plotPad = canvas.plotPad.DrawClone()
        garbage.append(plotPad)
        plotPad.SetTopMargin(simple.canvas.GetTopMargin())
        plotPad.SetRightMargin(simple.canvas.GetRightMargin())
        plotPad.SetBottomMargin(simple.canvas.GetBottomMargin())
        plotPad.SetLeftMargin(simple.canvas.GetLeftMargin())

        xaxis = canvas.xaxis.DrawClone()
        garbage.append(xaxis)
        xaxis.SetX1(simple.canvas.GetLeftMargin())
        xaxis.SetX2(1. - simple.canvas.GetRightMargin())
        xaxis.SetY1(simple.canvas.GetBottomMargin())
        xaxis.SetY2(simple.canvas.GetBottomMargin())

        yaxis = canvas.yaxis.DrawClone()
        garbage.append(yaxis)
        yaxis.SetX1(simple.canvas.GetLeftMargin())
        yaxis.SetX2(simple.canvas.GetLeftMargin())
        yaxis.SetY1(simple.canvas.GetBottomMargin())
        yaxis.SetY2(1. - simple.canvas.GetTopMargin())

        simple.canvas.IsA().Destructor(simple.canvas)
        simple.canvas = cnv
        simple._needUpdate = False
        simple.printWeb(plotDir, plotdef.name)

        sys.stdout.write('    main')
        if logy:
            sys.stdout.write(' (log)')
        else:
            sys.stdout.write(' (lin)')

        if addLinear:
            simple.ylimits = (0., -1.)
            simple.minimum = -1.
            plotdef.ymax = -1.
            plotdef.ymin = 0.
            simple._needUpdate = True
            simple.printWeb(plotDir, plotdef.name + 'Linear', logy = False)

            sys.stdout.write(' (lin)')

        sys.stdout.write('\n')
        sys.stdout.flush()

        # cleanup the mess
        for obj in garbage:
            obj.IsA().Destructor(obj)

        cnv.IsA().Destructor(cnv)

    else:
        canvas.printWeb(plotDir, plotdef.name, drawLegend = False)

        sys.stdout.write('    main')
        if logy:
            sys.stdout.write(' (log)')
        else:
            sys.stdout.write(' (lin)')

        if addLinear:
            canvas.ylimits = (0., -1.)
            canvas.minimum = -1.
            plotdef.ymax = -1.
            plotdef.ymin = 0.
            canvas._needUpdate = True
            canvas.printWeb(plotDir, plotdef.name + 'Linear', logy = False)

            sys.stdout.write(' (lin)')

        sys.stdout.write('\n')
        sys.stdout.flush()

    ROOT.gErrorIgnoreLevel = eil


if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('config', metavar = 'CONFIG', help = 'Plot config name.')
    argParser.add_argument('--all-signal', '-S', action = 'store_true', dest = 'allSignal', help = 'Write histogram for all signal points.')
    argParser.add_argument('--asimov', '-v', metavar = '(background|<signal>)', dest = 'asimov', default = '', help = 'Plot the total background or signal + background as the observed distribution. For signal + background, give the signal point name.')
    argParser.add_argument('--bin-by-bin', '-y', metavar = 'PLOT', dest = 'bbb', default = '', help = 'Print out bin-by-bin breakdown of the backgrounds and observation.')
    argParser.add_argument('--blind', '-B', action = 'store_true', dest = 'blind', help = 'Do not plot the observed distribution.')
    argParser.add_argument('--chi2', '-x', metavar = 'PLOT', dest = 'chi2', default = '', help = 'Compute the chi2 for the plot.')
    argParser.add_argument('--clear-dir', '-R', action = 'store_true', dest = 'clearDir', help = 'Clear the plot directory first.')
    argParser.add_argument('--hist-file', '-o', metavar = 'PATH', dest = 'histFile', default = '', help = 'Histogram output file.')
    argParser.add_argument('--plot', '-p', metavar = 'NAME', dest = 'plots', nargs = '+', default = [], help = 'Limit plotting to specified set of plots.')
    argParser.add_argument('--plot-dir', '-d', metavar = 'PATH', dest = 'plotDir', default = '', help = 'Specify a directory under {webdir}/monophoton to save images. Use "-" for no output.')
    argParser.add_argument('--print-level', '-m', metavar = 'LEVEL', dest = 'printLevel', default = 0, help = 'Verbosity of the script.')
    argParser.add_argument('--replot', '-P', action = 'store_true', dest = 'replot', default = '', help = 'Do not fill histograms. Need --hist-file.')
    argParser.add_argument('--save-trees', '-t', action = 'store_true', dest = 'saveTrees', help = 'Write trees to output file instead of histograms.')
    argParser.add_argument('--skim-dir', '-i', metavar = 'PATH', dest = 'skimDir', help = 'Input skim directory.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT
    ROOT.gROOT.SetBatch(True)

    thisdir = os.path.dirname(os.path.realpath(__file__))
    basedir = os.path.dirname(thisdir)
    sys.path.append(basedir)

    from plotstyle import WEBDIR, SimpleCanvas, DataMCCanvas
    from main.plotconfig import getConfig
    import config

    ##################################
    ## PARSE COMMAND-LINE ARGUMENTS ##
    ##################################

    if not args.skimDir:
        from config import skimDir
        args.skimDir = skimDir

    plotConfig = getConfig(args.config)

    if args.bbb:
        plotdefs = [plotConfig.getPlot(args.bbb)]
    elif args.chi2:
        plotdefs = [plotConfig.getPlot(args.chi2)]
    elif len(args.plots) != 0:
        plotdefs = [p for p in plotConfig.plots if p.name in args.plots]
    else:
        plotdefs = list(plotConfig.plots)

    plotNames = [p.name for p in plotdefs]

    if args.histFile:
        if args.replot:
            histFile = ROOT.TFile.Open(args.histFile)
        else:
            histFile = ROOT.TFile.Open(args.histFile, 'recreate')

    else:
        if args.allSignal:
            print '--all-signal set but no output file is given.'
            sys.exit(1)

        if args.replot:
            print '--replot requires a --hist-file.'
            sys.exit(1)

        histFile = ROOT.gROOT

    if args.asimov:
        if args.saveTrees:
            print 'Cannot use --save-trees together with --asimov.'
            sys.exit(1)

        if args.asimov == 'background':
            pass
        elif args.asimov in [s.name for s in plotConfig.signalPoints]:
            print 'Feature under construction.'
            sys.exit(0)
        else:
            print 'Invalid value for option --asimov.'
            sys.exit(1)

    ############################
    ## SET UP FROM PLOTCONFIG ##
    ############################

    fullLumi = 0.
    effLumi = 0.
    for sample in plotConfig.obs.samples:
        fullLumi += sample.lumi
        effLumi += sample.lumi / plotConfig.prescales[sample]

    #####################################
    ## FILL HISTOGRAMS FROM SKIM TREES ##
    #####################################

    if not args.replot:
        ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
    
        print 'Filling plots for %s..' % plotConfig.name

        # for data-driven background estimates under presence of prescales
        # multiply the yields by postscale
        postscale = effLumi / fullLumi
    
        groups = list(plotConfig.bkgGroups)
        if args.allSignal:
            groups += plotConfig.sigGroups
        else:
            for sspec in plotConfig.signalPoints:
                if sspec.group not in groups:
                    groups.append(sspec.group)
                    sspec.group.samples = []
    
                sspec.group.samples.append(sspec.sample)

        if not args.asimov:
            groups.append(plotConfig.obs)
    
        for group in groups:
            print ' ', group.name
    
            fillPlots(plotConfig, group, plotdefs, args.skimDir, histFile, lumi = effLumi, postscale = postscale, printLevel = args.printLevel, altSourceDir = config.localSkimDir)
   
        # Save a background total histogram (for display purpose) for each plotdef
        for plotdef in plotdefs:
            outDir = histFile.GetDirectory(plotdef.name)

            bkghist = plotdef.makeHist('bkgtotal', outDir = outDir)
            bkghistSyst = plotdef.makeHist('bkgtotal_syst', outDir = outDir)

            for group in plotConfig.bkgGroups:
                bkghist.Add(outDir.Get(group.name))
                bkghistSyst.Add(outDir.Get(group.name + '_syst'))
    
            writeHist(bkghist)
            writeHist(bkghistSyst)

            if args.asimov == 'background':
                # generate the "observed" distribution from background total
                obshist = plotdef.makeHist('data_obs', outDir = outDir)
                for iBin in xrange(1, bkghist.GetNbinsX() + 1):
                    x = bkghist.GetXaxis().GetBinCenter(iBin)
                    for _ in xrange(int(round(bkghist.GetBinContent(iBin)))):
                        obshist.Fill(x)

                writeHist(obshist)

        if args.histFile:
            # close and reopen the output file
            histFile.Close()
            histFile = ROOT.TFile.Open(args.histFile)

    # closes if not args.replot


    ####################
    ## DRAW / ANALYZE ##
    ####################

    if args.plotDir == '-' and not ('count' in plotNames or args.bbb or args.chi2):
        # nothing to do
        sys.exit(0)

    print 'Drawing plots..'

    canvas = DataMCCanvas()

    nentries = (1 + len(plotConfig.bkgGroups) + len(plotConfig.signalPoints))
    ncolumns = math.ceil(float(nentries) / 5.) 
    xmin = 0.35 if ncolumns > 2 else 0.55
    canvas.legend.setPosition(xmin, SimpleCanvas.YMAX - 0.01 - 0.035 * 5, 0.92, SimpleCanvas.YMAX - 0.01)

    if args.plotDir:
        if args.plotDir == '-':
            plotDir = ''
        else:
            plotDir = args.plotDir
    else:
        plotDir = 'monophoton/' + plotConfig.name

    if plotDir and args.clearDir:
        for plot in os.listdir(WEBDIR + '/' + plotDir):
            os.remove(WEBDIR + '/' + plotDir + '/' + plot)

    for plotdef in plotdefs:
        print ' ', plotdef.name

        if plotDir:
            if plotdef.name != 'count' and plotdef.name != args.bbb and plotdef.name != args.chi2:
                graphic = True
            else:
                # nothing to do
                continue
        else:
            graphic = False

        if graphic:
            if plotdef.ndim() == 1:
                drawOpt = 'HIST'
            elif plotdef.ndim() == 2:
                drawOpt = 'LEGO4 F 0'

            # set up canvas
            canvas.Clear(full = True)

            isSensitive = plotdef.sensitive

        else:
            counters = {}
            isSensitive = True
    
        if isSensitive:
            canvas.lumi = effLumi
            # for data-driven background estimates under presence of prescales
            # multiply the yields by 1/postscale
            postscale = fullLumi / effLumi
        else:
            canvas.lumi = fullLumi
            postscale = 1.

        inDir = histFile.GetDirectory(plotdef.name)

        # fetch and format background groups
        for group in plotConfig.bkgGroups:
            ghist = inDir.Get(group.name + '_syst')

            if graphic:
                formatHist(ghist, plotdef)
                canvas.addStacked(ghist, title = group.title, color = group.color, drawOpt = drawOpt)
            else:
                counters[group.name] = ghist

        # background total used for uncertainty display
        bkgTotal = inDir.Get('bkgtotal_syst')
        if graphic:
            formatHist(bkgTotal, plotdef)

        # plot signal distributions for sensitive plots
        if isSensitive:
            for sspec in plotConfig.signalPoints:
                shist = inDir.Get('samples/' + sspec.name + '_' + plotConfig.name)

                if graphic:
                    formatHist(shist, plotdef)
                    canvas.addSignal(shist, title = sspec.title, color = sspec.color, drawOpt = drawOpt)
                else:
                    counters[sspec.name] = shist

        # observed distributions (if not blinded)
        if not args.blind:
            obshist = inDir.Get('data_obs')

            if graphic:
                formatHist(obshist, plotdef)
                canvas.addObs(obshist, title = plotConfig.obs.title)
            else:    
                counters['data_obs'] = obshist

        if plotdef.name == 'count':
            printCounts(counters, plotConfig)
        elif plotdef.name == args.bbb:
            printBinByBin(counters, plotdef, plotConfig)
        elif plotdef.name == args.chi2:
            printChi2(counters, plotdef, plotConfig)
        else:
            printCanvas(canvas, plotdef, plotConfig)
