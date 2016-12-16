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

PhotonIds = ['loose', 'medium', 'tight', 'highpt']
for pid in list(PhotonIds):
    PhotonIds += [pid+'-pixel', pid+'-pixel-monoph']
PhotonPtSels = sorted(s.PhotonPtSels.keys())[:-1]
MetSels = sorted(s.MetSels.keys())[:1]

era = 'Spring15'

yields = {}
for loc in s.Locations[:1]:
    yields[loc] = {}
    for pid in PhotonIds + ['none']:
        yields[loc][pid] = {}
        for ptCut in PhotonPtSels:
            yields[loc][pid][ptCut] = {}
            for metCut in MetSels: 
                yields[loc][pid][ptCut][metCut] = {}
                dirName = era + '_' + loc+'_'+pid+'_'+ptCut+'_'+metCut
                print dirName
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
                        # print line
                        tmp = line.split()
                        if tmp:
                            match = True
                            # pprint(tmp)
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
rcanvas = SimpleCanvas(lumi = sphLumi)

PhotonIds = ['loose', 'medium', 'tight', 'highpt']

for loc in s.Locations[:1]:
    for pid in PhotonIds:
        for metCut in MetSels:
            rcanvas.cd()
            rcanvas.Clear()
            rcanvas.legend.Clear()
            rcanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

            for iMod, mod in enumerate(['', '-pixel', '-pixel-monoph']):

                dataEff = r.TGraphAsymmErrors()
                dataEff.SetName(loc+'-'+pid+mod+'-'+metCut+'-data')

                mcEff = r.TGraphAsymmErrors()
                mcEff.SetName(loc+'-'+pid+mod+'-'+metCut+'-mc')

                gSF = r.TGraphAsymmErrors()
                gSF.SetName(loc+'-'+pid+mod+'-'+metCut+'-sf')

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

                    mceffs = yields[loc][pid+mod][ptCut][metCut]['mc']
                    mcEff.SetPoint(iB, center, mceffs[0])
                    mcEff.SetPointError(iB, exl, exh, mceffs[2], mceffs[1])

                    passes = yields[loc][pid+mod][ptCut][metCut]['data']
                    totals = yields[loc]['none'][ptCut][metCut]['data']

                    # print passes
                    # print totals

                    eff = passes[0] / totals[0]
                    corr = eff
                    effError = eff * math.sqrt( (passes[1]/passes[0])**2 + (totals[1]/totals[0])**2 + 2*corr*(passes[1]/passes[0])*(totals[1]/passes[0]) )

                    # print eff
                    # print effError

                    dataEff.SetPoint(iB, center, eff)
                    dataEff.SetPointError(iB, exl, exh, effError, effError)

                    sf = eff / mceffs[0]
                    sfErrLow = effError / mceffs[0]
                    sfErrHigh = effError / mceffs[0]
                    gSF.SetPoint(iB, center, sf)
                    gSF.SetPointError(iB, exl, exh, sfErrLow, sfErrHigh)

                    # print sf, sfErrLow, sfErrLow / sf

                rcanvas.legend.add("mc"+mod, title = pid+mod, mcolor = r.kRed+iMod, lcolor = r.kRed+iMod, lwidth = 2)
                rcanvas.legend.apply("mc"+mod, mcEff)
                rcanvas.addHistogram(mcEff, drawOpt = 'EP')

                # rcanvas.legend.add("data"+mod, title = "Data"+mod, mcolor = r.Blue+iMod, lcolor = r.kBlue+iMod, lwidth = 2)
                # rcanvas.legend.apply("data"+mod, dataEff)
                # rcanvas.addHistogram(dataEff, drawOpt = 'EP')

                canvas.legend.add(loc+'-'+pid+mod, title = loc+'-'+pid+mod, color = r.kBlack+iMod, lwidth = 2)
                canvas.legend.apply(loc+'-'+pid+mod, gSF)
                canvas.addHistogram(gSF, drawOpt = 'EP')

            rcanvas.ylimits = (0.0, 1.1)
            rcanvas.ytitle = 'Photon Efficiency'
            rcanvas.xtitle = 'E_{T}^{#gamma} (GeV)'
            rcanvas.SetGridy(True)

            plotName = "efficiency_"+str(loc)+"_"+str(pid)
            rcanvas.printWeb('purity/'+s.Version+'/ScaleFactors', era+'_'+plotName, logy = False)
            
            # canvas.ylimits = (0.0, 2.0)
            canvas.ytitle = 'Photon Scale Factor'
            canvas.xtitle = 'E_{T}^{#gamma} (GeV)'

            plotName = "scalefactor_"+str(loc)+"_"+str(pid)
            # canvas.printWeb('purity/'+s.Version+'/ScaleFactors', plotName, logy = False)
