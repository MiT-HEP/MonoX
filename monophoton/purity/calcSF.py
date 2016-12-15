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
from datasets import allsamples
import selections as s

versDir = os.path.join('/data/t3home000/ballen/hist/purity',s.Version)
outDir = os.path.join(versDir, 'ScaleFactor')
if not os.path.exists(outDir):
    os.makedirs(outDir)

PhotonIds = ['medium-pixel-monoph']
PhotonPtSels = sorted(s.PhotonPtSels.keys())[-1:]
MetSels = sorted(s.MetSels.keys())[:1]

yields = {}
for loc in s.Locations[:1]:
    yields[loc] = {}
    for pid in PhotonIds + ['none']:
        yields[loc][pid] = {}
        for ptCut in PhotonPtSels:
            yields[loc][pid][ptCut] = {}
            for metCut in MetSels: 
                yields[loc][pid][ptCut][metCut] = {}
                dirName = 'Spring15' + '_' + loc+'_'+pid+'_'+ptCut+'_'+metCut
 
                # Get Data Yields
                dataFileName = os.path.join(versDir,dirName,"results.out") 
                dataFile = open(dataFileName)
                
                match = False
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

                if not match:
                    print "No data yields found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['data'] = (-1., 0.0)
                dataFile.close()
                
                yields[loc][pid][ptCut][metCut]['data'] = tuple(count)

                if pid == 'none':
                    continue

                # get mc effs
                mcFileName = os.path.join(versDir,dirName,"mceff.out") 
                mcFile = open(mcFileName)

                match = False
                count = [1., 0., 0.]
                for line in mcFile:
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
                    print "No mc eff found for skim:", dirName
                    yields[loc][pid][ptCut][metCut]['mc'] = (-1., 0.0, 0.0)
                mcFile.close()

                yields[loc][pid][ptCut][metCut]['mc'] = tuple(count)
                    
pprint(yields)


sphLumi = sum(allsamples[s].lumi for s in ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h1', 'sph-16h2', 'sph-16h3'])
canvas = SimpleCanvas(lumi = sphLumi)
rcanvas = RatioCanvas(lumi = sphLumi)

for loc in s.Locations[:1]:
    for pid in PhotonIds:
        for metCut in MetSels:
            rcanvas.cd()
            rcanvas.Clear()
            rcanvas.legend.Clear()
            rcanvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)

            dataEff = r.TGraphAsymmErrors()
            dataEff.SetName(loc+'-'+pid+'-'+metCut+'-data')
            
            mcEff = r.TGraphAsymmErrors()
            mcEff.SetName(loc+'-'+pid+'-'+metCut+'-mc')

            gSF = r.TGraphAsymmErrors()
            gSF.SetName(loc+'-'+pid+'-'+metCut+'-sf')

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

                mceffs = yields[loc][pid][ptCut][metCut]['mc']
                mcEff.SetPoint(iB, center, mceffs[0])
                mcEff.SetPointError(iB, exl, exh, mceffs[2], mceffs[1])

                passes = yields[loc][pid][ptCut][metCut]['data']
                totals = yields[loc]['none'][ptCut][metCut]['data']

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
