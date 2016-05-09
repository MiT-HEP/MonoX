#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
import os
import array
import math
import re

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

lumi = 0. # to be set in __main__

def groupHist(group, vardef, plotConfig, allsamples, skimDir, postscale = 1., outFile = None):
    """
    Fill and write the group histogram and its systematic variations.
    """

    if outFile:
        sampleDir = outFile.GetDirectory('samples')
    else:
        sampleDir = None

    if group.region:
        region = group.region
    else:
        region = plotConfig.name

    # nominal. name: variable-group
    hist = vardef.makeHist(group.name, outDir = outFile)

    for sname in group.samples:
        if group.region:
            hname = sname + '_' + group.region
        else:
            hname = ''

        # add up histograms from individual samples (saved to sampleDir)
        shist = getHist(sname, allsamples[sname], plotConfig, vardef, skimDir, region = region, hname = hname, postscale = postscale, outDir = sampleDir)
        shist.Scale(group.scale)
        hist.Add(shist)
        
    varhists = {}

    # systematics variations
    for variation in group.variations:
        if type(variation.reweight) is float:
            # uniform variation by a constant

            varname = variation.name + 'Var'

            vhist = vardef.makeHist(group.name + '_' + varname, outDir = outFile)

            reweight = 1. + variation.reweight

            for sname in group.samples:
                if group.region:
                    hname = sname + '_' + group.region + '_' + varname
                else:
                    hname = sname + '_' + varname

                shist = getHist(sname, allsamples[sname], plotConfig, vardef, skimDir, region = region, hname = hname, reweight = reweight, postscale = postscale, outDir = sampleDir)
                shist.Scale(group.scale)
                vhist.Add(shist)
                
            varhists[variation.name] = (vhist,) # make it a tuple to align with rest

        else:
            # up & down variations

            vhists = tuple([vardef.makeHist(group.name + '_' + variation.name + v, outDir = outFile) for v in ['Up', 'Down']])
    
            for iV in range(2):
                v = 'Up' if iV == 0 else 'Down'
                varname = variation.name + v

                if variation.region is not None:
                    vregion = variation.region[iV]
                else:
                    vregion = region
    
                if variation.replacements is not None:
                    repl = variation.replacements[iV]
                else:
                    repl = []
    
                if type(variation.reweight) is str:
                    reweight = 'reweight_' + variation.reweight + v
                else:
                    reweight = None
   
                for sname in group.samples:
                    if group.region:
                        hname = sname + '_' + group.region + '_' + varname
                    else:
                        hname = sname + '_' + varname
    
                    shist = getHist(sname, allsamples[sname], plotConfig, vardef, skimDir, region = vregion, hname = hname, cutReplacements = repl, reweight = reweight, postscale = postscale, outDir = sampleDir)
                    shist.Scale(group.scale)
                    vhists[iV].Add(shist)

            varhists[variation.name] = vhists

    # write raw histograms before formatting (which includes bin width normalization)
    writeHist(hist)
    for vhists in varhists.values():
        for vhist in vhists:
            writeHist(vhist)

    # apply variations as uncertainties
    for vhists in varhists.values():
        if len(vhists) == 1:
            vhist = vhists[0]
            vhist.Add(hist, -1.)
        else:
            # take the average variation as uncertainty
            vhist = vhists[0].Clone(hist.GetName() + '_var')
            vhist.Add(vhists[1], -1.)
            vhist.Scale(0.5)

        for iX in range(1, hist.GetNbinsX() + 1):
            err = math.sqrt(math.pow(hist.GetBinError(iX), 2.) + math.pow(vhist.GetBinContent(iX), 2.))
            hist.SetBinError(iX, err)

        if len(vhists) == 2:
            vhist.Delete()

    formatHist(hist, vardef)

    return hist


def getHist(sname, sample, plotConfig, vardef, skimDir, region = '', hname = '', cutReplacements = [], reweight = None, prescale = 1, postscale = 1., outDir = None, plotAcceptance = False):
    """
    Create a histogram object for a given variable (vardef) from a given sample and region (=plotConfig.name by default).
    Baseline cut is applied before the vardef-specific cuts, unless vardef.applyBaseline is False.
    """

    if not hname:
        hname = sname

    if not region:
        region = plotConfig.name

    # open the source file
    sourceName = skimDir + '/' + sname + '_' + region + '.root'
    if not os.path.exists(sourceName):
        print 'Error: Cannot open file', sourceName
        # return an empty histogram
        return vardef.makeHist(hname)

    # quantity to be plotted
    if type(vardef.expr) is tuple:
        expr = ':'.join(vardef.expr)
        print expr
        print ' '
    else:
        expr = vardef.expr

    # cuts and weights
    cuts = []
    if vardef.applyBaseline:
        cuts.append(plotConfig.baseline)

    if vardef.cut:
        cuts.append(vardef.cut)

    if vardef.applyFullSel:
        cuts.append(plotConfig.fullSelection)

    if prescale > 1 and vardef.blind is None:
        cuts.append('event % {prescale} == 0'.format(prescale = prescale))

    selection = '&&'.join(['(%s)' % c for c in cuts if c != ''])

    for repl in cutReplacements:
        # replace the variable names given in repl = ('original', 'new')
        # enclose the original variable name with characters that would not be a part of the variable
        selection = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', selection)
        expr = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', expr)

    source = ROOT.TFile.Open(sourceName)
    tree = source.Get('events')

    hist = vardef.makeHist(hname, outDir = outDir)

    if plotAcceptance:
        weight = '1.'
    else:
        weight = 'weight'
        if not sample.data:
            weight += '*' + str(lumi)

        if type(reweight) is float:
            weight += '*' + str(reweight)
        elif type(reweight) is str:
            weight += '*' + reweight

    tree.Draw(expr + '>>' + hist.GetName(), '%s*(%s)' % (weight, selection), 'goff')

    if vardef.overflow:
        iOverflow = hist.GetNbinsX()
        cont = hist.GetBinContent(iOverflow)
        err2 = math.pow(hist.GetBinError(iOverflow), 2.)
        hist.SetBinContent(iOverflow, cont + hist.GetBinContent(iOverflow + 1))
        hist.SetBinError(iOverflow, math.sqrt(err2 + math.pow(hist.GetBinError(iOverflow + 1), 2.)))

    if vardef.ndim() == 1:
        for iX in range(1, hist.GetNbinsX() + 1):
            if hist.GetBinContent(iX) < 0.:
                hist.SetBinContent(iX, 0.)
            if hist.GetBinContent(iX) - hist.GetBinError(iX) < 0.:
                hist.SetBinError(iX, hist.GetBinContent(iX) - 1.e-6)

    if plotAcceptance:
        hist.Scale(1. / sample.nevents)

    if sample.signal and sample.scale != 1.:
        # print sname
        # print hist.Integral()
        hist.Scale(sample.scale)
        # print hist.Integral()

    # To figure out which samples we need to scale
    """
    if sample.signal:
        norm = hist.Integral()
        print sname, norm
        if (norm < 0.05 or norm > 5000.) and norm != 0.:
            scale = 25. / norm
            print scale
            hist.Scale(scale)
            print hist.Integral()
    """

    writeHist(hist)

    # we don't need the tree any more
    source.Close()

    if postscale > 1. and vardef.blind is None:
        hist.Scale(1. / postscale)

    return hist


def writeHist(hist):
    if not hist.GetDirectory() or hist.GetDirectory() == ROOT.gROOT:
        return

    gd = ROOT.gDirectory
    hist.GetDirectory().cd()
    hist.Write()
    gd.cd()


def formatHist(hist, vardef):
    # Label the axes
    if vardef.ndim() == 1:
        for iX in range(1, hist.GetNbinsX() + 1):
            cont = hist.GetBinContent(iX)
            err = hist.GetBinError(iX)
            w = hist.GetXaxis().GetBinWidth(iX)
            if vardef.unit:
                hist.SetBinContent(iX, cont / w)
                hist.SetBinError(iX, err / w)
            else:
                if iX == 1:
                    wnorm = w

                hist.SetBinContent(iX, cont / (w / wnorm))
                hist.SetBinError(iX, err / (w / wnorm))

        xtitle = vardef.title
        if vardef.unit:
            xtitle += '(%s)' % vardef.unit

        ytitle = 'Events'
        if hist.GetXaxis().GetBinWidth(1) != 1.:
            ytitle += ' / '
            if vardef.unit:
                ytitle += vardef.unit
            else:
                ytitle += '%.2f' % hist.GetXaxis().GetBinWidth(1)

    else:
        xtitle = vardef.title[0]
        ytitle = vardef.title[1]
        ztitle = 'Events'

    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)

    if vardef.ndim() != 1:
        hist.GetZaxis().SetTitle(ztitle)
        hist.SetMinimum(0.)


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
    
    for group in plotConfig.sigGroups:
        counter = counters[group.name]
        print ('%+12s  ' + prec + ' +- ' + prec) % (group.name, counter.GetBinContent(1), counter.GetBinError(1))
    
    print '====================='
    print '%+12s  %d' % ('data_obs', int(counters['data_obs'].GetBinContent(1)))
    

def printBinByBin(stack, plotConfig, precision = '.2f'):
    obs = stack['data_obs']
    nBins = obs.GetNbinsX()

    boundaries = []
    for iX in range(1, nBins + 1):
        boundaries.append('%12s' % ('[%.0f, %.0f]' % (obs.GetXaxis().GetBinLowEdge(iX), obs.GetXaxis().GetBinUpEdge(iX))))
    boundaries.append('%12s' % 'total')

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


if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('config', metavar = 'CONFIG', help = 'Plot config name.')
    argParser.add_argument('--count-only', '-C', action = 'store_true', dest = 'countOnly', help = 'Just display the event counts.')
    argParser.add_argument('--bin-by-bin', '-y', metavar = 'PLOT', dest = 'bbb', default = '', help = 'Print out bin-by-bin breakdown of the backgrounds and observation.')
    argParser.add_argument('--prescale', '-b', metavar = 'PRESCALE', dest = 'prescale', type = int, default = 1, help = 'Prescale for prescaling.')
    argParser.add_argument('--clear-dir', '-R', action = 'store_true', dest = 'clearDir', help = 'Clear the plot directory first.')
    argParser.add_argument('--plot', '-p', metavar = 'NAME', dest = 'plots', nargs = '+', default = [], help = 'Limit plotting to specified set of plots.')
    argParser.add_argument('--plot-dir', '-d', metavar = 'PATH', dest = 'plotDir', default = '', help = 'Specify a directory under {webdir}/monophoton to save images. Use "-" for no output.')
    argParser.add_argument('--out-file', '-o', metavar = 'PATH', dest = 'outFile', default = '', help = 'Histogram output file.')
    argParser.add_argument('--all-signal', '-S', action = 'store_true', dest = 'allSignal', help = 'Write histogram for all signal points.')
    argParser.add_argument('--plot-configs', '-c', metavar = 'PATH', dest = 'plotConfigFile', help = 'Plot config file that defines a getConfig function which returns a PlotConfig.')
    argParser.add_argument('--skim-dir', '-i', metavar = 'PATH', dest = 'skimDir', help = 'Input skim directory.')
    argParser.add_argument('--samples-list', '-s', metavar = 'PATH', dest = 'samplesList', help = 'Dataset list CSV file.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT
    ROOT.gROOT.SetBatch(True)

    from plotstyle import SimpleCanvas, DataMCCanvas
    from datasets import SampleDefList

    if not args.skimDir:
        from config import skimDir
        args.skimDir = skimDir

    if args.plotConfigFile:
        execfile(args.plotConfigFile)
        plotConfig = getConfig(args.config)
    else:
        from main.plotconfig import getConfig
        plotConfig = getConfig(args.config)

    if args.samplesList:
        allsamples = SampleDefList(listpath = args.samplesList)
    else:
        allsamples = SampleDefList(listpath = basedir + '/data/datasets.csv')

    if len(args.plots) == 0:
        args.plots = [v.name for v in plotConfig.variables]

    # backward compatibility
    if args.countOnly:
        args.plots = ['count']

    if args.bbb:
        args.plots = [args.bbb]

    if args.outFile:
        outFile = ROOT.TFile.Open(args.outFile, 'recreate')
        sampleDir = outFile.mkdir('samples')
    else:
        outFile = None
        sampleDir = None

    # lumi defined in the global scope for getHist function
    for sName in plotConfig.obs.samples:
        lumi += allsamples[sName].lumi

    canvas = DataMCCanvas(lumi = lumi)

    if args.plotDir:
        if args.plotDir == '-':
            plotDir = ''
        else:
            plotDir = args.plotDir
    else:
        plotDir = 'monophoton/' + args.config

    if plotDir and args.clearDir:
        for plot in os.listdir(canvas.webdir + '/' + plotDir):
            os.remove(canvas.webdir + '/' + plotDir + '/' + plot)

    print "Starting plot making."
    
    for vardef in plotConfig.variables + [plotConfig.countConfig()]:
        if vardef.name not in args.plots:
            continue

        print vardef.name

        if vardef.name == 'count' or vardef.name == args.bbb:
            counters = {}
            isSensitive = True

        else:
            # set up canvas
            canvas.Clear(full = True)
            canvas.legend.setPosition(0.6, SimpleCanvas.YMAX - 0.01 - 0.035 * (1 + len(plotConfig.bkgGroups) + len(plotConfig.sigGroups)), 0.92, SimpleCanvas.YMAX - 0.01)
            isSensitive = vardef.name in plotConfig.sensitiveVars
    
        if isSensitive:
            canvas.lumi = lumi / args.prescale
            prescale = args.prescale
            postscale = float(args.prescale)
        else:
            canvas.lumi = lumi
            prescale = 1
            postscale = 1.

        # make background histograms
        for group in plotConfig.bkgGroups:
            hist = groupHist(group, vardef, plotConfig, allsamples, args.skimDir, postscale = postscale, outFile = outFile)

            if vardef.name == 'count' or vardef.name == args.bbb:
                counters[group.name] = hist
            elif plotDir:
                canvas.addStacked(hist, title = group.title, color = group.color)

        # plot signal distributions for sensitive variables
        if isSensitive or outFile:
            sigGroups = []
            for group in plotConfig.sigGroups:
                # signal groups should only have one sample

                sigGroups.append(group.name)

                hist = getHist(group.name, allsamples[group.name], plotConfig, vardef, args.skimDir, postscale = postscale, outDir = sampleDir)

                hist.SetDirectory(outFile)

                writeHist(hist)
                formatHist(hist, vardef)

                if vardef.name == 'count':
                    counters[group.name] = hist
                elif plotDir:
                    canvas.addSignal(hist, title = group.title, color = group.color)

            if args.allSignal:
                # when output file is specified, make plots for all signal models
                for sample in allsamples:
                    if not sample.signal or sample.name in sigGroups:
                        continue

                    getHist(sample.name, allsamples[sample.name], plotConfig, vardef, args.skimDir, postscale = postscale, outDir = outFile)
                    
        obshist = vardef.makeHist('data_obs', outDir = outFile)

        for sname in plotConfig.obs.samples:
            obshist.Add(getHist(sname, allsamples[sname], plotConfig, vardef, args.skimDir, prescale = prescale, outDir = sampleDir))

        writeHist(obshist)
        formatHist(obshist, vardef)

        # Take care of masking
        if vardef.blind is not None:
            for i in range(1, obshist.GetNbinsX()+1):
                binCenter = obshist.GetBinCenter(i)
                if vardef.fullyBlinded() or (binCenter > vardef.blind[0] and (vardef.blind[1] == 'inf' or binCenter < vardef.blind[1])):
                    obshist.SetBinContent(i, 0.)
                    obshist.SetBinError(i, 0.)

        if vardef.name == 'count' or vardef.name == args.bbb:
            counters['data_obs'] = obshist
        elif plotDir and not vardef.fullyBlinded():
            canvas.addObs(obshist, title = plotConfig.obs.title)

        if vardef.name == 'count':
            printCounts(counters, plotConfig)

        elif vardef.name == args.bbb:
            print 'Bin-by-bin yield for variable', args.bbb
            printBinByBin(counters, plotConfig)

        if plotDir and vardef.name != 'count':
            canvas.xtitle = obshist.GetXaxis().GetTitle()
            canvas.ytitle = obshist.GetYaxis().GetTitle()

            canvas.Update(logy = vardef.logy, ymax = vardef.ymax)

            if vardef.fullyBlinded():
                # remove ratio pad
                simple = SimpleCanvas(lumi = lumi)

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
                simple.printWeb(plotDir, vardef.name)

                # cleanup the mess
                for obj in garbage:
                    obj.IsA().Destructor(obj)

                cnv.IsA().Destructor(cnv)

            else:
                canvas.printWeb(plotDir, vardef.name)
