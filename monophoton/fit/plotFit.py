#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
import os
import re
import math

import parameters

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
from plotstyle import RatioCanvas
from main.plotconfig import getConfig

import ROOT

mlfit = ROOT.TFile.Open(sys.argv[1])
postfitDir = mlfit.Get('shapes_fit_b')

workspace = ROOT.TFile.Open(parameters.outname).Get('wspace')
x = workspace.arg('x')

for key in postfitDir.GetListOfKeys():
    region = key.GetName()

    prefitFile = ROOT.TFile.Open(parameters.sourcedir + '/' + region + '.root')
    prefitDir = prefitFile.Get(parameters.distribution)

    prefitTotal = prefitDir.Get('bkgtotal_syst')
    prefitTotal.Scale(1., 'width')
    prefitUnc = prefitTotal.Clone('prefitUnc')
    prefitRatio = prefitTotal.Clone('prefitRatio')
    prefitUncRatio = prefitTotal.Clone('prefitUncRatio')

    postfitTotal = postfitDir.Get(region + '/total_background')
    postfitUnc = postfitTotal.Clone('postfitUnc')
    postfitRatio = postfitTotal.Clone('postfitRatio')
    postfitUncRatio = postfitTotal.Clone('postfitUncRatio')

    dataHist = postfitTotal.Clone("dataHist")
    dataHist.Reset()

    data = postfitDir.Get(region + '/data')
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    for iBin in range(1, dataHist.GetNbinsX() + 1):
        width = dataHist.GetXaxis().GetBinWidth(iBin)

        data.GetPoint(iBin-1, x, y)
        ywidth = y * width
        yerr = math.sqrt(ywidth)

        dataHist.SetBinContent(iBin, ywidth)
        dataHist.SetBinError(iBin, yerr)

    obs = ROOT.RooHist(dataHist, 1.)
    obs.SetName('data_obs')

    dataHist.Scale(1., 'width')

    for iBin in range(1, prefitRatio.GetNbinsX()+1):
        data = dataHist.GetBinContent(iBin)
        if data == 0:
            data = 1
        dataerr = dataHist.GetBinError(iBin)
        if dataerr == 0:
            dataerr = 1

        prefitcontent = prefitUncRatio.GetBinContent(iBin)
        prefiterror = prefitUncRatio.GetBinError(iBin)
        prefitRatio.SetBinContent(iBin, data**2 / prefitcontent)
        prefitRatio.SetBinError(iBin, dataerr * data / prefitcontent) 
        prefitUncRatio.SetBinError(iBin, data * prefiterror / prefitcontent)
        prefitUncRatio.SetBinContent(iBin, data)

        postfitcontent = postfitUncRatio.GetBinContent(iBin)
        postfiterror = postfitUncRatio.GetBinError(iBin)
        postfitRatio.SetBinContent(iBin, data**2 / postfitcontent)
        postfitRatio.SetBinError(iBin, dataerr * data / postfitcontent) 
        postfitUncRatio.SetBinError(iBin, data * postfiterror / postfitcontent)
        postfitUncRatio.SetBinContent(iBin, data)

    floatNames = []

    allVars = workspace.allVars()
    vitr = allVars.iterator()
    while True:
        v = vitr.Next()
        if not v:
            break

        matches = re.match('mu_([^_]+)_' + region + '_bin[0-9]+', v.GetName())
        if matches and not v.isConstant():
            proc = matches.group(1)
            if proc not in floatNames:
                floatNames.append(proc)

        matches = re.match('([^_]+)_' + region + '_([^_]+)_([^_]+)_bin[0-9]+_tf', v.GetName())
        if matches:
            proc = matches.group(1)
            if proc not in floatNames:
                floatNames.append(proc)

            floatName = matches.group(1)

    if len(floatNames) != 0:
        postfitSub = postfitTotal.Clone('subdominant')
        for proc in floatNames:
            postfitSub.Add(postfitDir.Get(region + '/' + proc), -1.)
    else:
        postfitSub = None

    plotConfig = getConfig(region)
    
    lumi = 0.
    for sample in plotConfig.obs.samples:
        lumi += sample.lumi / plotConfig.prescales[sample]
    
    canvas = RatioCanvas(lumi = lumi, name = region)
    canvas.legend.setPosition(0.6, 0.6, 0.9, 0.9)
    canvas.legend.add('obs', title = 'Observed', opt = 'LP', color = ROOT.kBlack, mstyle = 8, msize = 0.8)
    canvas.legend.add('prefit', title = 'Prefit total', opt = 'LF', color = ROOT.kRed, lstyle = ROOT.kDashed, lwidth = 2, fstyle = 3004, mstyle = 8, msize = 0.8)
    if postfitSub:
        canvas.legend.add('subdom', title = 'Postfit subdominant', opt = 'F', fcolor = ROOT.kGray, fstyle = 1001)
    canvas.legend.add('postfit', title = 'Postfit total', opt = 'LF', color = ROOT.kBlue, lstyle = ROOT.kSolid, lwidth = 2, fstyle = 3005, mstyle = 8, msize = 0.8)

    obs.SetTitle('')
    prefitTotal.SetTitle('')
    postfitTotal.SetTitle('')
    if postfitSub:
        postfitSub.SetTitle('')

    canvas.legend.apply('obs', obs)
    canvas.legend.apply('prefit', prefitTotal, opt = 'L')
    canvas.legend.apply('prefit', prefitUnc, opt = 'F')
    canvas.legend.apply('prefit', prefitRatio, opt = 'LP')
    canvas.legend.apply('prefit', prefitUncRatio, opt = 'F')

    canvas.legend.apply('postfit', postfitTotal, opt = 'L')
    canvas.legend.apply('postfit', postfitUnc, opt = 'F')
    canvas.legend.apply('postfit', postfitRatio, opt = 'LP')
    canvas.legend.apply('postfit', postfitUncRatio, opt = 'F')
        
    if postfitSub:
        canvas.legend.apply('subdom', postfitSub)
    
    # reuse dataHist for unity line in ratio pad
    dataHist.SetLineColor(ROOT.kBlack)
    # dataHist.SetLineStyle(ROOT.kDashed)
    dataHist.SetLineWidth(2)

    iObs = canvas.addHistogram(obs)
    iPreUnc = canvas.addHistogram(prefitUnc, drawOpt = 'E2')
    iPre = canvas.addHistogram(prefitTotal, drawOpt = 'HIST')
    iPostUnc = canvas.addHistogram(postfitUnc, drawOpt = 'E2')
    iPost = canvas.addHistogram(postfitTotal, drawOpt = 'HIST')

    iLine = canvas.addHistogram(dataHist, drawOpt = 'HIST')
    iPreUncRatio = canvas.addHistogram(prefitUncRatio, drawOpt = 'E2')
    iPreRatio = canvas.addHistogram(prefitRatio, drawOpt = 'LP')
    iPostUncRatio = canvas.addHistogram(postfitUncRatio, drawOpt = 'E2')
    iPostRatio = canvas.addHistogram(postfitRatio, drawOpt = 'LP')
    

    if postfitSub:
        iSub = canvas.addHistogram(postfitSub)
        hList = [iSub, iPreUnc, iPre, iPostUnc, iPost, iObs]
    else:
        hList = [iPreUnc, iPre, iPostUnc, iPost, iObs]

    canvas.rlimits = (0.0, 2.0)
    canvas.xtitle = 'E_{T}^{#gamma} (GeV)'
    canvas.ytitle = 'Events / GeV'

    canvas.printWeb('monophoton/fit', region, hList = hList, rList = [iLine, iPreUncRatio, iPostUncRatio, iPreRatio, iPostRatio])
    canvas.Clear()

    dataHist.Delete()
    if postfitSub:
        postfitSub.Delete()
