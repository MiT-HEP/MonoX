import os
import sys
from pprint import pprint
from array import array
from ROOT import *
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
gROOT.SetBatch(True)

varName = 'sieie'
# var = Variables[varName]
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
#plotDir = os.path.join(versDir,'Plots')
plotDir = '/home/ballen/public_html/cmsplots/PurityTemp/'

MetSels = [ ("Met0toInf","cutstring that won't be used in this script") ] 
sources = [ "Data", "MC", "mcTruth" ]

purities = {}

for loc in Locations:
    purities[loc] = {}
    for pid in PhotonIds:
        purities[loc][pid] = {}
        for chiso in ChIsoSbSels:
            purities[loc][pid][chiso[0]] = {}
            for metCut in MetSels:
                purities[loc][pid][chiso[0]][metCut[0]] = {}
                for ptCut in PhotonPtSels[0][1:]:
                    purities[loc][pid][chiso[0]][metCut[0]][ptCut[0]] = {}

                    dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                    condorFileName = os.path.join(plotDir,dirName,"condor.out") 
                    condorFile = open(condorFileName)
                    
                    match = False
                    for source in sources:
                        for line in condorFile:
                            if "Purity of Photons in "+source+" is: " in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity = float(tmp[-2].strip("(),"))
                                    uncertainty = float(tmp[-1].strip("(),"))
                                # print purity, uncertainty
                                    purities[loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (purity, uncertainty)
                                    break
                        if not match:
                            print "No "+source+" purity found for skim:", dirName
                            purities[loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (1.025, 0.0)
pprint(purities)

for loc in Locations:
    for pid in PhotonIds:
        for source in sources:
            canvas = TCanvas()
            # canvas.SetLogx()
            histograms = []
            
            leg = TLegend(0.625,0.3,0.875,0.45)
            leg.SetFillColor(kWhite)
            leg.SetTextSize(0.03)
                
            lineColors = [ kBlue, kMagenta, kRed ]
            
            for chiso in ChIsoSbSels:
                
                # bins = [150, 250, 350, 500]
                bins = [150, 200, 250, 300, 500, 1000]
                # bins = [150,200,300,400,1000]
                hist = TH1F(chiso[0],chiso[0],(len(bins)-1),array('d',bins))
                hist.GetXaxis().SetTitle("#gamma p_{T} (GeV)")
                hist.GetYaxis().SetTitle("Purity")

                hist.SetMaximum(1.05)
                hist.SetMinimum(0.5)
                hist.SetLineColor(lineColors[ChIsoSbSels.index(chiso)])
                hist.SetStats(False)

                print chiso[0]
                leg.AddEntry(hist,chiso[0],'L')
            
                for ptCut in PhotonPtSels[0][1:]:
                    # print ptCut[0]
                    lowEdge = int(ptCut[0].split("t")[2])
                    # print lowEdge
                    binNumber = 0
                    for bin in bins:
                        if bin == lowEdge:
                            binNumber = bins.index(bin) + 1
                    print binNumber, float(purities[loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][0])
                    hist.SetBinContent(binNumber, float(purities[loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][0]))
                histograms.append(hist)
        
            histograms[0].SetTitle("Purity for "+str(loc)+" "+str(pid)+" Photons in "+source)
            histograms[0].Draw()
            histograms[2].Draw("same")
            histograms[1].Draw("same")
            # sys.stdin.readline()
        
            leg.Draw()
            plotName = "purity_"+str(source)+"_"+str(loc)+"_"+str(pid)+"_ptbinned_chiso"
            outDir = os.path.join(plotDir,'PtBinned')
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            plotPath = os.path.join(outDir,plotName)
            canvas.SaveAs(plotPath+".pdf")
            canvas.SaveAs(plotPath+".png")
            canvas.SaveAs(plotPath+".C")
            # sys.stdin.readline()
