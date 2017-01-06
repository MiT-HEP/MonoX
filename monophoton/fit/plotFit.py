#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
import os
import re

import parameters

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
from plotstyle import RatioCanvas
from main.plotconfig import getConfig

import ROOT

mlfit = ROOT.TFile.Open(sys.argv[1])
prefitDir = mlfit.Get('shapes_prefit')
postfitDir = mlfit.Get('shapes_fit_b')

workspace = ROOT.TFile.Open(parameters.outname).Get('wspace')
x = workspace.arg('x')

for key in prefitDir.GetListOfKeys():
    region = key.GetName()

    prefitTotal = prefitDir.Get(region + '/total_background')
    prefitUnc = prefitTotal.Clone('prefitUnc')
    postfitTotal = postfitDir.Get(region + '/total_background')
    postfitUnc = postfitTotal.Clone('postfitUnc')

    dataHist = prefitTotal.Clone('dataHist')
    dataHist.Reset()

    data = workspace.data('data_obs_' + region)
    for iBin in range(1, dataHist.GetNbinsX() + 1):
        center = dataHist.GetXaxis().GetBinCenter(iBin)
        x.setVal(center)
        cont = int(data.weight(ROOT.RooArgSet(x)))
        for _ in xrange(cont):
            dataHist.Fill(center)

    obs = ROOT.RooHist(dataHist, 1.)
    obs.SetName('data_obs')

    dataHist.Scale(1., 'width')

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

        matches = re.match('([^_]+)_' + region + '_bin[0-9]+_tf', v.GetName())
        if matches:
            proc = matches.group(1)
            if proc not in floatNames:
                floatNames.append(proc)

            floatName = matches.group(1)

    if len(floatNames) != 0:
        prefitSub = prefitTotal.Clone('subdominant')
        for proc in floatNames:
            prefitSub.Add(prefitDir.Get(region + '/' + proc), -1.)
    else:
        prefitSub = None

    plotConfig = getConfig(region)
    
    lumi = 0.
    for sName in plotConfig.obs.samples:
        lumi += allsamples[sName].lumi / plotConfig.prescales[sName]
    
    canvas = RatioCanvas(lumi = lumi, name = region)
    canvas.legend.setPosition(0.6, 0.6, 0.9, 0.9)
    canvas.legend.add('obs', title = 'Observed', opt = 'LP', color = ROOT.kBlack, mstyle = 8, msize = 0.8)
    canvas.legend.add('prefit', title = 'Prefit total', opt = 'LF', color = ROOT.kRed, lstyle = ROOT.kDashed, lwidth = 2, fstyle = 3003)
    if prefitSub:
        canvas.legend.add('subdom', title = 'Prefit subdominant', opt = 'F', fcolor = ROOT.kGray, fstyle = 1001)
    canvas.legend.add('postfit', title = 'Postfit total', opt = 'LF', color = ROOT.kBlue, lstyle = ROOT.kSolid, lwidth = 2, fstyle = 3003)

    obs.SetTitle('')
    prefitTotal.SetTitle('')
    postfitTotal.SetTitle('')
    if prefitSub:
        prefitSub.SetTitle('')

    canvas.legend.apply('obs', obs)
    canvas.legend.apply('prefit', prefitTotal, opt = 'L')
    canvas.legend.apply('prefit', prefitUnc, opt = 'F')
    canvas.legend.apply('postfit', postfitTotal, opt = 'L')
    canvas.legend.apply('postfit', postfitUnc, opt = 'F')
    if prefitSub:
        canvas.legend.apply('subdom', prefitSub)
    
    # reuse dataHist for unity line in ratio pad
    dataHist.SetLineColor(ROOT.kBlack)
    dataHist.SetLineStyle(ROOT.kDashed)
    dataHist.SetLineWidth(2)

    iObs = canvas.addHistogram(obs)
    iPreUnc = canvas.addHistogram(prefitUnc, drawOpt = 'E2')
    iPre = canvas.addHistogram(prefitTotal, drawOpt = 'HIST')
    iPostUnc = canvas.addHistogram(postfitUnc, drawOpt = 'E2')
    iPost = canvas.addHistogram(postfitTotal, drawOpt = 'HIST')
    iLine = canvas.addHistogram(dataHist, drawOpt = 'HIST')
    if prefitSub:
        iSub = canvas.addHistogram(prefitSub)
        hList = [iSub, iPreUnc, iPre, iPostUnc, iPost, iObs]
    else:
        hList = [iPreUnc, iPre, iPostUnc, iPost, iObs]

    canvas.rlimits = (0.5, 1.5)

    canvas.printWeb('monophoton/fit', region, hList = hList, rList = [iLine, iPreUnc, iPre, iPostUnc, iPost])
    canvas.Clear()

    dataHist.Delete()
    if prefitSub:
        prefitSub.Delete()
