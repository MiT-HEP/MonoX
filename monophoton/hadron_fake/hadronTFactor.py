import sys
import os
import array
import math
import ROOT
import time

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas, RatioCanvas
from datasets import allsamples
import purity.selections as selections
import config

###########################
# Setup and configuration #
###########################

lumi = sphLumi = sum(allsamples[s].lumi for s in ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m'])
canvas = SimpleCanvas(lumi = lumi)
rcanvas = RatioCanvas(lumi = lumi)

binning = array.array('d', [175., 200., 250., 300., 350., 400., 450., 500.])
pid = 'medium'
era = 'Ashim_ZG_CWIso'

inputFile = ROOT.TFile.Open(basedir+'/data/impurity.root')
impurityGraph = inputFile.Get("barrel-" + pid + "-pixel-Met0to60")

outputFile = ROOT.TFile.Open(basedir+'/data/hadronTFactor.root', 'recreate')

baseSels = [
    'jets.pt_[0] > 100.',
    't1Met.pt < 60.',
    'photons.size == 1',
    'photons.isEB[0]',
    selections.hOverESels[era]['barrel'][pid],
    'photons.pixelVeto[0]',
    selections.monophIdCut,
    'photons.chIso[0] < 11.',
    selections.sieieSels[era]['barrel'][pid]
]

goodSels = [
    selections.chIsoSels[era]['barrel'][pid],
    selections.nhIsoSels[era]['barrel'][pid],
    selections.phIsoSels[era]['barrel'][pid]
]

nomSels = [
    '!' + selections.chIsoSels[era]['barrel'][pid],
    selections.nhIsoSels[era]['barrel'][pid],
    selections.phIsoSels[era]['barrel'][pid]
]

tightSels = [
    '!' + selections.chIsoSels[era]['barrel'][pid],
    selections.nhIsoSels['Spring16']['barrel']['loose'],
    selections.phIsoSels['Spring16']['barrel']['loose']
]

looseSels = [
    '!' + selections.chIsoSels[era]['barrel'][pid],
    selections.nhIsoSels['Spring16']['barrel']['tight'],
    selections.phIsoSels['Spring16']['barrel']['tight']
]

# selections concatenated with chVeto
configurations = [
    ('Nom', nomSels),
    ('Tight', tightSels),
    ('Loose', looseSels)
]

##############
# Quick skim #
##############

gtree = ROOT.TChain('events')
gtree.Add(config.skimDir + '/sph-16*_emjet.root')
gtree.SetBranchStatus("*", 0)
gtree.SetBranchStatus("photons*", 1)
gtree.SetBranchStatus("jets.pt_", 1)
gtree.SetBranchStatus("t1Met.pt", 1)

baseSel = ' && '.join(baseSels)

print 'Skimming gtree with base sel'
print baseSel

gtree.Draw('>>elist', baseSel, 'goff')
elist = ROOT.gDirectory.Get('elist')
gtree.SetEntryList(elist)

####################################################################
# Plot the good photon + jet distribution and scale it by impurity #
####################################################################

gname = 'gpt'
gpt = ROOT.TH1D(gname, ';p_{T} (GeV)', len(binning) - 1, binning)
gpt.Sumw2()

sel = ' && '.join(goodSel)

print 'drawing gtree using selection: '
print sel

start = time.time()
gtree.Draw('photons.scRawPt[0]>>'+gname, gtreeSel, 'goff')
gpt.Scale(1., 'width')
elapsed = time.time() - start
print 'done with gtree. took ' + str(elapsed) + ' seconds.'

fname = 'fpt'
fpt = gpt.Clone(fname)
fptUp = gpt.Clone(fname+'PurityUp')
fptDown = gpt.Clone(fname+'PurityDown')

for iX in range(1, fpt.GetNbinsX() + 1):
    cent = fpt.GetXaxis().GetBinCenter(iX)        

    xval = ROOT.Double(0)
    imp = ROOT.Double(0)
    err = 0

    for iP in range(0, impurityGraph.GetN()):
        impurityGraph.GetPoint(iP, xval, imp)
        err = impurityGraph.GetErrorY(iP)
        low = xval - impurityGraph.GetErrorXlow(iP)
        high = xval + impurityGraph.GetErrorXhigh(iP)
        print iP, low, high
        if cent > low and cent < high:
            break

    imp = imp / 100.
    err = err / 100.

    cont = fpt.GetBinContent(iX) * imp 
    stat = fpt.GetBinError(iX) * imp 
    syst = fpt.GetBinContent(iX) * err

    fpt.SetBinContent(iX, cont)
    fpt.SetBinError(iX, math.sqrt(stat * stat)) # + syst * syst))

    impUp = imp + err
    contUp = fptUp.GetBinContent(iX) * impUp 
    statUp = fptUp.GetBinError(iX) * impUp

    fptUp.SetBinContent(iX, contUp)
    fptUp.SetBinError(iX, math.sqrt(statUp * statUp)) # + syst * syst))

    impDown = imp - err
    contDown = fptDown.GetBinContent(iX) * impDown
    statDown = fptDown.GetBinError(iX) * impDown

    fptDown.SetBinContent(iX, contDown)
    fptDown.SetBinError(iX, math.sqrt(statDown * statDown)) # + syst * syst))

    print "Bin center: %.2f, imp: %.2f,  err: %.2f (%2.0f), up: %.2f, down %.2f" % (cent, imp*100, err*100, err/imp*100, impUp*100, impDown*100)

outputFile.cd()
gpt.Write()
fpt.Write()
fptUp.Write()
fptDown.Write()

#########################################################
# Comute the transfer factors for various proxy choices #
#########################################################

for confName, sels in configurations:
    hname = 'hpt'+confName
    hpt = ROOT.TH1D(hname, ';p_{T} (GeV)', len(binning) - 1, binning)
    hpt.Sumw2()

    sel = ' && '.join(sels)

    print 'drawing gtree using selection'
    print sel
    gtree.Draw('photons.scRawPt[0]>>'+hname, sel, 'goff')
    hpt.Scale(1., 'width')
    print 'done with gtree'

    tname = 'tfact'+confName
    tfact = fpt.Clone(tname)
    tfact.Divide(hpt)

    tfactUp = fptUp.Clone(tname+'PurityUp')
    tfactUp.Divide(hpt)

    tfactDown = fptDown.Clone(tname+'PurityDown')
    tfactDown.Divide(hpt)

    for iX in range(1, fpt.GetNbinsX() + 1):
        print "pt: %3.0f gjets: %10.1f, fake:     %10.1f, hadron: %10.1f, tfact:     %6.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fpt.GetBinContent(iX), 
                                                                                    hpt.GetBinContent(iX), tfact.GetBinContent(iX)*100)
        print "pt: %3.0f gjets: %10.1f, fakeUp:   %10.1f, hadron: %10.1f, tfactUp:   %6.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fptUp.GetBinContent(iX)
                                                                                        , hpt.GetBinContent(iX), tfactUp.GetBinContent(iX)*100)
        print "pt: %3.0f gjets: %10.1f, fakeDown: %10.1f, hadron: %10.1f, tfactDown: %6.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fptDown.GetBinContent(iX)
                                                                                        , hpt.GetBinContent(iX), tfactDown.GetBinContent(iX)*100)

    outputFile.cd()
    hpt.Write()
    tfact.Write()
    tfactUp.Write()
    tfactDown.Write()

    canvas.cd()
    canvas.Clear()
    canvas.legend.Clear()

    canvas.legend.add(gname, title = '#gamma + jet', lcolor = ROOT.kBlack, lwidth = 2)
    canvas.legend.add(fname, title = '#gamma + jet #times impurity', lcolor = ROOT.kRed, lwidth = 2)
    canvas.legend.add(fname+'Syst', title = 'impurity #pm 1#sigma', lcolor = ROOT.kRed, lwidth = 2, lstyle = ROOT.kDashed)
    canvas.legend.add(hname, title = 'EMobject + jet', lcolor = ROOT.kBlue, lwidth = 2)
    canvas.legend.setPosition(0.6, 0.7, 0.95, 0.9)

    canvas.legend.apply(gname, gpt)
    canvas.legend.apply(fname, fpt)
    canvas.legend.apply(fname+'Syst', fptUp)
    canvas.legend.apply(fname+'Syst', fptDown)
    canvas.legend.apply(hname, hpt)

    canvas.addHistogram(gpt, drawOpt = 'HIST')
    canvas.addHistogram(fpt, drawOpt = 'HIST')
    canvas.addHistogram(fptUp, drawOpt = 'HIST')
    canvas.addHistogram(fptDown, drawOpt = 'HIST')
    canvas.addHistogram(hpt, drawOpt = 'HIST')

    canvas.ylimits = (1.0, 2500000.)
    canvas.SetLogy(True)

    canvas.printWeb('monophoton/hadronTFactor', 'distributions'+confName)

    rcanvas.Clear()
    rcanvas.legend.Clear()

    # if samp == 'Down':
    rcanvas.ylimits = (0., -1.)
    # else:
    # rcanvas.ylimits = (0., 0.05)

    rcanvas.SetLogy(False)

    rcanvas.legend.add(tname, title = 'transfer factor', lcolor = ROOT.kBlack, lwidth = 2)
    rcanvas.legend.add(tname+'Syst', title = 'impurity #pm 1#sigma', lcolor = ROOT.kBlack, lwidth = 2, lstyle = ROOT.kDashed)

    rcanvas.legend.apply(tname, tfact)
    rcanvas.legend.apply(tname+'Syst', tfactUp)
    rcanvas.legend.apply(tname+'Syst', tfactDown)

    iNom = rcanvas.addHistogram(tfact, drawOpt = 'HIST')
    iUp = rcanvas.addHistogram(tfactUp, drawOpt = 'HIST')
    iDown = rcanvas.addHistogram(tfactDown, drawOpt = 'HIST')

    rcanvas.printWeb('monophoton/hadronTFactor', 'tfactor'+confName, hList = [iUp, iDown, iNom], rList = [iNom, iUp, iDown] )
