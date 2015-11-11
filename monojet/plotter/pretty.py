from ROOT import *
from math import *

def plot_ratio(pull,data,mc,bin,xlabel,low,high,division):

    Pull = data
    #Pull.Add(mc,-1)
    Pull.GetXaxis().SetTitle(xlabel)
    Pull.GetYaxis().SetTitleOffset(1.2)
    Pull.GetYaxis().SetTitleSize(0.04)
    Pull.GetYaxis().SetNdivisions(division)
    Pull.GetYaxis().SetLabelSize(0.02)
    Pull.SetMarkerStyle(20)
    Pull.SetMarkerSize(0.8)

    if pull:
        print 'Plotting the pulls'
        for i in range(bin):
            i += 1
            if data.GetBinContent(i) != 0 :
                Pull.SetBinContent(i,Pull.GetBinContent(i)/Pull.GetBinError(i))
            else: Pull.SetBinContent(i,0)

        Pull.SetMaximum(5.0 )
        Pull.SetMinimum(-5.0)
        Pull.SetFillColor(2)
        Pull.GetYaxis().SetTitle('#sigma(Data-MC)')
        Pull.Draw("HIST")

    else:
        print 'Plotting the ratio'
        Pull.Divide(mc)
        Pull.SetMaximum(high)
        Pull.SetMinimum(low)
        Pull.GetYaxis().SetTitle('Data/Bkg.')
        Pull.SetMarkerColor(1)
        Pull.SetLineColor(1)
        Pull.Draw("e")


def plot_cms(preliminary,lumi):
    latex2 = TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.035)
    latex2.SetTextAlign(31) # align right
    latex2.DrawLatex(0.87, 0.95, str(lumi)+" pb^{-1} (13 TeV)");

    latex3 = TLatex()
    latex3.SetNDC()
    latex3.SetTextSize(0.75*c4.GetTopMargin())
    latex3.SetTextFont(62)
    latex3.SetTextAlign(11) # align right
    latex3.DrawLatex(0.22, 0.85, "CMS");
    latex3.SetTextSize(0.5*c4.GetTopMargin())
    latex3.SetTextFont(52)
    latex3.SetTextAlign(11)
    if(preliminary):
        latex3.DrawLatex(0.20, 0.8, "Preliminary");
