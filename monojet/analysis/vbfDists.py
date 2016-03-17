#! /usr/bin/python

from ROOT import TFile
#import cutsVBFVeto as cuts
import cuts
from CrombieTools import Nminus1Cut

inDir = '/Users/dabercro/GradSchool/Winter15/vbfFiles/'
outDir = 'plots/160317/'

if __name__ == '__main__':
    from CrombieTools.PlotTools.PlotHists import plotter

    vbfFile = TFile(inDir + 'monojet_VBFSignal.root')
    zvvFile = TFile(inDir + 'monojet_ZJetsToNuNu.root')
    qcdFile = TFile(inDir + 'monojet_QCD.root')
    
    plotter.AddTree(vbfFile.events)
    plotter.AddTree(zvvFile.events)
    plotter.AddTree(qcdFile.events)
    
    plotter.AddLegendEntry('VBF',1)
    plotter.AddLegendEntry('Zvv',2)
    plotter.AddLegendEntry('QCD',3)

    plotter.SetLumiLabel('2.30')
    plotter.SetIsCMSPrelim(True)
    plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)
    plotter.SetEventsPer(1.0)
    plotter.SetNormalizedHists(True)

    def MakePlot(args):
        holding = list(args)
        expr = args[0]
        holding[0] = outDir + 'VBFStudy_' + expr
        plotter.SetDefaultWeight(Nminus1Cut(cuts.cut('monoJet_inc','signal') + '*(' + cuts.METTrigger + ' * mcWeight * XSecWeight * puWeight * zkfactor * ewk_z)',expr))
        plotter.SetDefaultExpr(expr)
        plotter.MakeCanvas(*holding)

    MakePlot(['jot1Pt',40,0,1000,'Jet 1 p_{T} [GeV]','AU',True])
    MakePlot(['jot2Pt',40,0,1000,'Jet 2 p_{T} [GeV]','AU',True])
    MakePlot(['mjj',60,0,3000,'Di-jet Mass [GeV]','AU'])
    MakePlot(['jjDEta',40,0,10,'Di-jet #Delta#eta','AU'])
    MakePlot(['minJetMetDPhi_clean',20,0,4,'min #Delta#phi(j,MET)','AU'])
    MakePlot(['gen_jot1Pt',40,0,1000,'Jet 1 p_{T} [GeV]','AU',True])
    MakePlot(['gen_jot2Pt',40,0,1000,'Jet 2 p_{T} [GeV]','AU',True])
    MakePlot(['gen_mjj',60,0,3000,'Di-jet Mass [GeV]','AU'])
    MakePlot(['gen_jjDEta',40,0,10,'Di-jet #Delta#eta','AU'])
