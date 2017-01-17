import os
import sys
from array import array
from pprint import pprint
from selections import Variables, Version, Measurement, SigmaIetaIetaSels,  sieieSels, PhotonPtSels, MetSels, HistExtractor, config, skimDir
from ROOT import *
gROOT.SetBatch(True)

loc = sys.argv[1]
pid = sys.argv[2]
pt = sys.argv[3]
met = sys.argv[4]

try:
    era = sys.argv[5]
except:
    era = 'Spring15'

inputKey = era+'_'+loc+'_'+pid+'_PhotonPt'+pt+'_Met'+met

try:
    ptSel = PhotonPtSels['PhotonPt'+pt]
except KeyError:
    print 'Inputted pt range', pt, 'not found!'
    print 'Not applying any pt selection!'
    ptSel = '(1)'

try:
    metSel = MetSels['Met'+met]
except KeyError:
    print 'Inputted met range', met, 'not found!'
    print 'Not applying any met selection!'
    metSel = '(1)'

varName = 'chiso'
var = Variables[varName]
varBins = True

versDir = os.path.join('/data/t3home000/ballen/hist/purity',Version)
skimDir  = skimDir
plotDir = os.path.join(versDir,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skim = Measurement['bambu'][1]

pids = pid.split('-')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[2:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

baseSel = SigmaIetaIetaSels[era][loc][pid]+' && '+ptSel+' && '+metSel

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

raw = HistExtractor(var[0],var[2][loc],skim,fullSel,skimDir,varBins)
raw.SetName("rawmc")
histograms[0].append(raw)

nBins = len(var[2][loc][-1]) - 1
binEdges = array('d',var[2][loc][-1])
eSelScratch = "weight * ( (tp.mass > 81 && tp.mass < 101) && "+SigmaIetaIetaSels[era][loc][pid]+' && '+metSel+" && "+sieieSels[era][loc][pid]+")"
eSel = eSelScratch.replace("photons", "probes")
print eSel

# mcFile = TFile(os.path.join(skimDir, "mc_eg.root"))
# mcTree = mcFile.Get("skimmedEvents")
mcTree = TChain('skimmedEvents')
mcTree.Add(os.path.join(skimDir, 'dy-50_eg.root'))
mcHist = TH1F("emc","",nBins,binEdges)
mcTree.Draw("probes.chIso>>emc", eSel)
outFile.WriteTObject(mcHist)
histograms[1].append(mcHist)

# dataFile = TFile(os.path.join(skimDir, "data_eg.root"))
# dataTree = dataFile.Get("skimmedEvents")
dataTree = TChain('skimmedEvents')
dataTree.Add(os.path.join(skimDir, 'sph-16*_eg.root'))
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

    if mcValue == 0 or dataValue == 0:
        ratio = 1
        error = 0.05
    else:
        ratio = dataValue / mcValue 
        error = ratio * ( (dataError / dataValue)**2 + (mcError / mcValue)**2 )**(0.5)

    scaleHist.SetBinContent(iBin, ratio)
    scaled.SetBinContent(iBin, ratio * scaled.GetBinContent(iBin))
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
