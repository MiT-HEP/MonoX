import sys
import os
import array
import math
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas
from datasets import allsamples
import config

lumi = min(config.jsonLumi, allsamples['sph-16b2-d'].lumi + allsamples['sph-16c2-d'].lumi + allsamples['sph-16d2-d'].lumi)
canvas = SimpleCanvas(lumi = lumi)

binning = array.array('d', [175., 180., 185., 190., 200., 210., 230., 250., 300., 350., 400.])

inputFile = ROOT.TFile.Open(basedir+'/data/impurity.root')
impurityHist = inputFile.Get("FinalImpurity")

outputFile = ROOT.TFile.Open(basedir+'/data/hadronTFactor.root', 'recreate')

isos = [ ('Worst', '') ] # , ('JetPt', 'JetPt') ] # [ ( '', 'pv'), ('Worst', '') ]

baseSel = 't1Met.met < 60. && photons.size == 1 && photons.pixelVeto[0] && !(run > %s)' % config.runCutOff

samples = [ ('',  baseSel+' && (photons.sieie[0] > 0.012 || photons.chIso[0] > 1.37)')
            ,('Down', baseSel)
            ,('Up', baseSel)
            ]

for iso in isos:
    gtree = ROOT.TChain('events')
    gtree.Add(config.skimDir + '/sph-16*2-d_purity'+iso[1]+'.root')

    gname = 'gpt'+iso[0]
    gpt = ROOT.TH1D(gname, ';p_{T} (GeV)', len(binning) - 1, binning)
    gpt.Sumw2()

    gtree.Draw('photons.scRawPt[0]>>'+gname, baseSel+' && photons.medium[0]', 'goff')
    gpt.Scale(1., 'width')

    # inputFile = ROOT.TFile.Open(basedir+'/data/impurity'+iso[1]+'.root')
    # impurityHist = inputFile.Get("ChIso50to80imp")

    fname = 'fpt'+iso[0]
    fpt = gpt.Clone(fname)
    fptUp = gpt.Clone(fname+'PurityUp')
    fptDown = gpt.Clone(fname+'PurityDown')
    for iX in range(1, fpt.GetNbinsX() + 1):
        cent = fpt.GetXaxis().GetBinCenter(iX)
        bin = impurityHist.FindBin(cent)
        imp = impurityHist.GetBinContent(bin) / 100.
        err = impurityHist.GetBinError(bin) / 100.

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

    for samp, sel in samples:
        htree = ROOT.TChain('events')
        htree.Add(config.skimDir + '/sph-16*2-d_purity'+iso[1]+samp+'.root')

        hname = 'hpt'+iso[0]+samp
        hpt = ROOT.TH1D(hname, ';p_{T} (GeV)', len(binning) - 1, binning)
        hpt.Sumw2()

        # if iso[0] == 'Worst':
        sel = sel.replace('chIso', 'chWorstIso')
        htree.Draw('photons.scRawPt[0]>>'+hname, sel, 'goff')
        hpt.Scale(1., 'width')

        tname = 'tfact'+iso[0]+samp
        tfact = fpt.Clone(tname)
        tfact.Divide(hpt)

        tfactUp = fptUp.Clone(tname+'PurityUp')
        tfactUp.Divide(hpt)
        
        tfactDown = fptDown.Clone(tname+'PurityDown')
        tfactDown.Divide(hpt)

        for iX in range(1, fpt.GetNbinsX() + 1):
            print "pt: %3.0f gjets: %7.1f, fake:     %7.1f, hadron: %7.1f, tfact:     %4.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fpt.GetBinContent(iX), 
                                                                                        hpt.GetBinContent(iX), tfact.GetBinContent(iX)*100)
            print "pt: %3.0f gjets: %7.1f, fakeUp:   %7.1f, hadron: %7.1f, tfactUp:   %4.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fptUp.GetBinContent(iX)
                                                                                            , hpt.GetBinContent(iX), tfactUp.GetBinContent(iX)*100)
            print "pt: %3.0f gjets: %7.1f, fakeDown: %7.1f, hadron: %7.1f, tfactDown: %4.2f" % (fpt.GetBinLowEdge(iX), gpt.GetBinContent(iX), fptDown.GetBinContent(iX)
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

        canvas.ylimits = (0.1, 250000.)
        canvas.SetLogy(True)

        canvas.printWeb('monophoton/hadronTFactor', 'distributions'+iso[0]+samp)

        canvas.Clear()
        canvas.legend.Clear()

        if samp == 'Down':
            canvas.ylimits = (0., -1.)
        else:
            canvas.ylimits = (0., 0.15)
        
        canvas.SetLogy(False)

        canvas.legend.add(tname, title = 'transfer factor', lcolor = ROOT.kBlack, lwidth = 2)
        canvas.legend.add(tname+'Syst', title = 'impurity #pm 1#sigma', lcolor = ROOT.kBlack, lwidth = 2, lstyle = ROOT.kDashed)

        canvas.legend.apply(tname, tfact)
        canvas.legend.apply(tname+'Syst', tfactUp)
        canvas.legend.apply(tname+'Syst', tfactDown)

        canvas.addHistogram(tfact, drawOpt = 'HIST')
        canvas.addHistogram(tfactUp, drawOpt = 'HIST')
        canvas.addHistogram(tfactDown, drawOpt = 'HIST')

        canvas.printWeb('monophoton/hadronTFactor', 'tfactor'+iso[0]+samp)
