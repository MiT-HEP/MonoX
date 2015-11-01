#! /usr/bin/env python                                                                                                                                                               
from ROOT import *
from array import array
from tdrStyle import *
#from pretty import plot_cms
setTDRStyle()

def makevariations(channel):

  bins = [100,150,200,250,300,400,500,600,800,1000]
  binELow = array("d",[bins[i] for i in range(len(bins))])
  h_pt = TH1F("h_pt","h_pt",len(bins)-1,binELow)

  h_kfactor     = TH1F(channel+"_kfactor",channel+"_kfactor",len(bins)-1,binELow)
  h_pdfUp_f     = TH1F(channel+"_pdfUp",channel+"_pdfUp",len(bins)-1,binELow)
  h_pdfDown_f   = TH1F(channel+"_pdfDown",channel+"_pdfDown",len(bins)-1,binELow)
  h_scaleUp_f   = TH1F(channel+"_scaleUp",channel+"_scaleUp",len(bins)-1,binELow)
  h_scaleDown_f = TH1F(channel+"_scaleDown",channel+"_scaleDown",len(bins)-1,binELow)
  
  if channel is "z":
    nlo_file = TFile("eos/cms/store/user/zdemirag/privateGen/Z_13TeV_v3.root","READ");
  if channel is "pho":
    nlo_file = TFile("eos/cms/store/user/zdemirag/privateGen/A_13TeV_v2.root","READ");

  nlo_tree = nlo_file.Get("Events")

  h_pdf = {}; h_pdfUp = {}; h_pdfDn = {}; h_scale = {}
  for bin in range(len(bins)-1):
    h_pdf[bin] = TH1F("h_pdf_"+str(bin),"h_pdf_"+str(bin),100000,-500.0,500.0)
    h_pdfUp[bin] = TH1F("h_pdfUp_"+str(bin),"h_pdfUp_"+str(bin),100000,-500.0,500.0)
    h_pdfDn[bin] = TH1F("h_pdfDn_"+str(bin),"h_pdfDn_"+str(bin),100000,-500.0,500.0)
    for scale in ["00","01","02","10","12","20","21","22"]:
      h_scale["bin_"+str(bin)+"_"+scale] = TH1F("h_scale_bin_"+str(bin)+"_"+scale,"h_scale_"+str(bin)+"_"+scale,100000,-50.0,50.0)
      
  for bin in range(len(bins)-1):    
    binlo = bins[bin]
    binhi = bins[bin+1]
    #Events.Draw("pdf>>h_pdf_"+str(bin),"dm_pt>"+str(binlo)+" && dm_pt<"+str(binhi),"goff")
    Events.Draw("pdfUp>>h_pdfUp_"+str(bin),"dm_pt>"+str(binlo)+" && dm_pt<"+str(binhi),"goff")
    Events.Draw("pdfDown>>h_pdfDn_"+str(bin),"dm_pt>"+str(binlo)+" && dm_pt<"+str(binhi),"goff")
    for scale in ["00","01","02","10","12","20","21","22"]:
      Events.Draw("scale"+scale+">>h_scale_bin_"+str(bin)+"_"+scale,"dm_pt>"+str(binlo)+" && dm_pt<"+str(binhi),"goff")
    
  for bin in range(len(bins)-1):    
    binlo = bins[bin]
    binhi = bins[bin+1]
    scaleUp = 1.0
    scaleDn = 1.0
    #scaleUp=h_scale["bin_"+str(bin)+"_00"].GetMean()
    #scaleDn=h_scale["bin_"+str(bin)+"_22"].GetMean()
    for scale in ["00","01","02","10","12","20","21","22"]:
      if (h_scale["bin_"+str(bin)+"_"+scale].GetMean()>scaleUp): scaleUp=h_scale["bin_"+str(bin)+"_"+scale].GetMean()
      if (h_scale["bin_"+str(bin)+"_"+scale].GetMean()<scaleDn): scaleDn=h_scale["bin_"+str(bin)+"_"+scale].GetMean()

    h_kfactor.SetBinContent(bin+1,1.0)
    h_pdfUp_f.SetBinContent(bin+1,(1.0+h_pdfUp[bin].GetRMS()))
    h_pdfDown_f.SetBinContent(bin+1,(1.0+h_pdfDn[bin].GetRMS()))
    h_scaleUp_f.SetBinContent(bin+1,scaleUp)
    h_scaleDown_f.SetBinContent(bin+1,scaleDn)

    print binlo,binhi,1.0+h_pdfUp[bin].GetRMS(),1.0+h_pdfDn[bin].GetRMS(),scaleUp,scaleDn
  
  f_out = TFile("qcd.root","recreate")
  f_out.cd()
  h_kfactor.Write()
  h_pdfUp_f.Write()
  h_pdfDown_f.Write()
  h_scaleUp_f.Write()
  h_scaleDown_f.Write()

  f_out.Close()
  
################################

makevariations("z")
