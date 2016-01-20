import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
from ROOT import *
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
gROOT.SetBatch(True)

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
#plotDir = os.path.join(versDir,'Plots')
plotDir = '/home/ballen/public_html/cmsplots/PurityShape/'
outDir = os.path.join(plotDir,'PtBinned')
if not os.path.exists(outDir):
    os.makedirs(outDir)

MetSels = [ ("Met0toInf","cutstring that won't be used in this script") ] 
sources = [ "data", "mc", "truth" ]

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
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    purity = float(tmp[-2].strip("(),"))
                                    uncertainty = float(tmp[-1].strip("(),"))
                                    purities[loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (purity, uncertainty)
                                    break
                        if not match:
                            print "No "+source+" purity found for skim:", dirName
                            purities[loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (1.025, 0.0)
                    condorFile.close()
pprint(purities)

for loc in Locations:
    for pid in PhotonIds:
        for source in sources:
            purityFileName = "purity_"+source+"_"+loc+"_"+pid+".tex"
            purityFilePath = os.path.join(outDir,purityFileName)
            purityFile = open(purityFilePath, "w")
            
            purityFile.write(r"\documentclass{article}")
            purityFile.write("\n")
            purityFile.write(r"\usepackage[paperheight=1.5in, paperwidth=6in]{geometry}")
            purityFile.write(r"\begin{document}")
            purityFile.write("\n")

            purityFile.write(r"\begin{tabular}{ |r|c|c|c| }")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            purityFile.write(r"\multicolumn{4}{ |c| }{Purities for "+loc+" "+pid+" photons in "+source+r"} \\")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            

            purityFile.write(r"photon\ $p_{T}$ ")
            for ptCut in PhotonPtSels[0][1:]:
                purityFile.write(r"& "+ptCut[0].strip("PhotonPt")+" ")
            purityFile.write(r"\\ \hline")
            purityFile.write("\n")

            canvas = TCanvas()
            histograms = []
            
            leg = TLegend(0.625,0.3,0.875,0.45)
            leg.SetFillColor(kWhite)
            leg.SetTextSize(0.03)
                
            lineColors = [ kBlue, kMagenta, kRed ]
            
            bins = [150, 250, 350, 500]

            for chiso in ChIsoSbSels:                
                purityFile.write(chiso[0]+" ")

                hist = TH1F(chiso[0],chiso[0],(len(bins)-1),array('d',bins))
                hist.GetXaxis().SetTitle("#gamma p_{T} (GeV)")
                hist.GetYaxis().SetTitle("Purity")

                hist.SetMaximum(1.05)
                hist.SetMinimum(0.5)
                hist.SetLineColor(lineColors[ChIsoSbSels.index(chiso)])
                hist.SetLineWidth(2)
                hist.SetStats(False)

                leg.AddEntry(hist,chiso[0],'L')
            
                for ptCut in PhotonPtSels[0][1:]:
                    lowEdge = int(ptCut[0].split("t")[2])
                    binNumber = 0
                    for bin in bins:
                        if bin == lowEdge:
                            binNumber = bins.index(bin) + 1
   
                    purity = float(purities[loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][0])
                    uncertainty = float(purities[loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][1])
                    # print binNumber, purity, uncertainty
                    purityFile.write(r"& "+str(round(purity,3))+r" $\pm$ "+str(round(uncertainty,3))+" ")
                    hist.SetBinContent(binNumber, purity)
                
                histograms.append(hist)
                purityFile.write(r"\\ \hline")
                purityFile.write("\n")
            
            purityFile.write(r"\end{tabular}")
            purityFile.write("\n")
            purityFile.write(r"\end{document}")
            purityFile.close()

            histograms[0].SetTitle("Purity for "+str(loc)+" "+str(pid)+" Photons in "+source)
            histograms[0].Draw()
            histograms[2].Draw("same")
            histograms[1].Draw("same")
        
            leg.Draw()
            plotName = "purity_"+str(source)+"_"+str(loc)+"_"+str(pid)+"_ptbinned_chiso"
            plotPath = os.path.join(outDir,plotName)
            canvas.SaveAs(plotPath+".pdf")
            canvas.SaveAs(plotPath+".png")
            canvas.SaveAs(plotPath+".C")
            
            pdflatex = Popen( ["pdflatex",purityFilePath,"-interaction nonstopmode"]
                              ,stdout=PIPE,stderr=PIPE,cwd=outDir)
            pdfout = pdflatex.communicate()
            if not pdfout[1] == "":
                print pdfout[1]
            
            
            convert = Popen( ["convert",purityFilePath.replace(".tex",".pdf")
                              ,purityFilePath.replace(".tex",".png") ]
                             ,stdout=PIPE,stderr=PIPE,cwd=outDir)
            conout = convert.communicate()
            if not conout[1] == "":
                print conout[1] 
