#! /usr/bin/env python                                                                                                                                                               
from ROOT import *
from array import array
from tdrStyle import *
from gjets import *
from pretty import plot_cms
setTDRStyle()

def makevariations():

  bin = 9; low = 100; high = 1000;

  h_lo = TH1D('h_lo', 'h_lo',bin,low,high)
  h_lo.Sumw2()
  
  Variables = {}
  f  = {}
  h1 = {}

  for Type in ordered_physics_processes:
    print Type
    histName = Type
    Variables[Type] = TH1F(histName, histName, bin, low, high)
    Variables[Type].Sumw2()

    f[Type] = ROOT.TFile(physics_processes[Type]['files'][0],"read")
    h1[Type] = f[Type].Get("htotal")
    total = h1[Type].GetBinContent(1)
    f[Type].Close()

    scale = physics_processes[Type]['xsec']/total
    makeTrees(Type,'events').Draw("genBos_pt >> " + histName," (genBos_PdgId == 22  && (abs(genBos_eta) < 1.5))* mcWeight","goff")
    Variables[Type].Scale(scale)
    h_lo.Add(Variables[Type])

  nlo_file = TFile("eos/cms/store/user/zdemirag/privateGen/A_13TeV_v2.root","READ");
  h_nlo    = TH1F("h_nlo", "h_nlo", bin, low, high)
  h_nlo.Sumw2()
  h_int    = TH1F("h_int", "h_int", bin, -5000, 5000)
  nlo_tree = nlo_file.Get("Events")
  nlo_tree.Draw("dm_pt>>h_int","effweight","goff")
  total = h_int.Integral()
  print total
  nlo_tree.Draw("dm_pt >> h_nlo","effweight*mcweight*(abs(dm_eta) < 1.5)","goff")
  h_nlo.Scale(1./total)
  h_nlo.SetLineColor(2)
  h_lo.SetLineColor(4)

  # Add Legend
  legend = TLegend(.60,.60,.92,.92)
  legend . AddEntry(h_lo,"LO","l")
  legend . AddEntry(h_nlo,"NLO","l")

  c4 = TCanvas("c4","c4", 900, 1000)
  c4.SetBottomMargin(0.3)
  c4.SetRightMargin(0.06)
  c4.SetLogy()
  
  h_nlo.Draw();
  h_nlo.GetYaxis().SetTitle('Events')
  h_nlo.GetYaxis().CenterTitle()
  h_nlo.GetYaxis().SetTitleOffset(1.2)
  h_nlo.GetXaxis().SetLabelSize(0)
  h_nlo.GetXaxis().SetTitle('')

  h_lo.Draw("same");

  legend.SetShadowColor(0);
  legend.SetFillColor(0);
  legend.SetLineColor(0);

  legend.Draw("same")
  plot_cms(True,lumi)
  
  Pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 1.0)
  Pad.SetTopMargin(0.7)
  Pad.SetFillColor(0)
  Pad.SetGridy(1)
  Pad.SetFillStyle(0)
  Pad.Draw()
  Pad.cd(0)
  Pad.SetRightMargin(0.06)
  
  Pull = h_nlo.Clone("Pull")
  Pull.GetXaxis().SetTitle("Gen Boson Pt")
  Pull.GetYaxis().SetTitleOffset(1.2)
  Pull.GetYaxis().SetTitleSize(0.04)
  Pull.GetYaxis().SetNdivisions(5)
  Pull.GetYaxis().SetLabelSize(0.02)
  Pull.GetXaxis().SetLabelSize(0.04)
  Pull.SetMarkerStyle(20)
  Pull.SetMarkerSize(0.8)
  Pull.Divide(h_lo)
  Pull.SetMaximum(3)
  Pull.SetMinimum(1)
  Pull.GetYaxis().SetTitle('kfactor')
  Pull.SetMarkerColor(1)
  Pull.SetLineColor(1)
  Pull.Draw("e")
  
  c4.SaveAs("gjets_kfactor.pdf")
  c4.SaveAs("gjets_kfactor.png")
  c4.SaveAs("gjets_kfactor.C")

################################

makevariations()
