import os
import sys
from numpy import arange
from selections import Variables, Version, Measurement, Selections, SigmaIetaIetaSels,  sieieSels, chIsoSels, PhotonPtSels, MetSels, HistExtractor
from ROOT import *

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
# plotDir = os.path.join(versDir,'Plots',inputKey)
plotDir = os.path.join(os.environ['CMSPLOTS'],'SignalContamTemp',inputKey)
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

for dR in arange(0.4,0.9,0.1):
    truthSel = '( (TMath::Abs(selPhotons.matchedGen) == 22) && (!selPhotons.hadDecay) && (selPhotons.drParton > '+str(dR)+') )'
    fullSel = baseSel+' && '+truthSel
    
    hist = HistExtractor(var[0],var[3][loc],skim,fullSel,skimDir,varBins)
    hist.SetName("ShapeChIso_dR"+str(int(dR*10)))
    hist.Scale( 1. / hist.GetSumOfWeights())

    # hist.SetLineColor(kBlack)
    hist.SetLineColor(int(dR*10))
    hist.SetLineWidth(2)
    hist.SetLineStyle(kDashed)
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
    if (dR == 0.1):
        hist.Draw("hist")
    else:
        hist.Draw("histsame")

    leg.AddEntry(hist, 'dR > '+str(dR), 'L')
    histograms.append(hist)

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
