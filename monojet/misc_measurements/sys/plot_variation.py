#! /usr/bin/env python                                                                                                                                                         

from ROOT import *
from array import array
from tdrStyle import *

setTDRStyle()

def plotvariations(ch):

    if ch is 'pho':
        f = TFile("atoz_unc.root","READ")
        channel = "znlo1_over_anlo1"
    if ch is 'w':
        f = TFile("wtoz_unc.root","READ")
        channel = "znlo012_over_wnlo012"        

    h1  = f.Get(channel+"_central")
    h1.SetLineColor(1)
    h2 = f.Get(channel+"_CorrscaleUp")
    h2.SetLineColor(2)
    h3 = f.Get(channel+"_CorrscaleDown")
    h3.SetLineColor(2)
    h4 = f.Get(channel+"_pdfUp")
    h4.SetLineColor(4)
    h5 = f.Get(channel+"_pdfDown")
    h5.SetLineColor(4)
    h6 = f.Get(channel+"_UnCorrscaleUp")
    h6.SetLineColor(6)
    h7 = f.Get(channel+"_UnCorrscaleDown")
    h7.SetLineColor(6)
    h8 = f.Get(channel+"_UnCorr80scaleUp")
    h8.SetLineColor(8)
    h9 = f.Get(channel+"_UnCorr80scaleDown")
    h9.SetLineColor(8)
    
    c4 = TCanvas("c4","c4", 900, 1000)

    # Add Legend                                                                                                                                                                   
    legend = TLegend(.60,.70,.92,.92)
    legend . AddEntry(h1,"Central Value","l")
    legend . AddEntry(h2,"Correlated Scale Up/Down","l")
    legend . AddEntry(h7,"Uncorrelated Scale Up/Down","l")
    legend . AddEntry(h8,"Uncorrelated by 80% Scale Up/Down","l")
    legend . AddEntry(h4,"Pdf Up/Down","l")
    
    h1.Draw("HIST")
    h1.GetYaxis().SetTitle('Sys on the Ratio')
    h1.GetYaxis().CenterTitle()
    h1.GetYaxis().SetTitleOffset(1.2)
    #h1.GetXaxis().SetLabelSize(0)
    h1.GetXaxis().SetTitle('Gen Boson Pt')
    h2.Draw("HISTsame")
    h3.Draw("HISTsame")
    h4.Draw("HISTsame")
    h5.Draw("HISTsame")
    h6.Draw("HISTsame")
    h7.Draw("HISTsame")
    h8.Draw("HISTsame")
    h9.Draw("HISTsame")
    
    legend.Draw("same")

    c4.SaveAs(ch+"ratio_unc.root")
    c4.SaveAs(ch+"ratio_unc.pdf")
    c4.SaveAs(ch+"ratio_unc.png")

plotvariations("w")
#plotvariations("pho")
