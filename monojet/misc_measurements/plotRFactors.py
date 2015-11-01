from ROOT import *
from array import array
from tdrStyle import *
setTDRStyle()

def plotRFactors(process):

  f = TFile('mono-x.root','READ')

  if (process=='zjets'):
    num = f.Get("category_monojet/signal_zjets")
    den = f.Get("category_monojet/Zmm_zll")
    label = "R_{Z}"
  elif (process=='gjets'):
    num = f.Get("category_monojet/signal_zjets")
    den = f.Get("category_monojet/gjets_gjets")
    label = "R_{#gamma}"
  elif (process=='wjets'):
    num = f.Get("category_monojet/signal_wjets")
    den = f.Get("category_monojet/Wmn_wjets")
    label = "R_{W}"

  ratio = num.Clone("ratio")
  ratio.Divide(den)
            
  gStyle.SetOptStat(0)

  c = TCanvas("c","c",1000,800)  
  c.SetTopMargin(0.06)
  c.cd()
  c.SetRightMargin(0.04)
  c.SetTopMargin(0.07)
  c.SetLeftMargin(0.12)


  dummy = den.Clone("dummy")
  for i in range(1,dummy.GetNbinsX()):
    dummy.SetBinContent(i,0.01)
  dummy.SetFillColor(0)
  dummy.SetLineColor(0)
  dummy.SetLineWidth(0)
  dummy.SetMarkerSize(0)
  dummy.SetMarkerColor(0) 
  dummy.GetYaxis().SetTitle(label)
  dummy.GetYaxis().SetTitleSize(0.4*c.GetLeftMargin())
  dummy.GetXaxis().SetTitle("U [GeV]")
  dummy.GetXaxis().SetTitleSize(0.4*c.GetBottomMargin())
  dummy.SetMaximum(2.0*ratio.GetMaximum())
  dummy.SetMinimum(0.1*ratio.GetMinimum())
  dummy.GetYaxis().SetTitleOffset(1.15)
  dummy.Draw()

  ratio.SetLineColor(1)
  ratio.SetLineWidth(2)
  ratio.Draw("ehistsame")

  
  latex2 = TLatex()
  latex2.SetNDC()
  latex2.SetTextSize(0.5*c.GetTopMargin())
  latex2.SetTextFont(42)
  latex2.SetTextAlign(31) # align right
  latex2.DrawLatex(0.9, 0.94,"13 TeV")
  latex2.SetTextSize(0.8*c.GetTopMargin())
  latex2.SetTextFont(62)
  latex2.SetTextAlign(11) # align right
  latex2.DrawLatex(0.19, 0.85, "CMS")
  latex2.SetTextSize(0.7*c.GetTopMargin())
  latex2.SetTextFont(52)
  latex2.SetTextAlign(11)
  latex2.DrawLatex(0.19, 0.80, "Preliminary")          

  gPad.RedrawAxis()

  c.SaveAs("rfactor_"+process+".pdf")
  c.SaveAs("rfactor_"+process+".png")
  c.SaveAs("rfactor_"+process+".C")

  del c
  
#plotRFactors("zjets")
plotRFactors("gjets")
#plotRFactors("wjets")
