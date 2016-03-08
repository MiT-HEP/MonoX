#!/usr/bin/env python

import sys
import os
import array
import math
import re
import ROOT

ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig

lumi = 0. # to be set in __main__
lumiUncert = 0.027

def getHist(sample, region, vardef, baseline, weightVariation = True, cutReplacements = [], prescale = 1, postscale = 1.):
    """
    Create a histogram object for a given variable (vardef) from a given sample and region.
    Baseline cut is applied before the vardef-specific cuts, unless vardef.applyBaseline is False.
    """

    histName = vardef.name + '-' + sample.name + '_' + region
    sourceName = config.skimDir + '/' + sample.name + '_' + region + '.root'

    # quantity to be plotted
    if type(vardef.expr) is tuple:
        expr = ':'.join(vardef.expr)
    else:
        expr = vardef.expr

    # cuts and weights
    cuts = ['1']
    if vardef.applyBaseline and baseline:
        cuts = [baseline]

    if vardef.cut:
        cuts.append(vardef.cut)

    if prescale > 1 and vardef.blind is None:
        cuts.append('event % {prescale} == 0'.format(prescale = args.prescale))

    weightexpr = 'weight*(' + '&&'.join(['(%s)' % c for c in cuts]) + ')'

    if cutReplacements:
        print 'original', weightexpr

    for repl in cutReplacements:
        # replace the variable names given in repl = ('original', 'new')
        # enclose the original variable name with characters that would not be a part of the variable
        weightexpr = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', weightexpr)
        expr = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', expr)

    if not sample.data:
        weightexpr = str(lumi) + '*' + weightexpr

    # open the source file
    if not os.path.exists(sourceName):
        print 'Error: Cannot open file', sourceName
        # return an empty histogram
        return vardef.makeHist(histName)

    source = ROOT.TFile.Open(sourceName)
    tree = source.Get('events')

    # routine to fill a histogram with possible reweighting
    def fillHist(name, reweight = '1.'):
        """
        Fill h with expr, weighted with reweight * weightexpr. Take care of overflows
        """

        ROOT.gROOT.cd()
        h = vardef.makeHist(name)
        tree.Draw(expr + '>>' + name, reweight + '*' + weightexpr, 'goff')
        if vardef.overflow:
            iOverflow = h.GetNbinsX()
            cont = h.GetBinContent(iOverflow)
            err2 = math.pow(h.GetBinError(iOverflow), 2.)
            h.SetBinContent(iOverflow, cont + h.GetBinContent(iOverflow + 1))
            h.SetBinError(iOverflow, math.sqrt(err2 + math.pow(h.GetBinError(iOverflow + 1), 2.)))

        return h

    # fill the nominal histogram
    hist = fillHist(histName)

    if weightVariation:
        # set bin errors to uncertainties from weight variations
        diffs = []
        for branch in tree.GetListOfBranches():
            bname = branch.GetName()

            # find the shift-up weights reweight_(*)Up
            if not bname.startswith('reweight_') or not bname.endswith('Up'):
                continue

            upName = bname.replace('reweight_', '')
            varName = upName[0:-2]
            downName = varName + 'Down'

            if not tree.GetBranch('reweight_' + downName):
                print 'Weight variation ' + varName + ' does not have downward shift in ' + sample.name + ' ' + region
                continue

            upHist = fillHist(histName + '_' + upName, reweight = 'reweight_' + upName)
            downHist = fillHist(histName + '_' + downName, reweight = 'reweight_' + downName)

            upHist.Add(hist, -1.)
            downHist.Add(hist, -1.)

            # take the average variation as uncertainty
            varHist = upHist.Clone(histName + '_' + varName)
            varHist.Add(downHist, -1.)
            varHist.Scale(0.5)

            diffs.append(varHist)

        if not sample.data:
            # lumi up and down
            varHist = hist.Clone(histName + '_lumi')
            varHist.Scale(lumiUncert)

            diffs.append(varHist)

        for diff in diffs:
            for iX in range(1, hist.GetNbinsX() + 1):
                err = math.sqrt(math.pow(hist.GetBinError(iX), 2.) + math.pow(diff.GetBinContent(iX), 2.))
                hist.SetBinError(iX, err)

    # we don't need the tree any more
    source.Close()

    for iX in range(1, hist.GetNbinsX() + 1):
        if hist.GetBinContent(iX) < 0.:
            hist.SetBinContent(iX, 0.)
        if hist.GetBinContent(iX) - hist.GetBinError(iX) < 0.:
            hist.SetBinError(iX, hist.GetBinContent(iX) - 1.e-6)

    if postscale > 1. and vardef.blind is None:
        hist.Scale(1. / postscale)

    # Take care of masking
    if sample.data and vardef.blind:
        for i in range(1, hist.GetNbinsX()+1):
            binCenter = hist.GetBinCenter(i)
            if binCenter > vardef.blind[0] and binCenter < vardef.blind[1]:
                hist.SetBinContent(i, 0.)
                hist.SetBinError(i, 0.)

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

    return hist


if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('region', metavar = 'REGION', help = 'Control or signal region name.')
    argParser.add_argument('--count-only', '-C', action = 'store_true', dest = 'countOnly', help = 'Just display the event counts.')
    argParser.add_argument('--bin-by-bin', '-y', metavar = 'PLOT', dest = 'bbb', default = '', help = 'Print out bin-by-bin breakdown of the backgrounds and observation.')
    argParser.add_argument('--prescale', '-b', metavar = 'PRESCALE', dest = 'prescale', type = int, default = 1, help = 'Prescale for prescaling.')
    argParser.add_argument('--clear-dir', '-R', action = 'store_true', dest = 'clearDir', help = 'Clear the plot directory first.')
    argParser.add_argument('--plot', '-p', metavar = 'NAME', dest = 'plots', nargs = '+', default = [], help = 'Limit plotting to specified set of plots.')
    argParser.add_argument('--plot-dir', '-d', metavar = 'PATH', dest = 'plotDir', default = '', help = 'Specify a directory under {webdir}/monophoton to save images.')
    
    args = argParser.parse_args()
    sys.argv = []

    plotConfig = getConfig(args.region)

    # lumi defined in the global scope for getHist function
    for sName in plotConfig.obs.samples:
        lumi += allsamples[sName].lumi

    if not args.countOnly or args.bbb != '':
        if args.bbb:
            stack = {}
    
        canvas = DataMCCanvas(lumi = lumi)

        if args.plotDir:
            plotDir = 'monophoton/' + args.plotDir
        else:
            plotDir = 'monophoton/' + args.region
    
        if args.clearDir:
            for plot in os.listdir(canvas.webdir + '/' + plotDir):
                os.remove(canvas.webdir + '/' + plotDir + '/' + plot)
    
        print "Starting plot making."
        
        for vardef in plotConfig.variables:
            if args.countOnly and vardef.name != args.bbb:
                continue

            if len(args.plots) != 0 and vardef.name not in args.plots:
                continue

            print vardef.name

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
                idx = -1
                if group.region:
                    region = group.region
                else:
                    region = plotConfig.name

                # combined group histogram
                histName = vardef.name + '-' + group.name
                hist = vardef.makeHist(histName)

                for sName in group.samples:
                    hist.Add(getHist(allsamples[sName], region, vardef, plotConfig.baseline, postscale = postscale))

                # systematics variation
                for variation in group.variations:
                    # two histograms (up and down)
                    vhists = tuple([vardef.makeHist(histName + '_' + variation.name + v) for v in ['Up', 'Down']])

                    for iV in range(2):
                        if variation.region:
                            vregion = variation.region[iV]
                        else:
                            vregion = region

                        if variation.replacements:
                            repl = variation.replacements[iV]
                        else:
                            repl = []

                        for sName in group.samples:
                            vhists[iV].Add(getHist(allsamples[sName], vregion, vardef, plotConfig.baseline, weightVariation = False, cutReplacements = repl, postscale = postscale))

                    vhists[0].Add(hist, -1.)
                    vhists[1].Add(hist, -1.)

                    # take the average variation as uncertainty
                    varHist = vhists[0].Clone(histName + '_' + variation.name)
                    varHist.Add(vhists[1], -1.)
                    varHist.Scale(0.5)
                        
                    for iX in range(1, hist.GetNbinsX() + 1):
                        err = math.sqrt(math.pow(hist.GetBinError(iX), 2.) + math.pow(varHist.GetBinContent(iX), 2.))
                        hist.SetBinError(iX, err)

                canvas.addStacked(hist, title = group.title, color = group.color)

                if vardef.name == args.bbb:
                    stack[group.name] = hist.Clone(group.name + '_bbb')

            # plot signal distributions for sensitive variables
            if isSensitive:
                for group in plotConfig.sigGroups:
                    # signal groups should only have one sample

                    hist = getHist(allsamples[group.name], plotConfig.name, vardef, plotConfig.baseline, postscale = postscale)
    
                    canvas.addSignal(hist, title = group.title, color = group.color)
        
            for sName in plotConfig.obs.samples:
                hist = getHist(allsamples[sName], plotConfig.name, vardef, plotConfig.baseline, prescale = prescale)

                canvas.addObs(hist, title = plotConfig.obs.title)
    
                if vardef.name == args.bbb:
                    try:
                        stack['obs'].Add(hist)
                    except KeyError:
                        stack['obs'] = hist.Clone('obs_bbb')
        
            canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
            canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()
    
            if not args.countOnly:
                canvas.printWeb(plotDir, vardef.name, logy = vardef.logy, ymax = vardef.ymax)
    
        print "Finished plotting."
    
    print "Counting yields and preparing limits file."
   
    # counters: list of single-bin histograms
    counters = {}
    isSensitive = (len(plotConfig.sensitiveVars) != 0) # if any variable is deemed sensitive, signal region count should also be
    vardef = plotConfig.countConfig()

    if isSensitive:
        prescale = args.prescale
        postscale = float(args.prescale)
    else:
        prescale = 1
        postscale = 1.

    for group in plotConfig.bkgGroups:
        counters[group.name] = vardef.makeHist('counts-' + group.name + '_' + plotConfig.name)

        if group.region:
            region = group.region
        else:
            region = plotConfig.name

        for sName in group.samples:
            hist = getHist(allsamples[sName], region, vardef, plotConfig.baseline, postscale = postscale)
            counters[group.name].Add(hist)

    for group in plotConfig.sigGroups:
        hist = getHist(allsamples[group.name], plotConfig.name, vardef, plotConfig.baseline, postscale = postscale)

        counters[group.name] = hist
    
    counters['obs'] = vardef.makeHist('counts-obs_' + plotConfig.name)

    for sName in plotConfig.obs.samples:
        hist = getHist(allsamples[sName], plotConfig.name, vardef, plotConfig.baseline, prescale = prescale)
        counters['obs'].Add(hist)

    # Print out the predictions and yield
    bkgTotal = 0.
    bkgTotalErr2 = 0.
    print 'Yields for ' + plotConfig.baseline + ' && ' + vardef.cut
    for group in reversed(plotConfig.bkgGroups):
        counter = counters[group.name]
        count = counter.GetBinContent(1)
        err = counter.GetBinError(1)

        bkgTotal += count
        bkgTotalErr2 += math.pow(err, 2.)

        print '%+12s  %.2f +- %.2f' % (group.name, count, err)
    
    print '---------------------'
    print '%+12s  %.2f +- %.2f' % ('bkg', bkgTotal, math.sqrt(bkgTotalErr2))
    
    print '====================='
    
    for group in plotConfig.sigGroups:
        counter = counters[group.name]
        print '%+12s  %.2f +- %.2f' % (group.name, counter.GetBinContent(1), counter.GetBinError(1))
    
    print '====================='
    print '%+12s  %d' % ('obs', int(counters['obs'].GetBinContent(1)))
    
    if args.bbb != '':
        print 'Bin-by-bin yield for variable', args.bbb
    
        obs = stack['obs']
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
    
            print ('%+12s' % group.name), ' '.join(['%12.2f' % y for y in yields]), ('%12.2f' % sum(yields))
    
        print '------------------------------------------------------------------------------------'
        print ('%+12s' % 'total'), ' '.join(['%12.2f' % b for b in bkgTotal]), ('%12.2f' % sum(bkgTotal))
        print '===================================================================================='
        print ('%+12s' % 'obs'), ' '.join(['%12d' % int(round(obs.GetBinContent(iX)  * obs.GetXaxis().GetBinWidth(iX))) for iX in range(1, nBins + 1)]), ('%12d' % int(round(obs.Integral('width'))))
