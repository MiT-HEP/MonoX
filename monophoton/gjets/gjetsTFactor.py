import sys
import os
import array
import math
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas, RatioCanvas, DataMCCanvas
import config

canvas = DataMCCanvas(lumi = 2239.9)

binning = array.array('d', [0. + 10. * x for x in range(13)]) 
outputFile = ROOT.TFile.Open(basedir+'/data/gjetsTFactor.root', 'recreate')

dtree = ROOT.TChain('events')
dtree.Add(config.skimDir + '/sph-d*_monoph.root')

btree = ROOT.TChain('events')
btree.Add(config.skimDir + '/sph-d*_hfakeWorst.root')
btree.Add(config.skimDir + '/sph-d*_efake.root')

bmctree = ROOT.TChain('events')
bmctree.Add(config.skimDir + '/znng-130_monoph.root')
bmctree.Add(config.skimDir + '/wnlg-130_monoph.root')
bmctree.Add(config.skimDir + '/wlnu-*_monoph.root')
bmctree.Add(config.skimDir + '/ttg_monoph.root')
bmctree.Add(config.skimDir + '/zllg-130_monoph.root')

mctree = ROOT.TChain('events')
mctree.Add(config.skimDir + '/g-40_monoph.root')
mctree.Add(config.skimDir + '/g-100_monoph.root')
mctree.Add(config.skimDir + '/g-200_monoph.root')
mctree.Add(config.skimDir + '/g-400_monoph.root')
mctree.Add(config.skimDir + '/g-600_monoph.root')

regions = [ ( 'Low', '(photons.pt[0] > 175. && !t1Met.iso)')
            ,('High', '(photons.pt[0] > 175. && t1Met.iso)') 
            ] 

dmets = []
bmets = []
gmets = []
mcmets = []

for region, sel in regions:
    dname = 'dmet'+region
    dmet = ROOT.TH1D(dname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    dmet.SetMinimum(0.02)
    dmet.SetMaximum(3000.)
    dmet.Sumw2()
    dtree.Draw('t1Met.met>>'+dname, sel, 'goff')

    bname = 'bmet'+region
    bmet = ROOT.TH1D(bname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmet.SetMinimum(0.02)
    bmet.SetMaximum(3000.)
    bmet.Sumw2()
    btree.Draw('t1Met.met>>'+bname, 'weight * '+sel, 'goff')

    bmcmet = ROOT.TH1D(bname+'MC', ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmcmet.Sumw2()
    bmctree.Draw('t1Met.met>>'+bname, '2239.9 * weight * '+sel, 'goff')
    bmet.Add(bmcmet)

    gname ='gmet'+region
    gmet = dmet.Clone(gname)
    gmet.Add(bmet, -1)

    mcname = 'mcmet'+region
    mcmet = ROOT.TH1D(mcname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    mcmet.SetMinimum(0.02)
    mcmet.SetMaximum(3000.)
    mcmet.Sumw2()
    mctree.Draw('t1Met.met>>'+mcname, '2239.9 * weight * '+sel, 'goff')
    
    dmet.Scale(1., 'width')
    bmet.Scale(1., 'width')
    gmet.Scale(1., 'width')
    mcmet.Scale(1., 'width')

    outputFile.cd()
    dmet.Write()
    bmet.Write()
    gmet.Write()
    mcmet.Write()

    dmets.append(dmet)
    bmets.append(bmet)
    gmets.append(gmet)
    mcmets.append(mcmet)

    canvas.cd()
    canvas.ylimits = (0.2, 2000.)
    canvas.Clear()
    canvas.legend.Clear()

    canvas.ylimits = (0.2, 2000.)
    canvas.SetLogy(True)

    canvas.legend.setPosition(0.6, 0.7, 0.95, 0.9)

    canvas.addStacked(bmet, title = 'Background', color = ROOT.TColor.GetColor(0x55, 0x44, 0xff), idx = -1)

    canvas.addStacked(mcmet, title = '#gamma + jet MC', color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc), idx = -1)

    canvas.addObs(dmet, title = 'Data')

    canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
    canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()

    canvas.Update(logy = True, ymax = 2000.)

    canvas.printWeb('monophoton/gjetTFactor', 'distributions'+region)

methods = [ ('Data', gmets), ('MC', mcmets) ]
scanvas = SimpleCanvas(lumi = 2239.9)

tfacts = []

for method, hists in methods:
    tname = 'tfact'+method
    tfact = hists[1].Clone(tname)
    tfact.Divide(hists[0])
    tfact.GetYaxis().SetTitle("")

    outputFile.cd()
    tfact.Write()
    tfacts.append(tfact)

    scanvas.Clear()
    scanvas.legend.Clear()

    scanvas.ylimits = (0., 1.)
    scanvas.SetLogy(False)

    scanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    scanvas.legend.add(tname, title = 'Transfer factor', lcolor = ROOT.kBlack, lwidth = 1)

    scanvas.legend.apply(tname, tfact)

    scanvas.addHistogram(tfact, drawOpt = 'EP')

    scanvas.printWeb('monophoton/gjetTFactor', 'tfactor'+method)

canvas.Clear()
canvas.legend.Clear()

canvas.ylimits = (0., 1.)
canvas.SetLogy(False)

canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

canvas.addObs(tfacts[0], 'Data')
canvas.addSignal(tfacts[1], title = 'MC', color = ROOT.kRed, idx = -1)
canvas.addStacked(tfacts[1], title = 'MC', idx = -1)

canvas.printWeb('monophoton/gjetTFactor', 'tfactorRatio')
