import os
import sys
from ROOT import *
from selections import Variables, Version, Measurement, Selections, HistExtractor

gROOT.SetBatch(True)

varName = 'sieie'
var = Variables[varName]

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "MonophotonBkgdComp"
skims = Measurement[skimName] 
regions = ["low", "med","high","real"]
# regions = ["Real"]
selName = "barrel_medium_PhotonPt180toInf"
selKeys = [selName+"_"+region for region in regions]

histInfo = [ ('total','Total',0,kBlack,'P')
             ,('true','True Photons',1001,kBlue,'F')
             ,('fake',"Fake Photons",1001,kRed,'F') ]

for selKey,region in zip(selKeys,regions):
    histograms = []

    leg = TLegend(0.125,0.6,0.375,0.75 );
    leg.SetFillColor(kWhite);
    leg.SetTextSize(0.03);
    
    for skim,sel,info in zip(skims,Selections[selKey],histInfo):
        hist = HistExtractor(var[0],var[3][loc],skim,sel,skimDir,False)
        print hist.GetSumOfWeights()
        hist.Draw()
        #sys.stdin.readline()
        hist.SetFillColor(info[3])
        hist.SetFillStyle(info[2])
        hist.GetXaxis().SetTitle("#sigma_{i#etai#eta}")
        hist.GetYaxis().SetTitle("Events / (0.0005)")
        leg.AddEntry(hist, info[1], info[4]);
        histograms.append(hist)

    histograms[0].SetMarkerStyle(8)
    histograms[0].SetLineColor(histInfo[0][3])
    histograms[0].SetMarkerColor(histInfo[0][3])

    stack = THStack("stack","stack")
    stack.Add(histograms[2])
    stack.Add(histograms[1])

    canvas = TCanvas()
    stack.SetTitle('Background Composition of '+region+' Sideband for Monophoton')


    stack.Draw('hist')
    stack.GetXaxis().SetTitle("#sigma_{i#etai#eta}")
    stack.GetYaxis().SetTitle("Events / (0.0005)")


    for iHist in xrange(0,1):
        histograms[iHist].Draw("SAME")

    leg.Draw("goff");

    outName = os.path.join(plotDir,'composition_'+selKey+'.pdf')
    canvas.SaveAs(outName)

    truthTotal = histograms[0].Integral(1,12)
    truthReal = histograms[1].Integral(1,12)
    truthFake = histograms[2].Integral(1,12)
    print "Number of Total photons passing selection:", truthTotal
    print "Number of Real photons passing selection:", truthReal
    print "Number of Fake photons passing selection:", truthFake

    truthPurity = float(truthReal) / float(truthTotal)
    print "Purity of Photons using Real / Total:", truthPurity

    truthPurity = float(truthReal) / float(truthReal + truthFake)
    print "Purity of Photons using Real / (Real + Fake):", truthPurity
