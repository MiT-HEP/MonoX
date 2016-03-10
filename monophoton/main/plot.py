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

def groupHist(group, vardef, plotConfig, postscale = 1., outFile = None):
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
    varhists = {}

    for sname in group.samples:
        if group.region:
            hname = sname + '_' + group.region
        else:
            hname = ''

        # add up histograms from individual samples (saved to sampleDir)
        weightVariations = {}
        shist = getHist(sname, region, vardef, plotConfig.baseline, hname = hname, weightVariations = weightVariations, postscale = postscale, outDir = sampleDir)
        hist.Add(shist)
        
        # add up reweight variation histograms. name: variable-group_varname{Up,Down}
        for varname, (up, down) in weightVariations.items():
            if varname not in varhists:
                varhists[varname] = (vardef.makeHist(group.name + '_' + varname + 'Up', outDir = outFile), vardef.makeHist(group.name + '_' + varname + 'Down', outDir = outFile))

            varhists[varname][0].Add(up)
            varhists[varname][1].Add(down)

        # add the nominal if the sample does not have the particular variation
        for varname in varhists.keys():
            if varname not in weightVariations:
                varhists[varname][0].Add(shist)
                varhists[varname][1].Add(shist)

    # other systematics variation
    for variation in group.variations:
        # two histograms (up and down)
        vhists = tuple([vardef.makeHist(group.name + '_' + variation.name + v, outDir = outFile) for v in ['Up', 'Down']])
        varhists[variation.name] = vhists

        for iV in range(2):
            if variation.region:
                vregion = variation.region[iV]
            else:
                vregion = region

            if variation.replacements:
                repl = variation.replacements[iV]
            else:
                repl = []

            varname = variation.name + ('Up' if iV == 0 else 'Down')

            for sname in group.samples:
                if group.region:
                    hname = sname + '_' + group.region + '_' + varname
                else:
                    hname = sname + '_' + varname

                vhists[iV].Add(getHist(sname, vregion, vardef, plotConfig.baseline, hname = hname, cutReplacements = repl, postscale = postscale, outDir = sampleDir))

    # write raw histograms before formatting (which includes bin width normalization)
    writeHist(hist)
    for up, down in varhists.values():
        writeHist(up)
        writeHist(down)

    # apply variations as uncertainties
    for up, down in varhists.values():
        # take the average variation as uncertainty
        vhist = up.Clone(hist.GetName() + '_var')
        vhist.Add(down, -1.)
        vhist.Scale(0.5)

        for iX in range(1, hist.GetNbinsX() + 1):
            err = math.sqrt(math.pow(hist.GetBinError(iX), 2.) + math.pow(vhist.GetBinContent(iX), 2.))
            hist.SetBinError(iX, err)

        vhist.Delete()

    formatHist(hist, vardef)

    return hist


def getHist(sname, region, vardef, baseline, hname = '', weightVariations = None, cutReplacements = [], prescale = 1, postscale = 1., outDir = None, plotAcceptance = False):
    """
    Create a histogram object for a given variable (vardef) from a given sample and region.
    Baseline cut is applied before the vardef-specific cuts, unless vardef.applyBaseline is False.
    """

    if not hname:
        hname = sname

    # open the source file
    sourceName = config.skimDir + '/' + sname + '_' + region + '.root'
    if not os.path.exists(sourceName):
        print 'Error: Cannot open file', sourceName
        # return an empty histogram
        return vardef.makeHist(hname)

    sample = allsamples[sname]

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

    selection = '&&'.join(['(%s)' % c for c in cuts])

    for repl in cutReplacements:
        # replace the variable names given in repl = ('original', 'new')
        # enclose the original variable name with characters that would not be a part of the variable
        selection = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', selection)
        expr = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', expr)

    source = ROOT.TFile.Open(sourceName)
    tree = source.Get('events')

    # routine to fill a histogram with possible reweighting
    def fillHist(name, reweight = '1.'):
        """
        Fill h with expr, weighted with reweight * weight * (selection). Take care of overflows
        """

        h = vardef.makeHist(name, outDir = outDir)

        if plotAcceptance:
            weight = '1.'
        else:
            weight = 'weight'
            if not sample.data:
                weight += '*' + str(lumi)

        tree.Draw(expr + '>>' + h.GetName(), '%s*%s*(%s)' % (reweight, weight, selection), 'goff')
        if vardef.overflow:
            iOverflow = h.GetNbinsX()
            cont = h.GetBinContent(iOverflow)
            err2 = math.pow(h.GetBinError(iOverflow), 2.)
            h.SetBinContent(iOverflow, cont + h.GetBinContent(iOverflow + 1))
            h.SetBinError(iOverflow, math.sqrt(err2 + math.pow(h.GetBinError(iOverflow + 1), 2.)))

        for iX in range(1, h.GetNbinsX() + 1):
            if h.GetBinContent(iX) < 0.:
                h.SetBinContent(iX, 0.)
            if h.GetBinContent(iX) - h.GetBinError(iX) < 0.:
                h.SetBinError(iX, h.GetBinContent(iX) - 1.e-6)

        if plotAcceptance:
            h.Scale(1. / sample.nevents)

        writeHist(h)

        return h

    # fill the nominal histogram
    hist = fillHist(hname)

    if type(weightVariations) is dict:
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
    
            upHist = fillHist(hname + '_' + upName, reweight = 'reweight_' + upName)
            downHist = fillHist(hname + '_' + downName, reweight = 'reweight_' + downName)

            weightVariations[varName] = (upHist, downHist)
    
        if not sample.data:
            # lumi up and down
            upHist = hist.Clone(hist.GetName() + '_lumiUp')
            upHist.Scale(1. + lumiUncert)
            downHist = hist.Clone(hist.GetName() + '_lumiUp')
            downHist.Scale(1. - lumiUncert)

            weightVariations['lumi'] = (upHist, downHist)
    
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
    # Print out the predictions and yield
    bkgTotal = 0.
    bkgTotalErr2 = 0.

    print 'Yields for ' + plotConfig.baseline + ' && ' + plotConfig.fullSelection

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
    
    args = argParser.parse_args()
    sys.argv = []

    plotConfig = getConfig(args.config)

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
            plotDir = 'monophoton/' + args.plotDir
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
            hist = groupHist(group, vardef, plotConfig, postscale = postscale, outFile = outFile)

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

                hist = getHist(group.name, plotConfig.name, vardef, plotConfig.baseline, postscale = postscale, outDir = sampleDir)

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

                    getHist(sample.name, plotConfig.name, vardef, plotConfig.baseline, postscale = postscale, outDir = outFile)
                    
        obshist = vardef.makeHist('data_obs', outDir = outFile)

        for sname in plotConfig.obs.samples:
            obshist.Add(getHist(sname, plotConfig.name, vardef, plotConfig.baseline, prescale = prescale, outDir = sampleDir))

        writeHist(obshist)
        formatHist(obshist, vardef)

        # Take care of masking
        if vardef.blind is not None:
            for i in range(1, obshist.GetNbinsX()+1):
                binCenter = obshist.GetBinCenter(i)
                if binCenter > vardef.blind[0] and binCenter < vardef.blind[1]:
                    obshist.SetBinContent(i, 0.)
                    obshist.SetBinError(i, 0.)

        if vardef.name == 'count' or vardef.name == args.bbb:
            counters['data_obs'] = obshist
        elif plotDir:
            canvas.addObs(obshist, title = plotConfig.obs.title)

        if vardef.name == 'count':
            printCounts(counters, plotConfig)

        elif vardef.name == args.bbb:
            print 'Bin-by-bin yield for variable', args.bbb
            printBinByBin(counters, plotConfig)

        if plotDir and vardef.name != 'count':
            canvas.xtitle = obshist.GetXaxis().GetTitle()
            canvas.ytitle = obshist.GetYaxis().GetTitle()
            canvas.printWeb(plotDir, vardef.name, logy = vardef.logy, ymax = vardef.ymax)
