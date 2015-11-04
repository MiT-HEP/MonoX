#! /usr/bin/env python                                                                                                                                                               
from ROOT import *
from array import array
from tdrStyle import *
#from pretty import plot_cms
setTDRStyle()

def makevariations(ch):

  infile = TFile("newscalefactors.root","READ")
  if ch is 'atoz':
    ratio = "znlo1_over_anlo1"
  else:
    ratio = "znlo012_over_wnlo012"
  
  infile.cd(ratio)
  
  #PDF
  h_ratio    = gDirectory.Get(ratio)
  h_pdf_up   = gDirectory.Get(ratio+"_pdfUp")
  h_pdf_down = gDirectory.Get(ratio+"_pdfDown")

  h_central = h_ratio.Clone(); h_central.SetName(ratio+"_central")
  h_central.Divide(h_ratio)

  h_ratio_pdf_up = h_pdf_up.Clone(); h_ratio_pdf_up.SetName(ratio+"_pdfUp")
  h_ratio_pdf_up.Divide(h_ratio);

  h_ratio_pdf_down = h_pdf_down.Clone(); h_ratio_pdf_down.SetName(ratio+"_pdfDown")  
  h_ratio_pdf_down.Divide(h_ratio);

  #Correlated scale
  h_scale_up   = gDirectory.Get(ratio+"_corrQCDUp")
  h_scale_down = gDirectory.Get(ratio+"_corrQCDDown") 

  h_ratio_scale_up = h_scale_up.Clone(); h_ratio_scale_up.SetName(ratio+"_CorrscaleUp")
  h_ratio_scale_up.Divide(h_ratio);

  h_ratio_scale_down = h_scale_down.Clone(); h_ratio_scale_down.SetName(ratio+"_CorrscaleDown")  
  h_ratio_scale_down.Divide(h_ratio);

  #Un-Correlated
  h_scale_up_uncor   = gDirectory.Get(ratio+"_uncorrQCDUp")
  h_scale_down_uncor = gDirectory.Get(ratio+"_uncorrQCDDown") 

  h_ratio_scale_up_uncor = h_scale_up_uncor.Clone(); h_ratio_scale_up_uncor.SetName(ratio+"_UnCorrscaleUp")
  h_ratio_scale_up_uncor.Divide(h_ratio);

  h_ratio_scale_down_uncor = h_scale_down_uncor.Clone(); h_ratio_scale_down_uncor.SetName(ratio+"_UnCorrscaleDown")  
  h_ratio_scale_down_uncor.Divide(h_ratio);

  # 80% Correlated
  h_ratio_scale_up_uncor80 = h_central.Clone(); h_ratio_scale_up_uncor80.SetName(ratio+"_UnCorr80scaleUp")
  for b in range(h_ratio_scale_up_uncor80.GetNbinsX()): 
    h_ratio_scale_up_uncor80.SetBinContent(b+1,h_ratio_scale_up_uncor.GetBinContent(b+1)*0.2 + h_ratio_scale_up.GetBinContent(b+1)*0.8)
    print b, h_ratio_scale_up_uncor.GetBinContent(b+1), h_ratio_scale_up.GetBinContent(b+1), h_ratio_scale_up_uncor80.GetBinContent(b+1)

  # 80% Correlated
  h_ratio_scale_down_uncor80 = h_central.Clone(); h_ratio_scale_down_uncor80.SetName(ratio+"_UnCorr80scaleDown")
  for b in range(h_ratio_scale_down_uncor80.GetNbinsX()): 
    h_ratio_scale_down_uncor80.SetBinContent(b+1,h_ratio_scale_down_uncor.GetBinContent(b+1)*0.2 + h_ratio_scale_down.GetBinContent(b+1)*0.8)
    print b, h_ratio_scale_down_uncor.GetBinContent(b+1), h_ratio_scale_down.GetBinContent(b+1), h_ratio_scale_down_uncor80.GetBinContent(b+1)


  f_out = TFile(ch+"_unc.root","recreate")
  f_out.cd()
  h_ratio.Write()
  h_central.Write()
  h_ratio_pdf_up.Write()
  h_ratio_pdf_down.Write()
  h_ratio_scale_up.Write()
  h_ratio_scale_down.Write()
  h_ratio_scale_up_uncor.Write()
  h_ratio_scale_down_uncor.Write()
  h_ratio_scale_up_uncor80.Write()
  h_ratio_scale_down_uncor80.Write()
  f_out.Close()

################################

#makevariations('atoz')
makevariations('wtoz')
