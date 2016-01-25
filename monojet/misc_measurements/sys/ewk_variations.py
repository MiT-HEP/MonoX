#! /usr/bin/env python                                                                                                                                                               
from ROOT import *
from array import array
from tdrStyle import *
import math
#from pretty import plot_cms
setTDRStyle()

def makevariations(ch):

  infile = TFile("newscalefactors.root","READ")

  if ch is 'atoz':
    central   = "a_ewkcorr"
  if ch is 'wtoz':
    central   = "w_ewkcorr"
  
  central_z = "z_ewkcorr"
  infile.cd(central_z)

  #Central Value for Z
  h_central_z  = gDirectory.Get(central_z)
  h_ewk_z_up   = gDirectory.Get(central_z+"Up")
  h_ewk_z_down = gDirectory.Get(central_z+"Down")

  h_relative_up_z   = h_ewk_z_up.Clone(); h_relative_up_z.SetName(central_z+"_up")
  h_relative_up_z.Divide(h_central_z)

  h_relative_down_z   = h_ewk_z_down.Clone(); h_relative_down_z.SetName(central_z+"_down")
  h_relative_down_z.Divide(h_central_z)

  infile.cd(central)

  #Central Value for w or photon
  h_central  = gDirectory.Get(central)

  h_ewk_up   = gDirectory.Get(central+"Up")
  h_ewk_down = gDirectory.Get(central+"Down")
    
  if ch is 'atoz':
    h_relative_up   = h_ewk_up.Clone(); h_relative_up.SetName(central+"_up")
    h_relative_up.Divide(h_central)

    h_relative_down   = h_ewk_down.Clone(); h_relative_down.SetName(central+"_down")
    h_relative_down.Divide(h_central)
    
  # Have center at 1 file
  h_1 = h_central.Clone(); h_1.SetName("set1");
  h_1.Divide(h_central)

  if ch is 'atoz':
    # Have the ratio for the sys up and down as quad sum (z over other boson)
    h_ratio_up   = h_1.Clone(); h_ratio_up.SetName(central+"_ratio_up")
    h_ratio_down = h_1.Clone(); h_ratio_down.SetName(central+"_ratio_down")
    
    for b in range(h_ratio_up.GetNbinsX()):
      h_ratio_up.SetBinContent(b+1, sqrt(h_ewk_z_up.GetBinContent(b)**2 +h_ewk_up.GetBinContent(b)**2) )
      print b, h_ratio_up.GetBinContent(b+1)
      if (sqrt(h_ewk_z_down.GetBinContent(b+1)**2 +h_ewk_down.GetBinContent(b+1)**2) > 1):
        h_ratio_down.SetBinContent(b+1, 2-sqrt(h_ewk_z_down.GetBinContent(b+1)**2 +h_ewk_down.GetBinContent(b+1)**2) )
      else:
        h_ratio_down.SetBinContent(b+1, sqrt(h_ewk_z_down.GetBinContent(b+1)**2 +h_ewk_down.GetBinContent(b+1)**2) )
        print b, h_ratio_down.GetBinContent(b+1)
    
  h_ratio = h_central.Clone(); h_ratio.SetName(central+"overz")
  h_ratio.Divide(h_central_z)
  
  h_ratio_up_common = h_ratio.Clone(); h_ratio_up_common.SetName(central+"_overz_Upcommon")
  h_ratio_down_common = h_ratio.Clone(); h_ratio_down_common.SetName(central+"_overz_Downcommon")
  for b in range(h_ratio_down_common.GetNbinsX()):
    h_ratio_down_common.SetBinContent(b+1, 2-h_ratio_down_common.GetBinContent(b+1))
    print b+1, h_ratio_up_common.GetBinContent(b+1), h_ratio_down_common.GetBinContent(b+1)


  f_out = TFile(ch+"_ewkunc.root","recreate")
  f_out.cd()

  h_1.Write()
  h_central.Write()
  h_central_z.Write()
  h_relative_up_z.Write()
  h_relative_down_z.Write()
  if ch is 'atoz':
    h_relative_up.Write()
    h_relative_down.Write()
    h_ratio_up.Write()
    h_ratio_down.Write()  
  h_ratio.Write()
  h_ratio_down_common.Write()
  h_ratio_up_common.Write()
  f_out.Close()

################################

makevariations('atoz')
#makevariations('wtoz')
