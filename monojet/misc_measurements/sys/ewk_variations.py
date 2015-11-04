#! /usr/bin/env python                                                                                                                                                               
from ROOT import *
from array import array
from tdrStyle import *
#from pretty import plot_cms
setTDRStyle()

def makevariations(ch):

  infile = TFile("newscalefactors.root","READ")

  if ch is 'atoz':
    central   = "a_ewkcorr"
    central_z = "z_ewk"
  if ch is 'wtoz':
    central   = "w_ewkcorr"
    central_z = "z_ewkcorr"
  
  infile.cd(central_z)

  #Central Value for Z
  h_central_z  = gDirectory.Get(central_z)
  h_ewk_z_up   = gDirectory.Get(central_z+"Up")
  h_ewk_z_down = gDirectory.Get(central_z+"Down")

  h_relative_up_z   = h_central_z.Clone(); h_relative_up_z.SetName(central_z+"_up")
  h_relative_up_z.Divide(h_ewk_z_up)

  h_relative_down_z   = h_central_z.Clone(); h_relative_down_z.SetName(central_z+"_down")
  h_relative_down_z.Divide(h_ewk_z_down)


  infile.cd(central)

  #Central Value for w or photon
  h_central  = gDirectory.Get(central)
  if ch is 'atoz':
    h_ewk_up   = gDirectory.Get(central+"Up_orig")
    h_ewk_down = gDirectory.Get(central+"Down_orig")
    
    h_relative_up   = h_central.Clone(); h_relative_up.SetName(central+"_up")
    h_relative_up.Divide(h_ewk_up)

    h_relative_down   = h_central.Clone(); h_relative_down.SetName(central+"_down")
    h_relative_down.Divide(h_ewk_down)

  f_out = TFile(ch+"_ewkunc.root","recreate")
  f_out.cd()
  h_central.Write()
  h_central_z.Write()
  h_relative_up_z.Write()
  h_relative_down_z.Write()
  if ch is 'atoz':
    h_relative_up.Write()
    h_relative_down.Write()
  f_out.Close()

################################

#makevariations('atoz')
makevariations('wtoz')
