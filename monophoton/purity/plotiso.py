import os
import sys
from array import array
from pprint import pprint
from selections import Variables, Version, Measurement, Selections, SigmaIetaIetaSels,  sieieSels, chIsoSels, PhotonPtSels, MetSels, HistExtractor
from ROOT import *
gROOT.SetBatch(True)

loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

ptSel = '(1)'
for ptsel in PhotonPtSels[0]:
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
skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots','SignalContam',inputKey)
# plotDir = os.path.join(os.environ['CMSPLOTS'],'SignalContamTemp',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skim = Measurement[skimName][0]

baseSel = SigmaIetaIetaSels[loc][pid]+' && '+ptSel+' && '+metSel

outName = os.path.join(plotDir,'chiso_'+inputKey)
print outName+'.root'
outFile = TFile(outName+'.root','recreate')

canvas = TCanvas()
histograms = []
leg = TLegend(0.625,0.45,0.875,0.85 );
leg.SetFillColor(kWhite);
leg.SetTextSize(0.03);

colors = [kBlue, kRed, kBlack]

truthSel = '(selPhotons.matchedGen == -22)'
fullSel = baseSel+' && '+truthSel

raw = HistExtractor(var[0],var[3][loc],skim,fullSel,skimDir,varBins)
raw.SetName("rawmc")
histograms.append(raw)

nBins = len(var[3][loc][-1]) - 1
binEdges = array('d',var[3][loc][-1])
eSelScratch = "weight * ( (tp.mass > 81 && tp.mass < 101) && "+SigmaIetaIetaSels[loc][pid]+' && '+metSel+" && "+sieieSels[loc][pid]+")"
eSel = eSelScratch.replace("selPhotons", "probes")
print eSel

dataFile = TFile(os.path.join(skimDir, "data_eg.root"))
dataTree = dataFile.Get("skimmedEvents")
dataHist = TH1F("edata","edata",nBins,binEdges)
dataTree.Draw("probes.chIso>>edata", eSel)
outFile.WriteTObject(dataHist)

mcFile = TFile(os.path.join(skimDir, "mc_eg.root"))
mcTree = mcFile.Get("skimmedEvents")
mcHist = TH1F("emc","emc",nBins,binEdges)
mcTree.Draw("probes.chIso>>emc", eSel)
outFile.WriteTObject(mcHist)

scaled = raw.Clone("scaledmc")
scaleHist = TH1F("escale","escale",nBins,binEdges)
for iBin in range(1,scaleHist.GetNbinsX()+1):
    ratio = dataHist.GetBinContent(iBin) / mcHist.GetBinContent(iBin)
    scaleHist.SetBinContent(iBin, ratio)
    scaled.SetBinContent(iBin, ratio * scaled.GetBinContent(iBin))
outFile.WriteTObject(scaleHist)
histograms.append(scaled)

for iHist, hist in enumerate(histograms[:]):
    # pprint(hist)
    # hist.Draw()
    # print hist.GetSumOfWeights()
    hist.Scale( 1. / hist.GetSumOfWeights())

    hist.SetLineColor(iHist+1)
    hist.SetLineWidth(2)
    hist.SetLineStyle(iHist+2*iHist)
    hist.SetStats(False)
    
    hist.GetXaxis().SetTitle("CH Iso (GeV)")
    hist.GetYaxis().SetTitle("Events")
    
    hist.GetXaxis().SetLabelSize(0.045)
    hist.GetXaxis().SetTitleSize(0.045)
    hist.GetYaxis().SetLabelSize(0.045)
    hist.GetYaxis().SetTitleSize(0.045)
    
    outFile.cd()
    hist.Write()

    canvas.cd()
    if (iHist == 0):
        hist.Draw("")
    else:
        hist.Draw("same")
    leg.AddEntry(hist, hist.GetName(), 'L')

outFile.Close()
canvas.cd()
leg.Draw()

canvas.SaveAs(outName+'.pdf')
canvas.SaveAs(outName+'.png')
canvas.SaveAs(outName+'.C')

canvas.SetLogy()
canvas.SaveAs(outName+'_Logy.pdf')
canvas.SaveAs(outName+'_Logy.png')
canvas.SaveAs(outName+'_Logy.C')
