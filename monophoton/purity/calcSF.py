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
from plotstyle import SimpleCanvas, RatioCanvas

import selections as s

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',s.Version,varName)
plotDir = os.path.join(versDir, 'Plots', 'SignalContam') 
outDir = os.path.join(plotDir, 'ScaleFactor')
if not os.path.exists(outDir):
    os.makedirs(outDir)

yields = {}
PhotonIds = ['medium_pixel_monoph']
PhotonPtSels = s.PhotonPtSels[:1]

for source in ['nero']:
    yields[source] = {}
    for loc in s.Locations[:1]:
        yields[source][loc] = {}
        for pid in PhotonIds + ['none']:
            yields[source][loc][pid] = {}
            for ptCut in PhotonPtSels:
                yields[source][loc][pid][ptCut[0]] = {}
                for metCut in s.MetSels[1:2]:
                    tempyields = {}

                    for chiso in s.ChIsoSbSels[:]:
                        dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                        condorFileName = os.path.join(plotDir,source,dirName,"results.out") 
                        # print condorFileName
                        condorFile = open(condorFileName)
                        
                        match = False
                        count = [1., 0.]
                        for line in condorFile:
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

                        tempyields[chiso[0]] = count

                        if not match:
                            print "No yield found for skim:", source, dirName
                            tempyields[chiso[0]] = (-1., 0.0)
                        condorFile.close()

                    nReal = tempyields[s.ChIsoSbSels[1][0]][0]
                    unc = tempyields[s.ChIsoSbSels[1][0]][1]
                    sbUnc = max(abs(nReal - tempyields[s.ChIsoSbSels[0][0]][0]),
                                    abs(nReal - tempyields[s.ChIsoSbSels[2][0]][0]))
                    totalUnc = (unc**2 + sbUnc**2)**(0.5)

                    yields[source][loc][pid][ptCut[0]][metCut[0]] = (nReal, totalUnc)

for source in ['neromc']:
    yields[source] = {}
    for loc in s.Locations[:1]:
        yields[source][loc] = {}
        for pid in PhotonIds:
            yields[source][loc][pid] = {}
            for ptCut in PhotonPtSels:
                yields[source][loc][pid][ptCut[0]] = {}
                for metCut in s.MetSels[1:2]:                        
                    dirName = loc+'_'+pid+'_ChIso50to80_'+ptCut[0]+'_'+metCut[0] 
                    condorFileName = os.path.join(plotDir,source,dirName,"mceff.out") 
                    # print condorFileName
                    condorFile = open(condorFileName)
                        
                    match = False
                    count = [1., 0., 0.]
                    for line in condorFile:
                        if "Efficiency" in line:
                            print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                pprint(tmp)
                                count[0] = float(tmp[-3].strip("(),+-"))
                                count[1] = float(tmp[-2].strip("(),+-"))
                                count[2] = float(tmp[-1].strip("(),+-"))
                                #print count

                    if not match:
                        print "No yield found for skim:", source, dirName
                        yields[source][loc][pid][ptCut[0]][metCut[0]] = (-1., 0.0, 0.0)
                    condorFile.close()

                    yields[source][loc][pid][ptCut[0]][metCut[0]] = count
                    
pprint(yields)

canvas = SimpleCanvas(lumi = config.jsonLumi)
rcanvas = RatioCanvas(lumi = config.jsonLumi)

for loc in s.Locations[:1]:
    for pid in PhotonIds:
        for metCut in s.MetSels[1:2]:
            rcanvas.cd()
            rcanvas.Clear()
            rcanvas.legend.Clear()
            rcanvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)

            dataEff = r.TGraphAsymmErrors()
            dataEff.SetName(loc+'-'+pid+'-'+metCut[0]+'-data')
            
            mcEff = r.TGraphAsymmErrors()
            mcEff.SetName(loc+'-'+pid+'-'+metCut[0]+'-mc')

            gSF = r.TGraphAsymmErrors()
            gSF.SetName(loc+'-'+pid+'-'+metCut[0]+'-sf')

            for iB, ptCut in enumerate(PhotonPtSels):
                lowEdge = float(ptCut[0].split('t')[2])
                highEdge = ptCut[0].split('to')[-1]
                if highEdge == 'Inf':
                    highEdge = 500.
                highEdge = float(highEdge)
                
                center = (lowEdge + highEdge) / 2.
                exl = center - lowEdge
                exh = highEdge - center

                mceffs = yields['neromc'][loc][pid][ptCut[0]][metCut[0]]
                mcEff.SetPoint(iB, center, mceffs[0])
                mcEff.SetPointError(iB, exl, exh, mceffs[2], mceffs[1])

                passes = yields['nero'][loc][pid][ptCut[0]][metCut[0]]
                totals = yields['nero'][loc]['none'][ptCut[0]][metCut[0]]

                eff = passes[0] / totals[0]
                corr = eff
                effError = eff * math.sqrt( (passes[1]/passes[0])**2 + (totals[1]/totals[0])**2 + 2*corr*(passes[1]/passes[0])*(totals[1]/passes[0]) )
              
                dataEff.SetPoint(iB, center, eff)
                dataEff.SetPointError(iB, exl, exh, effError, effError)

                sf = eff / mceffs[0]
                sfErrLow = effError / mceffs[0]
                sfErrHigh = effError / mceffs[0]
                gSF.SetPoint(iB, center, sf)
                gSF.SetPointError(iB, exl, exh, sfErrLow, sfErrHigh)

                print sf, sfErrLow, sfErrLow / sf

            rcanvas.legend.add("mc", title = "MC", mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
            rcanvas.legend.apply("mc", mcEff)
            rcanvas.addHistogram(mcEff, drawOpt = 'EP')

            rcanvas.legend.add("data", title = "Data", lcolor = r.kBlack, lwidth = 2)
            rcanvas.legend.apply("data", dataEff)
            rcanvas.addHistogram(dataEff, drawOpt = 'EP')

            rcanvas.ylimits = (0.0, 1.1)
            rcanvas.ytitle = 'Photon Efficiency'
            rcanvas.xtitle = 'E_{T}^{#gamma} (GeV)'

            plotName = "efficiency_"+str(loc)+"_"+str(pid)
            rcanvas.printWeb('purity/'+s.Version+'/ScaleFactors', plotName, logy = False)
                
            canvas.legend.add(loc+'-'+pid, title = loc+'-'+pid, color = r.kBlack, lwidth = 2)
            canvas.legend.apply(loc+'-'+pid, gSF)
            canvas.addHistogram(gSF, drawOpt = 'EP')
            
            canvas.ylimits = (0.0, 2.0)
            canvas.ytitle = 'Photon Scale Factor'
            canvas.xtitle = 'E_{T}^{#gamma} (GeV)'

            plotName = "scalefactor_"+str(loc)+"_"+str(pid)
            canvas.printWeb('purity/'+s.Version+'/ScaleFactors', plotName, logy = False)
