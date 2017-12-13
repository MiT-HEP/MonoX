import sys
import os
import math

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

import ROOT
from datasets import allsamples

file1 = ROOT.TFile("../data/muo_muon_idsf_2016_bcdef.root")
file2 = ROOT.TFile("../data/muo_muon_idsf_2016_gh.root")

lumi1 = sum(s.lumi for s in allsamples.getmany("sph-16{b,c,d,e,f}-m"))
lumi2 = sum(s.lumi for s in allsamples.getmany("sph-16{g,h}-m"))

lids = ['Loose', 'Tight']

outfile = ROOT.TFile("../data/muo_muon_idsf_2016.root", "RECREATE")

unc = 0.01

for lid in lids:

    folder = "MC_NUM_" + lid + "ID_DEN_genTracks_PAR_pt_eta"
    axes = "pt_abseta"

    sfhistname = folder + "/" + axes + "_ratio"
    sfhist1 = file1.Get(sfhistname)
    sfhist2 = file2.Get(sfhistname)

    datahist1 = file1.Get(folder + "/efficienciesDATA/" + axes + "_DATA")
    datahist2 = file2.Get(folder + "/efficienciesDATA/" + axes + "_DATA")

    mchist1 = file1.Get(folder + "/efficienciesMC/" + axes + "_MC")
    mchist2 = file2.Get(folder + "/efficienciesMC/" + axes + "_MC")

    sfhist = sfhist1.Clone(lid + "_ScaleFactor")
    vsfhist = sfhist1.Clone(lid + "Veto_ScaleFactor")

    for ybin in range(1, sfhist1.GetNbinsY() + 1):
        for xbin in range(1, sfhist1.GetNbinsX() + 1):
            # print xbin, ybin
            
            sf1 = sfhist1.GetBinContent(xbin, ybin)
            sf2 = sfhist2.GetBinContent(xbin, ybin)

            data1 = datahist1.GetBinContent(xbin, ybin)
            data2 = datahist2.GetBinContent(xbin, ybin)

            mc1 = mchist1.GetBinContent(xbin, ybin)
            mc2 = mchist2.GetBinContent(xbin, ybin)

            sf = (lumi1 * sf1 + lumi2 * sf2) / (lumi1 + lumi2)
            data = (lumi1 * data1 + lumi2 * data2) / (lumi1 + lumi2)
            mc = (lumi1 * mc1 + lumi2 * mc2) / (lumi1 + lumi2)

            # print data, mc 

            vsf = (1. - data) / (1. - mc)
            if (1. - data) > 0.:
                vsfunc = math.sqrt( (unc / (1. - data))**2 + (unc / (1. - mc))**2)
            else:
                vsfunc = 0.

            sfhist.SetBinContent(xbin, ybin, sf)
            sfhist.SetBinError(xbin, ybin, unc)

            vsfhist.SetBinContent(xbin, ybin, vsf)
            vsfhist.SetBinError(xbin, ybin, vsfunc)

            # print sf, vsf, vsfunc

    outfile.cd()
    sfhist.Write()
    vsfhist.Write()

file1.Close()
file2.Close()
outfile.Close()

infile = ROOT.TFile("../data/egamma_electron_loose_SF_2016.root")
outfile = ROOT.TFile("../data/egamma_electron_veto_SF_2016.root", "RECREATE")

datahist = infile.Get("EGamma_EffData2D")
mchist = infile.Get("EGamma_EffMC2D")

vsfhist = datahist.Clone("EGamma_VetoSF2D")

unc = 0.05

for ybin in range(1, datahist.GetNbinsY() + 1):
    for xbin in range(1, datahist.GetNbinsX() + 1):
        print xbin, ybin
        data = datahist.GetBinContent(xbin, ybin)
        mc = mchist.GetBinContent(xbin, ybin)

        print data, mc 

        vsf = (1. - data) / (1. - mc)
        if (1. - data) > 0.:
            vsfunc = math.sqrt( (unc / (1. - data))**2 + (unc / (1. - mc))**2)
        else:
            vsfunc = 0.

        vsfhist.SetBinContent(xbin, ybin, vsf)
        vsfhist.SetBinError(xbin, ybin, vsfunc)

        print data/mc, vsf, vsfunc

outfile.cd()
vsfhist.Write()

infile.Close()
outfile.Close()
