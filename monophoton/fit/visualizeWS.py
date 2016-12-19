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

source = ROOT.TFile.Open(args.sourcePath)
workspace = source.Get('wspace')

x = workspace.arg('x')

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('total', 'stat. + syst.', opt = 'F', color = ROOT.kOrange + 1, fstyle = 1001)
canvas.legend.add('stat', 'stat.', opt = 'L', color = ROOT.kBlack, mstyle = 8)

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
    logy = True
    
    hmods = {}

    for ibin in range(1, len(binning)):
        binName = pdf.GetName() + '_bin' + str(ibin)

        if not workspace.var('mu_' + binName) and not workspace.var('raw_' + binName):
            # raw is tf x another mu -> plot the TF

            if hnominal is None:
                hnominal = ROOT.TH1D(pdf.GetName() + '_tf', '', len(binning) - 1, binning)
                huncert = hnominal.Clone(pdf.GetName() + '_tf_uncertainties')
                logy = False

            tf = workspace.var(binName + '_tf')
            print tf.IsA().GetName()

            hnominal.SetBinContent(ibin, tf.getVal())
            huncert.SetBinContent(ibin, tf.getVal())

        else:
            if hnominal is None:
                hnominal = pdf.createHistogram(pdf.GetName(), x, ROOT.RooFit.Binning('default'))
                hnominal.SetName(pdf.GetName())
                huncert = hnominal.Clone(pdf.GetName() + '_uncertainties')

        unc = workspace.function('unc_' + binName)
        if not unc:
            continue

        totalUncert2 = 0.
        mods = unc.components()
        modItr = mods.iterator()
        while True:
            mod = modItr.Next()
            if not mod:
                break

            uncert2 = 0.
            
            # stat uncertainty of TFs have two parameters
            # allow for general case of N parameters
            iparam = 0
            p = mod.getParameter(iparam)
            while p:
                p.setVal(1.)
                d = (mod.getVal() - 1.) * hnominal.GetBinContent(ibin)
                p.setVal(0.)

                uncert2 += d * d

                iparam += 1
                p = mod.getParameter(iparam)

            if mod.GetName().endswith('_stat'):
                hnominal.SetBinError(ibin, math.sqrt(uncert2))
            else:
                uncertName = mod.GetName().replace('mod_' + binName + '_', '')
                if uncertName not in hmods:
                    hmods[uncertName] = ROOT.TH1D(pdf.GetName() + '_' + uncertName, '', len(binning) - 1, binning)

                hmods[uncertName].SetBinContent(ibin, math.sqrt(uncert2))
                
            # total uncertainty includes stat
            totalUncert2 += uncert2

        huncert.SetBinError(ibin, math.sqrt(totalUncert2))

    outputFile.cd()
    hnominal.SetDirectory(outputFile)
    hnominal.Write()
    huncert.SetDirectory(outputFile)
    huncert.Write()
    for h in hmods.values():
        h.SetDirectory(outputFile)
        h.Write()

    canvas.legend.apply('total', huncert)
    canvas.legend.apply('stat', hnominal)

    huncert.GetXaxis().SetTitle(xtitle)

    canvas.Clear()
    canvas.addHistogram(huncert, drawOpt = 'E2')
    canvas.addHistogram(hnominal, drawOpt = 'EP')
    canvas.printWeb(plotDir, hnominal.GetName(), logy = logy)

