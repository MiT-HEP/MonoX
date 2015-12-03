import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
from ROOT import *
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels, cutPhotonPtHigh
gROOT.SetBatch(True)

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
plotDirs = [ ('shape', os.path.join(versDir,'Plots','Shape')), ('twobin', os.path.join(versDir,'Plots','TwoBin')) ]
# outDir = '/home/ballen/public_html/cmsplots/PurityComp/'
outDir = os.path.join(versDir,'Plots','Comp')
if not os.path.exists(outDir):
    os.makedirs(outDir)

MetSels = [ ("Met0toInf","cutstring that won't be used in this script") ] 
sources = [ "data" ] 

purities = {}

for plotDir in plotDirs:
    fit = plotDir[0]
    purities[fit] = {}
    for loc in Locations:
        purities[fit][loc] = {}
        for pid in PhotonIds:
            purities[fit][loc][pid] = {}
            for chiso in ChIsoSbSels:
                purities[fit][loc][pid][chiso[0]] = {}
                for metCut in MetSels:
                    purities[fit][loc][pid][chiso[0]][metCut[0]] = {}
                    for ptCut in PhotonPtSels[0][1:]:
                        purities[fit][loc][pid][chiso[0]][metCut[0]][ptCut[0]] = {}
                        
                        dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                        condorFileName = os.path.join(plotDir[1],dirName,"condor.out") 
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
                                        purities[fit][loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (purity, uncertainty)
                                        break
                        if not match:
                            print "No "+source+" purity found for skim:", dirName
                            purities[fit][loc][pid][chiso[0]][metCut[0]][ptCut[0]][source] = (1.025, 0.0)
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
            purityFile.write(r"\usepackage[paperheight=1.5in, paperwidth=9.5in]{geometry}")
            purityFile.write("\n")
            purityFile.write(r"\usepackage{multirow}")
            purityFile.write("\n")
            purityFile.write(r"\begin{document}")
            purityFile.write("\n")

            purityFile.write(r"\begin{tabular}{ |c|c|c|c|c|c|c| }")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            purityFile.write(r"\multicolumn{7}{ |c| }{Purities for "+loc+" "+pid+" photons in "+source+r"} \\")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            

            purityFile.write(r"\multicolumn{2}{|c|}{photon\ $p_{T}$} ")
            for ptCut in PhotonPtSels[0][1:]:
                purityFile.write(r"& "+ptCut[0].strip("PhotonPt")+" ")
            purityFile.write(r"\\ \hline")
            purityFile.write("\n")

            canvas = TCanvas()
            histograms = [ [], [] ]
            
            legCoords = [ (0.625,0.3,0.875,0.45) , (0.15,0.6,0.4,0.75) ]
            coords = legCoords[Locations.index(loc)]

            leg = TLegend(coords[0],coords[1],coords[2],coords[3])
            leg.SetFillColor(kWhite)
            leg.SetTextSize(0.03)

            lineColors = [ kBlue, kRed ]
            lineStyles = [ kSolid, kDashed ]
            
            bins = cutPhotonPtHigh+[500]
            
            for chiso in ChIsoSbSels[1:]:                
                purityFile.write(r"\multirow{2}{*}{"+chiso[0]+"} ")

                for plotDir in plotDirs:
                    fit = plotDir[0]
                    purityFile.write(r"& "+fit+" ")

                    hist = TH1F(chiso[0]+fit,chiso[0]+fit,(len(bins)-1),array('d',bins))
                    hist.GetXaxis().SetTitle("#gamma p_{T} (GeV)")
                    hist.GetYaxis().SetTitle("Purity")
                    
                    hist.GetXaxis().SetLabelSize(0.045)
                    hist.GetXaxis().SetTitleSize(0.045)
                    hist.GetYaxis().SetLabelSize(0.045)
                    hist.GetYaxis().SetTitleSize(0.045)

                    mins = [0.775, 0.625]
                    maxs = [1.025, 1.025]
                    hist.SetMaximum(maxs[Locations.index(loc)])
                    hist.SetMinimum(mins[Locations.index(loc)])
                    hist.GetYaxis().SetNdivisions(508)

                    hist.SetLineColor(lineColors[ChIsoSbSels.index(chiso)-1])
                    hist.SetLineStyle(lineStyles[plotDirs.index(plotDir)])
                    hist.SetLineWidth(2)
                    hist.SetStats(False)

                    leg.AddEntry(hist,chiso[0]+" "+fit,'L')
            
                    for ptCut in PhotonPtSels[0][1:]:
                        lowEdge = int(ptCut[0].split("t")[2])
                        binNumber = 0
                        for bin in bins:
                            if bin == lowEdge:
                                binNumber = bins.index(bin) + 1
   
                        purity = float(purities[fit][loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][0])
                        uncertainty = float(purities[fit][loc][pid][chiso[0]][MetSels[0][0]][ptCut[0]][source][1])
                        # print binNumber, purity, uncertainty
                        purityFile.write(r"& "+str(round(purity,3))+r" $\pm$ "+str(round(uncertainty,3))+" ")
                        hist.SetBinContent(binNumber, purity)
                
                    histograms[plotDirs.index(plotDir)].append(hist)
                    purityFile.write(r"\\ ")
                    purityFile.write("\n")

                purityFile.write(r"\hline")
                purityFile.write("\n")
            
            purityFile.write(r"\end{tabular}")
            purityFile.write("\n")
            purityFile.write(r"\end{document}")
            purityFile.close()

            histograms[0][1].SetTitle("Purity for "+str(loc)+" "+str(pid)+" Photons in "+source)
            histograms[0][1].Draw()
            histograms[0][0].Draw("same")
            histograms[1][1].Draw("same")
            histograms[1][0].Draw("same")
            line = TLine(175.,1.,500.,1.)
            line.Draw("same")
        
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
