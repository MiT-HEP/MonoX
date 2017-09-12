import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

outFile = ROOT.TFile.Open(basedir + '/data/ewk_corr.root', 'recreate')

wgbins = array.array('d', [40. * x for x in range(36)])
wghist = ROOT.TH1D('wnlg-130-o', ';p_{T}^{#gamma} (GeV);#delta_{EWK}', len(wgbins) - 1, wgbins)
wguphist = wghist.Clone('wnlg-130-o_Up')
wgdownhist = wghist.Clone('wnlg-130-o_Down')

with open(basedir + '/data/raw/ewk_corr_wg.dat') as source:
    for line in source:
        x, y = map(float, line.strip().split())

        iX = wghist.FindFixBin(x)
        wghist.SetBinContent(iX, 1. + y / 100.)
        wguphist.SetBinContent(iX, max(1., 1. + 2. * y / 100.))
        wgdownhist.SetBinContent(iX, min(1., 1. + 2. * y / 100.))

outFile.cd()
wghist.Write()
wguphist.Write()
wgdownhist.Write()

zgbins = array.array('d', [100.] + [120. + 40. * x for x in range(23)])
zghist = ROOT.TH1D('znng-130-o', ';p_{T}^{#gamma} (GeV);#delta_{EWK}', len(zgbins) - 1, zgbins)
zguphist = zghist.Clone('znng-130-o_Up')
zgdownhist = zghist.Clone('znng-130-o_Down')

with open(basedir + '/data/raw/ewk_corr_zg.dat') as source:
    for line in source:
        x, y = map(float, line.strip().split())

        iX = zghist.FindFixBin(x)
        zghist.SetBinContent(iX, 1. + y / 100.)
        zguphist.SetBinContent(iX, max(1., 1. + 2. * y / 100.))
        zgdownhist.SetBinContent(iX, min(1., 1. + 2. * y / 100.))

outFile.cd()
zghist.Write()
zguphist.Write()
zgdownhist.Write()

zgbins = array.array('d', [40. * x for x in range(26)])
zghist = ROOT.TH1D('zllg-130-o', ';p_{T}^{#gamma} (GeV);#delta_{EWK}', len(zgbins) - 1, zgbins)
zguphist = zghist.Clone('zllg-130-o_Up')
zgdownhist = zghist.Clone('zllg-130-o_Down')

with open(basedir + '/data/raw/ewk_corr_zllg.dat') as source:
    for line in source:
        x, y = map(float, line.strip().split())

        iX = zghist.FindFixBin(x)
        zghist.SetBinContent(iX, 1. + y / 100.)
        zguphist.SetBinContent(iX, max(1., 1. + 2. * y / 100.))
        zgdownhist.SetBinContent(iX, min(1., 1. + 2. * y / 100.))

outFile.cd()
zghist.Write()
zguphist.Write()
zgdownhist.Write()

zghist.Clone('zllg-300-o').Write()
zguphist.Clone('zllg-300-o_Up').Write()
zgdownhist.Clone('zllg-300-o_Down').Write()

outFile.Close()
