import sys
import os
import array
import math
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Visualize the workspace content')
argParser.add_argument('sourcePath', metavar = 'PATH', help = 'Workspace ROOT file.')

plotDir = 'workspace'
outputFileName = 'workspace_plots.root'
xtitle = 'p_{T}^{#gamma} (GeV)'

args = argParser.parse_args()
sys.argv = []

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas

import ROOT

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

def modRelUncert2(mod):
    # stat uncertainty of TFs have two parameters
    # allow for general case of N parameters
    relUncert2 = 0.
    iparam = 0
    p = mod.getParameter(iparam)
    while p:
        p.setVal(1.)
        d = mod.getVal() - 1.
        p.setVal(0.)

        relUncert2 += d * d

        iparam += 1
        p = mod.getParameter(iparam)

    return relUncert2

source = ROOT.TFile.Open(args.sourcePath)
workspace = source.Get('wspace')

x = workspace.arg('x')

canvas1 = SimpleCanvas(name = 'canvas1')
canvas1.legend.setPosition(0.7, 0.7, 0.9, 0.9)
# a very ugly hack - somehow cannot plot two types (with and without uncertainty) of plots..
canvas2 = SimpleCanvas(name = 'canvas2')

canvas1.legend.add('total', 'stat. + syst.', opt = 'F', color = ROOT.kOrange + 1, fstyle = 1001)
canvas1.legend.add('stat', 'stat.', opt = 'L', color = ROOT.kBlack, mstyle = 8)

outputFile = ROOT.TFile.Open(outputFileName, 'recreate')

xbinning = x.getBinning('default')
boundaries = xbinning.array()
binning = array.array('d', [boundaries[i] for i in range(xbinning.numBoundaries())])

allPdfs = workspace.allPdfs()

pdfItr = allPdfs.iterator()
while True:
    pdf = pdfItr.Next()
    if not pdf:
        break

    hnominal = None
    huncert = None
    isTF = False
    
    hmods = {}
    normMods = {}

    unc = workspace.function('unc_' + pdf.GetName() + '_norm')
    if unc:
        # normalization given to this PDF has associated uncertainties

        # loop over all modifiers
        mods = unc.components()
        modItr = mods.iterator()
        while True:
            mod = modItr.Next()
            if not mod:
                break

            uncertName = mod.GetName().replace('mod_' + pdf.GetName() + '_norm_', '')
            normMods[uncertName] = mod
            hmods[uncertName] = ROOT.TH1D(pdf.GetName() + '_' + uncertName, '', len(binning) - 1, binning)

    for ibin in range(1, len(binning)):
        binName = pdf.GetName() + '_bin' + str(ibin)

        # if mu is a RooRealVar -> simplest case; static PDF
        # if mu = raw x unc and raw is a RooRealVar -> dynamic PDF, not linked
        # if mu = raw x unc and raw is a function -> linked from another sample

        if not workspace.var('mu_' + binName) and not workspace.var('raw_' + binName):
            # raw is tf x another mu -> plot the TF

            if hnominal is None:
                hnominal = ROOT.TH1D('tf_' + pdf.GetName(), ';' + xtitle, len(binning) - 1, binning)
                huncert = hnominal.Clone(hnominal.GetName() + '_uncertainties')
                isTF = True

            tf = workspace.var(binName + '_tf')
            val = tf.getVal()

            # TF is historically plotted inverted
            hnominal.SetBinContent(ibin, 1. / val)
            huncert.SetBinContent(ibin, 1. / val)

        else:
            if hnominal is None:
                hnominal = pdf.createHistogram(pdf.GetName(), x, ROOT.RooFit.Binning('default'))
                for iX in range(1, hnominal.GetNbinsX() + 1):
                    hnominal.SetBinError(iX, 0.)

                hnominal.SetName(pdf.GetName())
                hnominal.GetXaxis().SetTitle(xtitle)
                huncert = hnominal.Clone(pdf.GetName() + '_uncertainties')

            val = hnominal.GetBinContent(ibin)

        totalUncert2 = 0.

        for uncertName, mod in normMods.items():
            uncert2 = modRelUncert2(mod) * val
            hmods[uncertName].SetBinContent(ibin, math.sqrt(uncert2))

            totalUncert2 += uncert2

        unc = workspace.function('unc_' + binName)
        if unc:
            # loop over all modifiers for this bin
            mods = unc.components()
            modItr = mods.iterator()
            while True:
                mod = modItr.Next()
                if not mod:
                    break
    
                uncert2 = modRelUncert2(mod) * val
    
                if mod.GetName().endswith('_stat'):
                    if isTF: # nominal is 1/value
                        hnominal.SetBinError(ibin, math.sqrt(uncert2) / val / val)
                    else:
                        hnominal.SetBinError(ibin, math.sqrt(uncert2))
                else:
                    uncertName = mod.GetName().replace('mod_' + binName + '_', '')
                    if uncertName not in hmods:
                        hmods[uncertName] = ROOT.TH1D(pdf.GetName() + '_' + uncertName, '', len(binning) - 1, binning)
    
                    hmods[uncertName].SetBinContent(ibin, math.sqrt(uncert2))
                    
                # total uncertainty includes stat
                totalUncert2 += uncert2
    
        if isTF:
            huncert.SetBinError(ibin, math.sqrt(totalUncert2) / val / val)
        else:
            huncert.SetBinError(ibin, math.sqrt(totalUncert2))

    hasUncert = sum(huncert.GetBinError(iX) for iX in range(1, huncert.GetNbinsX() + 1)) != 0.

    outputFile.cd()
    hnominal.SetDirectory(outputFile)
    hnominal.Write()
    if hasUncert:
        huncert.SetDirectory(outputFile)
        huncert.Write()
    for h in hmods.values():
        h.SetDirectory(outputFile)
        h.Write()

    canvas1.legend.apply('stat', hnominal)

    if hasUncert:
        canvas1.Clear()
        canvas1.legend.apply('total', huncert)

        canvas1.addHistogram(huncert, drawOpt = 'E2')
        canvas1.addHistogram(hnominal, drawOpt = 'EP')
        canvas1.printWeb(plotDir, hnominal.GetName(), logy = not isTF)
    else:
        canvas2.Clear()
        canvas2.addHistogram(hnominal, drawOpt = 'EP')
        canvas2.printWeb(plotDir, hnominal.GetName(), logy = not isTF)
