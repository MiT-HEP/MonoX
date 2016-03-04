import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

outFile = ROOT.TFile.Open(basedir + '/data/ewk_corr.root', 'recreate')

wgbins = array.array('d', [40. * x for x in range(36)])
wghist = ROOT.TH1D('wnlg-130', ';p_{T}^{#gamma} (GeV);#delta_{EWK}', len(wgbins) - 1, wgbins)
wguphist = wghist.Clone('wnlg-130_Up')
wgdownhist = wghist.Clone('wnlg-130_Down')

with open(basedir + '/data/ewk_corr_wg.dat') as source:
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
wghist.Clone('wg').Write()
wguphist.Clone('wg_Up').Write()
wgdownhist.Clone('wg_Down').Write()

zgbins = array.array('d', [100.] + [120. + 40. * x for x in range(23)])
zghist = ROOT.TH1D('znng-130', ';p_{T}^{#gamma} (GeV);#delta_{EWK}', len(zgbins) - 1, zgbins)
zguphist = zghist.Clone('znng-130_Up')
zgdownhist = zghist.Clone('znng-130_Down')

with open(basedir + '/data/ewk_corr_zg.dat') as source:
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
zghist.Clone('zg').Write()
zguphist.Clone('zg_Up').Write()
zgdownhist.Clone('zg_Down').Write()

outFile.Close()
