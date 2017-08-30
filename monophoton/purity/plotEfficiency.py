import os 
import sys
from pprint import pprint
import ROOT as r
from array import array
import math 

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if basedir not in sys.path:
    sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas, RatioCanvas, WEBDIR
from datasets import allsamples
import selections as s

versDir = WEBDIR + '/purity/' + s.Version
outDir = os.path.join(versDir, 'ScaleFactor')
if not os.path.exists(outDir):
    os.makedirs(outDir)

tune = 'GJetsCWIso'

outFile = r.TFile("../data/impurity_" + tune + ".root", "RECREATE")

bases = ['loose', 'medium', 'tight', 'highpt']
mods = ['', '-pixel'] #  '-pixel-monoph'
PhotonIds = [base+mod for base in bases for mod in mods]
PhotonPtSels = sorted(s.PhotonPtSels.keys())[:-1]
MetSels = sorted(s.MetSels.keys())[:2]

yields = {}
for loc in s.Locations[:1]:
    yields[loc] = {}
    for pid in PhotonIds:
        yields[loc][pid] = {}
        for ptCut in PhotonPtSels:
            yields[loc][pid][ptCut] = {}
            for metCut in MetSels: 
                yields[loc][pid][ptCut][metCut] = {}
                dirName = tune + '_' + loc+'_'+pid+'_'+ptCut+'_'+metCut
                print dirName

                # Get Data Yields
                dataFileName = os.path.join(versDir,dirName,"results.out") 
                match = False
                try:
                    dataFile = open(dataFileName)

                    count = [1., 0.]
                    for line in dataFile:
                        if "# of real photons is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                count[0] = float(tmp[-1].strip("(),"))
                                #print count
                        elif "Total unc yield is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                count[1] = float(tmp[-1].strip("(),"))
                                #print count

                        # dataFile.close()

                    dataFile.close()

                except IOError:
                    print "No data eff file found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['data'] = (-1., 0.0)
                    
                if match:
                    yields[loc][pid][ptCut][metCut]['data'] = tuple(count)

                else:
                    print "No data yields found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['data'] = (-1., 0.0)


                # get mc effs
                mcFileName = os.path.join(versDir,dirName,"mceff.out") 
                gjMatch = False
                wjMatch = False
                    
                try:
                    mcFile = open(mcFileName)

                    gjCount = [1., 0.]
                    wjCount = [1., 0.]

                    count = [1., 0.]
                    for line in mcFile:
                        if "gj04 efficiency" in line:
                            # print line
                            tmp = line.split()
                            if tmp: 
                                gjMatch = True
                                # pprint(tmp)
                                gjCount[0] = float(tmp[-4].strip("(),+-"))
                                gjCount[1] = float(tmp[-3].strip("(),+-"))
                                #print count

                        elif "wlnun efficiency" in line:
                            # print line
                            tmp = line.split()
                            if tmp: 
                                wjMatch = True
                                # pprint(tmp)
                                wjCount[0] = float(tmp[-4].strip("(),+-"))
                                wjCount[1] = 0.14 * wjCount[0]
                                #print count

                    mcFile.close()

                except IOError:
                    print "No mc eff file found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['mc'] = (-1., 0.0)

                    
                if gjMatch and wjMatch:
                    count[0] = gjCount[0] + wjCount[0]
                    count[1] = math.sqrt(gjCount[1]**2 + wjCount[1]**2)

                    yields[loc][pid][ptCut][metCut]['mc'] = tuple(count)

                else:
                    print "No mc yields file found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['mc'] = (-1., 0.0)
                    
                    
pprint(yields)

canvas = SimpleCanvas(lumi = s.sphLumi)
rcanvas = RatioCanvas(lumi = s.sphLumi)

for loc in s.Locations[:1]:
    for base in bases:
        print '\n' + base
        for metCut in MetSels:
            rcanvas.cd()
            rcanvas.Clear()
            rcanvas.legend.Clear()
            rcanvas.legend.setPosition(0.45, 0.725, 0.8, 0.925)

            canvas.cd()
            canvas.Clear()
            canvas.legend.Clear()
            canvas.legend.setPosition(0.45, 0.725, 0.8, 0.925)

            gDataEff = r.TGraphAsymmErrors()
            gDataEff.SetName(loc+'-'+base+mod+'-'+metCut+'-data')
            
            gMcEff = r.TGraphAsymmErrors()
            gMcEff.SetName(loc+'-'+base+mod+'-'+metCut+'-mc')
            
            gSF = r.TGraphAsymmErrors()
            gSF.SetName(loc+'-'+base+mod+'-'+metCut+'-sf')

            for iB, ptCut in enumerate(PhotonPtSels):
                if 'Inclusive' in ptCut:
                    lowEdge = 175.
                    highEdge = 500.
                else:
                    lowEdge = float(ptCut.split('t')[2])
                    highEdge = ptCut.split('to')[-1]
                    if highEdge == 'Inf':
                        highEdge = 500.
                    highEdge = float(highEdge)

                center = (lowEdge + highEdge) / 2.
                exl = center - lowEdge
                exh = highEdge - center
        
                mcPasses = yields[loc][base+mods[1]][ptCut][metCut]['mc']
                mcTotals = yields[loc][base+mods[0]][ptCut][metCut]['mc']

                mcEff = mcPasses[0] / mcTotals[0]
                mcCorr = mcEff
                mcEffError = mcEff * math.sqrt( (mcPasses[1]/mcPasses[0])**2 + (mcTotals[1]/mcTotals[0])**2 + 2*mcCorr*(mcPasses[1]/mcPasses[0])*(mcTotals[1]/mcPasses[0]) )


                gMcEff.SetPoint(iB, center, mcEff)
                gMcEff.SetPointError(iB, exl, exh, mcEffError, mcEffError)

                dataPasses = yields[loc][base+mods[1]][ptCut][metCut]['data']
                dataTotals = yields[loc][base+mods[0]][ptCut][metCut]['data']

                dataEff = dataPasses[0] / dataTotals[0]
                dataCorr = dataEff
                dataEffError = dataEff * math.sqrt( (dataPasses[1]/dataPasses[0])**2 + (dataTotals[1]/dataTotals[0])**2 + 2*dataCorr*(dataPasses[1]/dataPasses[0])*(dataTotals[1]/dataPasses[0]) )

                gDataEff.SetPoint(iB, center, dataEff)
                gDataEff.SetPointError(iB, exl, exh, dataEffError, dataEffError)
                
                # print ptCut, dataEffError, mcEffError

                sf = dataEff / mcEff
                sfErrLow = sf * math.sqrt( (dataEffError / dataEff)**2 + (mcEffError / mcEff)**2)
                sfErrHigh = sfErrLow
                gSF.SetPoint(iB, center, sf)
                gSF.SetPointError(iB, exl, exh, sfErrLow, sfErrHigh)

                outFile.cd()
                gMcEff.Write()
                gDataEff.Write()
                gSF.Write()

                # print ptCut, sf, sfErrLow

            rcanvas.legend.add("mc", title = 'mc ' + base, mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
            rcanvas.legend.apply("mc", gMcEff)
            rcanvas.addHistogram(gMcEff, drawOpt = 'EP')
            
            rcanvas.legend.add("data", title = "data " + base, mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 2)
            rcanvas.legend.apply("data", gDataEff)
            rcanvas.addHistogram(gDataEff, drawOpt = 'EP')

            canvas.legend.add(loc+'-'+base, title = loc+'-'+base, color = r.kBlack, lwidth = 2)
            canvas.legend.apply(loc+'-'+base, gSF)
            canvas.addHistogram(gSF, drawOpt = 'EP')
            
            rcanvas.ylimits = (0.5, 1.2)
            rcanvas.rlimits = (0.9, 1.1)
            rcanvas.ytitle = 'Pixel Veto Efficiency'
            rcanvas.xtitle = 'E_{T}^{#gamma} (GeV)'
            rcanvas.SetGridy(True)

            plotName = "efficiency_"+str(metCut)+"_"+str(loc)+"_"+str(base)
            rcanvas.printWeb('purity/'+s.Version+'/ScaleFactors', tune+'_'+plotName, logy = False)
            
            canvas.ylimits = (0.9, 1.1)
            canvas.ytitle = 'Pixel Veto Factor'
            canvas.xtitle = 'E_{T}^{#gamma} (GeV)'

            plotName = "scalefactor_"+str(metCut)+"_"+str(loc)+"_"+str(base)
            canvas.printWeb('purity/'+s.Version+'/ScaleFactors', tune+'_'+plotName, logy = False)

outFile.Close()
