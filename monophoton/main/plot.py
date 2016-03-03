#!/usr/bin/env python

import sys
import os
import collections
import array
import math
import ROOT

ROOT.gROOT.SetBatch(True)

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig

def getHist(sampledef, selection, vardef, baseline, lumi = 0., isSensitive = False):
    
    histName = vardef.name + '-' + sampledef.name + '-' + selection
    fileName = config.skimDir + '/' + sampledef.name + '_' + selection + '.root'

    if vardef.is2D:
        nbins = []
        arr = []
        for binning in vardef.binning:
            if type(binning) is list:
                nbins_ = len(binning) - 1
                binning_ = list(binning)
            elif type(binning) is tuple:
                nbins_ = binning[0]
                binning_ = [binning[1] + (binning[2] - binning[1]) / nbins * i for i in range(nbins + 1)]
                
            arr_ = array.array('d', binning_)
            nbins.append(nbins_)
            arr.append(arr_)

        hist = ROOT.TH2D(histName, '', nbins[0], arr[0], nbins[1], arr[1]) 
        
    else:
        if type(vardef.binning) is list:
            nbins = len(vardef.binning) - 1
            binning = list(vardef.binning)
        elif type(vardef.binning) is tuple:
            nbins = vardef.binning[0]
            binning = [vardef.binning[1] + (vardef.binning[2] - vardef.binning[1]) / nbins * i for i in range(nbins + 1)]

        arr = array.array('d', binning)

        hist = ROOT.TH1D(histName, '', nbins, arr)

        if vardef.overflow:
            lastbinWidth = (binning[-1] - binning[0]) / 30.
            binning += [binning[-1] + lastbinWidth]
            arr = array.array('d', binning)
            hist.SetBins(len(binning) - 1, arr)

    if not os.path.exists(fileName):
        # need to be slightly smarter about this for the MC backgrounds
        return hist

    source = ROOT.TFile.Open(fileName)
    tree = source.Get('events')

    hist.SetDirectory(source)

    cuts = []
    if vardef.baseline:
        cuts.append(baseline)

    cuts.append(vardef.cut)

    if isSensitive and args.blind > 1:
        cuts.append('event % {blind} == 0'.format(blind = args.blind))

    cut = '&&'.join(c for c in cuts if c)

    if cut:
        weightexpr = 'weight * (%s)' % cut
    else:
        weightexpr = 'weight'

    drawexpr = vardef.expr + '>>' + histName

    hist.Sumw2()
    if sampledef.data:
        tree.Draw(drawexpr, weightexpr, 'goff')
        if vardef.blind:
            for i in range(1, hist.GetNbinsX()+1):
                binCenter = hist.GetBinCenter(i)
                if binCenter > vardef.blind[0] and binCenter < vardef.blind[1]:
                    hist.SetBinContent(i, 0.)
                    hist.SetBinError(i, 0.)

    else:
        weightexpr = str(lumi) + ' * ' + weightexpr
        tree.Draw(drawexpr, weightexpr, 'goff')

    hist.SetDirectory(0)
    if vardef.is2D:
        xtitle = vardef.title[0]
        ytitle = vardef.title[1]
        ztitle = 'Events'
    else:
        for iX in range(1, nbins + 1):
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

    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)
    if vardef.is2D:
        hist.GetZaxis().SetTitle(ztitle)
        hist.SetMinimum(0.)

    return hist


if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('region', metavar = 'REGION', help = 'Control or signal region name.')
    argParser.add_argument('--count-only', '-C', action = 'store_true', dest = 'countOnly', help = 'Just display the event counts.')
    argParser.add_argument('--bin-by-bin', '-y', metavar = 'PLOT', dest = 'bbb', default = '', help = 'Print out bin-by-bin breakdown of the backgrounds and observation.')
    argParser.add_argument('--blind', '-b', metavar = 'PRESCALE', dest = 'blind', type = int, default = 1, help = 'Prescale for blinding.')
    argParser.add_argument('--clear-dir', '-R', action = 'store_true', dest = 'clearDir', help = 'Clear the plot directory first.')
    
    args = argParser.parse_args()
    sys.argv = []

    plotConfig = getConfig(args.region)

    lumi = 0.
    for sName in plotConfig.obs.samples:
        if type(sName) is tuple:
            lumi += allsamples[sName[0]].lumi
        else:
            lumi += allsamples[sName].lumi
    
    if not args.countOnly or args.bbb != '':
        if args.bbb:
            stack = {}
    
        canvas = DataMCCanvas(lumi = lumi)
        simpleCanvas = SimpleCanvas(lumi = lumi, sim = True)
    
        plotdir = canvas.webdir + '/monophoton/' + args.region
    
        if args.clearDir:
            for plot in os.listdir(plotdir):
                os.remove(plotdir + '/' + plot)
    
        print "Starting plot making."
        
        for vardef in plotConfig.variables:
            if args.countOnly and vardef.name != args.bbb:
                continue

            print vardef.name
    
            isSensitive = vardef.name in plotConfig.sensitiveVars
    
            canvas.Clear(full = True)
            canvas.legend.setPosition(0.6, SimpleCanvas.YMAX - 0.01 - 0.035 * (1 + len(plotConfig.bkgGroups) + len(plotConfig.sigGroups)), 0.92, SimpleCanvas.YMAX - 0.01)
        
            if isSensitive:
                canvas.lumi = lumi / args.blind
            else:
                canvas.lumi = lumi
        
            for group in plotConfig.bkgGroups:
                idx = -1
                for sName in group.samples:
                    if type(sName) is tuple:
                        selection = sName[1]
                        sName = sName[0]
                    else:
                        selection = plotConfig.defaultRegion
        
                    hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, lumi = lumi)
      
                    for iX in range(1, hist.GetNbinsX() + 1):
                        if hist.GetBinContent(iX) < 0.:
                            hist.SetBinContent(iX, 0.)
        
                    if isSensitive and args.blind > 1:
                        hist.Scale(1. / args.blind)
       
                    idx = canvas.addStacked(hist, title = group.title, color = group.color, idx = idx)
    
                    if vardef.name == args.bbb:
                        try:
                            stack[group.name].Add(hist)
                        except KeyError:
                            stack[group.name] = hist.Clone(grop.name + '_bbb')
    
            if isSensitive:
                for sGroup in plotConfig.sigGroups:
                    idx = -1
                    for sName in sGroup.samples:
                        if type(sName) is tuple:
                            selection = sName[1]
                            sName = sName[0]
                        else:
                            selection = plotConfig.defaultRegion
    
                        hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, lumi = lumi)
                        if args.blind > 1:
                            hist.Scale(1. / args.blind)
        
                        idx = canvas.addSignal(hist, title = sGroup.title, color = sGroup.color, idx = idx)
        
            for sName in plotConfig.obs.samples:
                if type(sName) is tuple:
                    selection = sName[1]
                    sName = sName[0]
                else:
                    selection = plotConfig.defaultRegion
    
                hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, isSensitive = isSensitive)
                canvas.addObs(hist, title = plotConfig.obs.title)
    
                if vardef.name == args.bbb:
                    try:
                        stack['obs'].Add(hist)
                    except KeyError:
                        stack['obs'] = hist.Clone('obs_bbb')
        
            canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
            canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()
    
            if not args.countOnly:
                canvas.printWeb('monophoton/' + args.region, vardef.name, logy = vardef.logy, ymax = vardef.ymax)
    
        print "Finished plotting."
    
    print "Counting yields and preparing limits file."
#    systs = [ '', '-gup', '-gdown', '-jecup', '-jecdown' ] 
    
    #canvas = simpleCanvas # this line causes segfault somewhere down the line of DataMCCanvas destruction
    hists = {}
    counts = {}
    isSensitive = ('count' in plotConfig.sensitiveVars)
    vardef = plotConfig.countConfig()

    blindScale = 1.
    if isSensitive:
        blindScale = args.blind
    
    for group in plotConfig.bkgGroups:
        counts[group.name] = 0.
        for sName in group.samples:
            if type(sName) is tuple:
                selection = sName[1]
                sName = sName[0]
            else:
                selection = plotConfig.defaultRegion
    
            hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, lumi = lumi)
            counts[group.name] += hist.GetBinContent(1) / blindScale
    
#            for syst in systs:
#                hist2D = getHist(allsamples[sName], selection+syst, 'limit', limitDef, isSensitive = isSensitive)
#                histName = group.name + syst
#                if histName in hists.keys():
#                    hists[histName].Add(hist2D)
#                else:
#                    hists[histName] = hist2D
#                    hists[histName].SetName(histName)
#                if 'sph' in sName:
#                    break
    
    if isSensitive:
        for sGroup in plotConfig.sigGroups:
            for sName in sGroup.samples:
                if type(sName) is tuple:
                    selection = sName[1]
                    sName = sName[0]
                else:
                    selection = plotConfig.defaultRegion
    
                hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, lumi = lumi)
                counts[sName] = hist.GetBinContent(1) / blindScale
    
#                for syst in systs:
#                    hist2D = getHist(allsamples[sName], selection+syst, 'limit', limitDef, isSensitive = isSensitive)
#                    if sName+syst in hists.keys():
#                        hists[sName+syst].Add(hist2D)
#                    else:
#                        hists[sName+syst] = hist2D
#                        hists[sName+syst].SetName(sName+syst)
    
    counts['obs'] = 0.
    for sName in plotConfig.obs.samples:
        if type(sName) is tuple:
            selection = sName[1]
            sName = sName[0]
        else:
            selection = plotConfig.defaultRegion
    
        hist = getHist(allsamples[sName], selection, vardef, plotConfig.baseline, isSensitive = isSensitive)
        counts['obs'] += hist.GetBinContent(1)
    
#        hist2D = getHist(allsamples[sName], selection, 'limit', limitDef, isSensitive = blindCounts)
#        if 'obs' in hists.keys():
#            hists['obs'].Add(hist2D)
#        else:
#            hists['obs'] = hist2D
#            hists['obs'].SetName('data_obs')
    
#    if args.region == 'monoph':
#        limitFile = ROOT.TFile(config.histDir + "/"+args.region+".root", "RECREATE")
#        limitFile.cd()
#        
#        for name, hist in sorted(hists.iteritems()):
#            hist.Write()
    
    bkgTotal = 0.
    print 'Yields for ' + plotConfig.baseline + ' && ' + vardef.cut
    for group in reversed(plotConfig.bkgGroups):
        bkgTotal += counts[group.name]
        print '%+10s  %.2f' % (group.name, counts[group.name])
    
    print '---------------------'
    print '%+10s  %.2f' % ('bkg', bkgTotal)
    
    print '====================='
    
    if isSensitive:
        for sGroup in plotConfig.sigGroups:
            for sName in sGroup.samples:
                print '%+10s  %.2f' % (sName, counts[sName])
    
    print '====================='
    print '%+10s  %d' % ('obs', counts['obs'])
    
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
    
            print ('%+10s' % group.name), ' '.join(['%12.2f' % y for y in yields]), ('%12.2f' % sum(yields))
    
        print '------------------------------------------------------------------------------------'
        print ('%+10s' % 'total'), ' '.join(['%12.2f' % b for b in bkgTotal]), ('%12.2f' % sum(bkgTotal))
        print '===================================================================================='
        print ('%+10s' % 'obs'), ' '.join(['%12d' % int(round(obs.GetBinContent(iX)  * obs.GetXaxis().GetBinWidth(iX))) for iX in range(1, nBins + 1)]), ('%12d' % int(round(obs.Integral('width'))))
