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

            bins = [175, 500] # [175, 200, 250, 300, 350, 500]
            effs = {}

            for source in ['nero']: # , 'neromc']:
                hTrue = r.TH1F("ntrue"+loc+pid+metCut[0]+source, ";#gamma p_{T} (GeV)", len(bins)-1, array('d', bins))
                hTotal = r.TH1F("ntotal"+loc+pid+metCut[0]+source, ";#gamma p_{T} (GeV)", len(bins)-1, array('d', bins))
                hEff = r.TH1F("eff"+loc+pid+metCut[0]+source, ";#gamma p_{T} (GeV)", len(bins)-1, array('d', bins))

                gEff = r.TGraphAsymmErrors()
                gEff.SetName(loc+'-'+pid+'-'+metCut[0]+'-'+source)
                
                for ptCut in PhotonPtSels:
                    lowEdge = int(ptCut[0].split("t")[2])
                    binNumber = 0
                    for bin in bins:
                        if bin == lowEdge:
                            binNumber = bins.index(bin) + 1

                    passes = yields[source][loc][pid][ptCut[0]][metCut[0]]
                    totals = yields[source][loc]['none'][ptCut[0]][metCut[0]]

                    print passes
                    print totals
                    
                    hTrue.SetBinContent(binNumber, passes[0])
                    hTrue.SetBinError(binNumber, passes[1])

                    print hTrue.GetBinError(binNumber)
                    
                    hTotal.SetBinContent(binNumber, totals[0])
                    hTotal.SetBinError(binNumber, totals[1])
                    
                    print hTotal.GetBinError(binNumber)

                    eff = passes[0] / totals[0]
                    corr = eff
                    effError = eff * math.sqrt( (passes[1]/passes[0])**2 + (totals[1]/totals[0])**2 + 2*corr*(passes[1]/passes[0])*(totals[1]/passes[0]) )
              
                    print eff, effError
      
                    hEff.SetBinContent(binNumber, eff)
                    hEff.SetBinError(binNumber, effError)

                teff = r.TEfficiency(hTrue, hTotal)
                teff.SetStatisticOption(r.TEfficiency.kBBayesian)
                # gEff.Divide(hTrue, hTotal, "cl=0.683 b(1,1) mode")
                gEff = teff.CreateGraph()
                # effs[source] = gEff
                effs[source] = hEff


            #rcanvas.legend.add("mc", title = "MC", lcolor = r.kRed, lwidth = 2)
            #rcanvas.legend.apply("mc", effs['neromc'])
            #rcanvas.addHistogram(effs['neromc'], drawOpt = 'EP')

            rcanvas.legend.add("data", title = "Data", lcolor = r.kBlack, lwidth = 2)
            rcanvas.legend.apply("data", effs['nero'])
            rcanvas.addHistogram(effs['nero'], drawOpt = 'EP')

            # sys.stdin.readline()

            xeff = r.Double(0.)
            yeff = r.Double(0.)
            # effs['nero'].GetPoint(0, xeff, yeff)
            # print xeff, yeff, effs['nero'].GetErrorYhigh(0), effs['nero'].GetErrorYlow(0)

            rcanvas.ylimits = (0.0, 1.1)
            rcanvas.ytitle = 'Photon Efficiency'
            rcanvas.xtitle = 'E_{T}^{#gamma} (GeV)'

            plotName = "efficiency_"+str(loc)+"_"+str(pid)
            rcanvas.printWeb('purity/'+s.Version+'/ScaleFactors', plotName, logy = False)
