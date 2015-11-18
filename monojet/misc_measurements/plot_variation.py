#! /usr/bin/env python                                                                                                                                                         

from ROOT import *
from array import array
from tdrStyle import *

setTDRStyle()

def plotvariations(channel):

    f = TFile("qcd_13TeV.root","READ")
    h1  = f.Get(channel+"_kfactor")
    h2 = f.Get(channel+"_scaleUp")
    h2.SetLineColor(2)
    h3 = f.Get(channel+"_scaleDown")
    h3.SetLineColor(2)
    h4 = f.Get(channel+"_pdfUp")
    h4.SetLineColor(4)
    h5 = f.Get(channel+"_pdfDown")

    for bin in range(1, h5.GetNbinsX()+1):
        if h5.GetBinContent(bin) > 1.0:
            h5.SetBinContent(bin,2-h5.GetBinContent(bin))        

    h5.SetLineColor(4)
    
    c4 = TCanvas("c4","c4", 900, 1000)

    # Add Legend                                                                                                                                                                   
    legend = TLegend(.60,.60,.92,.92)
    legend . AddEntry(h1,"Central Value","l")
    legend . AddEntry(h2,"Scale Up/Down","l")
    legend . AddEntry(h4,"Pdf Up/Down","l")
    
    h1.Draw()
    h1.GetYaxis().SetTitle('Scale')
    h1.GetYaxis().CenterTitle()
    h1.GetYaxis().SetTitleOffset(1.2)
    #h1.GetXaxis().SetLabelSize(0)
    h1.GetXaxis().SetTitle('Gen Boson Pt')
    h2.Draw("same")
    h3.Draw("same")
    h4.Draw("same")
    h5.Draw("same")

    legend.Draw("same")

    c4.SaveAs("test.root")
    c4.SaveAs("test.pdf")
    c4.SaveAs("test.png")

#plotvariations("pho")
plotvariations("z")
