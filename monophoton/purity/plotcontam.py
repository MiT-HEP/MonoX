import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
from ROOT import *
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.axes as axes
from scipy.optimize import leastsq
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
# gROOT.SetBatch(True)

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
plotDir = os.path.join(versDir, 'Plots', 'SignalContam') 
outDir = os.path.join(plotDir, 'Fitting')
if not os.path.exists(outDir):
    os.makedirs(outDir)

purities = {}

for loc in Locations[:1]:
    purities[loc] = {}
    for pid in PhotonIds[1:2]:
        purities[loc][pid] = {}
        for ptCut in PhotonPtSels[0][1:]:
            purities[loc][pid][ptCut[0]] = {}
            for metCut in MetSels[:1]:
                purities[loc][pid][ptCut[0]][metCut[0]] = {}
                
                purityFileName = "purity_data_"+loc+"_"+pid+"_"+ptCut[0]+"_"+metCut[0]+"_ex.tex"
                purityFilePath = os.path.join(outDir,purityFileName)
                purityFile = open(purityFilePath, "w")
                
                purityFile.write(r"\documentclass{article}")
                purityFile.write("\n")
                purityFile.write(r"\usepackage[paperheight=2in, paperwidth=8in]{geometry}")
                purityFile.write("\n")
                purityFile.write(r"\begin{document}")
                purityFile.write("\n")
                purityFile.write(r"\pagenumbering{gobble}")
                purityFile.write("\n")
                
                purityFile.write(r"\begin{tabular}{ |l|l l|l l l| }")
                purityFile.write("\n")
                purityFile.write(r"\hline")
                purityFile.write("\n")
                ptRange = ptCut[0].strip("PhotonPt").split("to")
                purityFile.write(r"\multicolumn{6}{ |c| }{Purities for "+loc+" "+pid+r" photons with $p_{T} \in$ ["+ptRange[0]+","+ptRange[1]+r"] GeV} \\")
                purityFile.write("\n")
                purityFile.write(r"\hline \hline")
                purityFile.write("\n")
                
                purityFile.write(r"CH Iso SB & Impurity ")
                purityFile.write(r"& Total Unc. ")
                purityFile.write(r"& CH Iso Shape ")
                purityFile.write(r"& Signal Shape ")
                purityFile.write(r"& Background Shape ")
                purityFile.write(r"\\ \hline")
                purityFile.write("\n")

                for chiso in ChIsoSbSels[:]:
                    purities[loc][pid][ptCut[0]][metCut[0]][chiso[0]] = {}
                        
                    dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                    condorFileName = os.path.join(plotDir,dirName,"condor.out") 
                    # print condorFileName
                    condorFile = open(condorFileName)
                    
                    match = False
                    purity = [1, 0, 0, 0, 0]
                    for line in condorFile:
                        if "Nominal purity is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[0] = (1.0 - float(tmp[-1].strip("(),"))) * 100
                                # print purity[0]
                        elif "Total uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[-1] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Method uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[1] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Signal shape uncertainty is:" in line: # need to add t back
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[2] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Background stat uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[3] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                    purities[loc][pid][ptCut[0]][metCut[0]][chiso[0]] = purity 
                        
                    purityFile.write(chiso[0].strip("ChIso")+" ")
                    for value in purity[:1]+purity[-1:]+purity[1:-1]:
                        purityFile.write(r" & "+str(round(value,3)))
                    purityFile.write(r"\\")
                    purityFile.write("\n")

                    if not match:
                        print "No purity found for skim:", dirName
                        purities[loc][pid][ptCut[0]][metCut[0]][chiso[0]] = (1.025, 0.0)
                    condorFile.close()
                purityFile.write(r"\hline")
                purityFile.write("\n")
                purityFile.write(r"\end{tabular}")
                purityFile.write("\n")
                purityFile.write(r"\end{document}")
                purityFile.close()

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
pprint(purities)

colors = ['r','b','g','m','k']

for loc in Locations[:1]:
    for pid in PhotonIds[1:2]:
        for ptCut in PhotonPtSels[0][1:]:
            for metCut in MetSels[:1]:
                isoVals = np.asarray([ float(key.split('o')[1].strip('t'))/10.0 for key in sorted(purities[loc][pid][ptCut[0]][metCut[0]]) ])
                    #isoVals = np.arange(2.0,8.5,0.5)
                puritiesCalc = ( np.asarray(  [ value[0] for key, value in sorted(purities[loc][pid][ptCut[0]][metCut[0]].iteritems()) ])
                                 ,np.asarray( [ abs(value[-1]) for key, value in sorted(purities[loc][pid][ptCut[0]][metCut[0]].iteritems()) ]) )
                pprint(isoVals)
                pprint(puritiesCalc)

                params = [ 0.01, 10.0 ]
                paramsInit = params

                def purityFunc(_params, _iso):
                    purity_ = _params[0] # + _params[1] * _iso
                    return purity_
                    
                def resFunc(_params, _iso, _purity):
                    err = ( _purity[0] - purityFunc(_params, _iso) ) / _purity[1]
                    return err

                    
                paramsFit = leastsq(resFunc, paramsInit, args=(isoVals, puritiesCalc), full_output=1, warning=True )
                pprint(paramsFit)

                isosFit = np.arange(0.0,10.5,0.5)
                puritiesFit = [ purityFunc(paramsFit[0], iso) for iso in  isosFit]
                #pprint(isosFit)
                #pprint(puritiesFit)
                    
                    
                plot.figure()
                # plot.errorbar(isoVals, puritiesCalc[0], yerr=puritiesCalc[1], fmt=colors[PhotonPtSels[0][1:].index(ptCut)]+'o', markersize=8.0, capsize=8, solid_capstyle='projecting', elinewidth=2)
                plot.errorbar(isoVals, puritiesCalc[0], yerr=puritiesCalc[1], fmt='ko', markersize=8.0, capsize=8, solid_capstyle='projecting', elinewidth=2)
                plot.plot(isosFit, puritiesFit, 'r-', linewidth=1.0)
                # plot.legend(['Measured', 'Fit'])
                plot.xlim(0.,10.)
                plot.ylim(0.0,10.0)
                # plot.ylim(2.5,7.5)
                plot.tick_params(axis='both', which='major', labelsize=16)
                plot.ylabel(r'Impurity (%)', fontsize=24)
                plot.xlabel(r'Charged Hadron Isolation (GeV)', fontsize=24)
                outName = os.path.join(outDir,'purityfit_'+loc+'_'+pid+'_'+ptCut[0]+'_'+metCut[0]+'_ex')
                plot.savefig(outName+'.pdf', format='pdf')
                plot.savefig(outName+'.png', format='png')


for loc in Locations[:1]:
    for pid in PhotonIds[1:2]:
        for metCut in MetSels[:1]:
            purityFileName = "purity_data_"+loc+"_"+pid+"_ptbinned_table.tex"
            purityFilePath = os.path.join(outDir,purityFileName)
            purityFile = open(purityFilePath, "w")
            
            purityFile.write(r"\documentclass{article}")
            purityFile.write("\n")
            purityFile.write(r"\usepackage[paperheight=1.5in, paperwidth=8in]{geometry}")
            purityFile.write(r"\begin{document}")
            purityFile.write("\n")

            purityFile.write(r"\begin{tabular}{ |r|c|c|c|c|c| }")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            purityFile.write(r"\multicolumn{6}{ |c| }{Purities for "+loc+" "+pid+r" photons in data} \\")
            purityFile.write("\n")
            purityFile.write(r"\hline")
            purityFile.write("\n")
            

            purityFile.write(r"photon\ $p_{T}$ ")
            for ptCut in PhotonPtSels[0][1:]:
                purityFile.write(r"& "+ptCut[0].strip("PhotonPt")+" ")
            purityFile.write(r"\\ \hline")
            purityFile.write("\n")

            
            histograms = [ [], [] ]
            
            leg = TLegend(0.625,0.65,0.875,0.85)
            leg.SetFillColor(kWhite)
            leg.SetTextSize(0.045)
                
            lineColors = [ kBlue, kBlack, kRed ]
            
            bins = [175, 200, 250, 300, 350, 500]

            for chiso in ChIsoSbSels:                
                purityFile.write(chiso[0]+" ")
                
                hists = [] 

                himp =  TH1F(chiso[0]+"imp",chiso[0]+"imp",(len(bins)-1),array('d',bins))
                himp.GetYaxis().SetTitle("Impurity (%)")
                himp.SetMaximum(10.)
                hists.append(himp)

                herr = TH1F(chiso[0]+"err",chiso[0]+"err",(len(bins)-1),array('d',bins))
                herr.GetYaxis().SetTitle("Percent Error on Impurity (%)")
                herr.SetMaximum(100.)
                hists.append(herr)
                
                for hist in hists:
                    hist.GetXaxis().SetTitle("#gamma p_{T} (GeV)")
                    
                    
                    hist.SetMinimum(0.0)
                    hist.SetLineColor(lineColors[ChIsoSbSels.index(chiso)])
                    hist.SetLineWidth(3)
                    hist.SetStats(False)
                    
                    hist.GetXaxis().SetLabelSize(0.045)
                    hist.GetXaxis().SetTitleSize(0.045)
                    hist.GetYaxis().SetLabelSize(0.045)
                    hist.GetYaxis().SetTitleSize(0.045)

                leg.AddEntry(hist,chiso[0],'L')
            
                for ptCut in PhotonPtSels[0][1:]:
                    lowEdge = int(ptCut[0].split("t")[2])
                    binNumber = 0
                    for bin in bins:
                        if bin == lowEdge:
                            binNumber = bins.index(bin) + 1
   
                    impurity = float(purities[loc][pid][ptCut[0]][metCut[0]][chiso[0]][0])
                    uncertainty = float(purities[loc][pid][ptCut[0]][metCut[0]][chiso[0]][-1])
                    # print binNumber, purity, uncertainty
                    purityFile.write(r"& "+str(round(impurity,3))+r" $\pm$ "+str(round(uncertainty,3))+" ")
                    hists[0].SetBinContent(binNumber, impurity)
                    hists[1].SetBinContent(binNumber, uncertainty/impurity * 100)
                                
                histograms[0].append(hists[0])
                histograms[1].append(hists[1])
                purityFile.write(r"\\ \hline")
                purityFile.write("\n")
            
            purityFile.write(r"\end{tabular}")
            purityFile.write("\n")
            purityFile.write(r"\end{document}")
            purityFile.close()

            histograms[0][0].SetTitle("Impurity for "+str(loc)+" "+str(pid)+" Photons in data")
            histograms[1][0].SetTitle("Error on Impurity for "+str(loc)+" "+str(pid)+" Photons in data")
            suffix = [ "central", "error" ] 
            for hlist in histograms:
                canvas = TCanvas()
                hlist[0].Draw()
                hlist[2].Draw("same")
                hlist[1].Draw("same")
        
                leg.Draw()
                plotName = "purity_data_"+str(loc)+"_"+str(pid)+"_ptbinned_"+suffix[histograms.index(hlist)] 
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
