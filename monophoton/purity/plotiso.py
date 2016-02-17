import os
import sys
from array import array
from pprint import pprint
from selections import Variables, Version, Measurement, SigmaIetaIetaSels,  sieieSels, chIsoSels, PhotonPtSels, MetSels, HistExtractor
from ROOT import *
gROOT.SetBatch(False)

loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

ptSel = '(1)'
for ptsel in PhotonPtSels:
    if 'PhotonPt'+pt == ptsel[0]:
        ptSel = ptsel[1]
if ptSel == '(1)':
    print 'Inputted pt range', pt, 'not found!'
    print 'Not applying any pt selection!'

metSel = '(1)'
for metsel in MetSels:
    if 'Met'+met == metsel[0]:
        metSel = metsel[1]
if metSel == '(1)':
    print 'Inputted met range', met, 'not found!'
    print 'Not applying any met selection!'

varName = 'chiso'
var = Variables[varName]
varBins = True

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = '/scratch5/ballen/hist/monophoton/skim'
plotDir = os.path.join(versDir,'Plots','SignalContam',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skim = Measurement[skimName][1]

baseSel = SigmaIetaIetaSels[loc][pid]+' && '+ptSel+' && '+metSel

outName = os.path.join(plotDir,'chiso_'+inputKey)
print outName+'.root'
outFile = TFile(outName+'.root','RECREATE')

histograms = [ [], [], [] ]
leg = TLegend(0.725,0.7,0.875,0.85 );
leg.SetFillColor(kWhite);
leg.SetTextSize(0.03);

colors = [kBlue, kRed, kBlack]

truthSel = '(photons.matchedGen == -22)'
fullSel = baseSel+' && '+truthSel

raw = HistExtractor(var[0],var[3][loc],skim,fullSel,skimDir,varBins)
raw.SetName("rawmc")
histograms[0].append(raw)

nBins = len(var[3][loc][-1]) - 1
binEdges = array('d',var[3][loc][-1])
eSelScratch = "weight * ( (tp.mass > 81 && tp.mass < 101) && "+SigmaIetaIetaSels[loc][pid]+' && '+metSel+" && "+sieieSels[loc][pid]+")"
eSel = eSelScratch.replace("photons", "probes")
print eSel

mcFile = TFile(os.path.join(skimDir, "mc_eg.root"))
mcTree = mcFile.Get("skimmedEvents")
mcHist = TH1F("emc","",nBins,binEdges)
mcTree.Draw("probes.chIso>>emc", eSel)
outFile.WriteTObject(mcHist)
histograms[1].append(mcHist)

dataFile = TFile(os.path.join(skimDir, "data_eg.root"))
dataTree = dataFile.Get("skimmedEvents")
dataHist = TH1F("edata","",nBins,binEdges)
dataTree.Draw("probes.chIso>>edata", eSel)
outFile.WriteTObject(dataHist)
histograms[1].append(dataHist)

scaled = raw.Clone("scaledmc")
scaleHist = TH1F("escale","Data/MC Scale Factors from Electrons",nBins,binEdges)
for iBin in range(1,scaleHist.GetNbinsX()+1):
    dataValue = dataHist.GetBinContent(iBin)
    dataError = dataHist.GetBinError(iBin)

    mcValue = mcHist.GetBinContent(iBin)
    mcError = mcHist.GetBinError(iBin)

    ratio = dataValue / mcValue 
    scaleHist.SetBinContent(iBin, ratio)
    scaled.SetBinContent(iBin, ratio * scaled.GetBinContent(iBin))

    error = ratio * ( (dataError / dataValue)**2 + (mcError / mcValue)**2 )**(0.5)
    scaleHist.SetBinError(iBin, error)

outFile.WriteTObject(scaleHist)
histograms[0].append(scaled)
histograms[2].append(scaleHist)

suffix = [ ("photons", "Events"), ("electrons", "Events"), ("scale", "Scale Factor") ]

for iList, hlist in enumerate(histograms):
    canvas = TCanvas()
    for iHist, hist in enumerate(hlist):
        if (iList < 2): 
            hist.Scale( 1. / hist.GetSumOfWeights())

        hist.SetLineColor(iHist+1)
        hist.SetLineWidth(3)
        if (iList < 2): 
            hist.SetLineStyle(kDashed)
        hist.SetStats(False)
    
        hist.GetXaxis().SetTitle("CH Iso (GeV)")
        hist.GetYaxis().SetTitle(suffix[iList][1])
        
        hist.GetXaxis().SetLabelSize(0.045)
        hist.GetXaxis().SetTitleSize(0.045)
        hist.GetYaxis().SetLabelSize(0.045)
        hist.GetYaxis().SetTitleSize(0.045)

        outFile.cd()
        hist.Write()
        
        canvas.cd()
        if (iHist == 0):
            if (iList < 2): 
                hist.Draw("hist")
            else:
                hist.Draw("")
        else:
            hist.Draw("samehist")
        leg.AddEntry(hist, hist.GetName(), 'L')

    canvas.cd()
    if (iList < 2): 
        leg.Draw()

    newName = outName+'_'+suffix[iList][0]

    canvas.SaveAs(newName+'.pdf')
    canvas.SaveAs(newName+'.png')
    canvas.SaveAs(newName+'.C')
    
    canvas.SetLogy()
    canvas.SaveAs(newName+'_Logy.pdf')
    canvas.SaveAs(newName+'_Logy.png')
    canvas.SaveAs(newName+'_Logy.C')
    
    
    leg.Clear()
outFile.Close()
