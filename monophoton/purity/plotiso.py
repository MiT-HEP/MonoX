import os
import sys
from array import array
from pprint import pprint
from selections import Variables, Version, Samples, Measurement, SigmaIetaIetaSels, chIsoCuts, sieieSels, PhotonPtSels, MetSels, HistExtractor, config, versionDir
from ROOT import *
gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

if basedir not in sys.path:
    sys.path.append(basedir)

from datasets import allsamples
import config

def plotiso(loc, pid, pt, met, era):
    inputKey = era+'_'+loc+'_'+pid+'_PhotonPt'+pt+'_Met'+met
    
    if loc == 'barrel':
        iloc = 0
    elif loc == 'endcap':
        iloc = 1
    
    try:
        ptSel = PhotonPtSels['PhotonPt'+pt]
    except KeyError:
        print 'Inputted pt range', pt, 'not found!'
        print 'Not applying any pt selection!'
        ptSel = '(1)'
    
    try:
        metSel = MetSels['Met'+met]
    except KeyError:
        print 'Inputted met range', met, 'not found!'
        print 'Not applying any met selection!'
        metSel = '(1)'
    
    varName = 'chiso'
    var = Variables[varName]
    
    versDir = versionDir
    skimDir = config.skimDir
    plotDir = os.path.join(versDir,inputKey)
    if not os.path.exists(plotDir):
        os.makedirs(plotDir)
    
    skim = Measurement['bambu'][1]
    
    pids = pid.split('-')
    if len(pids) > 1:
        pid = pids[0]
        extras = pids[2:]
    elif len(pids) == 1:
        pid = pids[0]
        extras = []

    # selection on H/E & INH & IPh
    baseSel = SigmaIetaIetaSels[era][loc][pid]+' && '+ptSel+' && '+metSel
    if 'pixel' in extras:
        baseSel = baseSel+' && '+s.pixelVetoCut
    if 'monoph' in extras:
        baseSel = baseSel+' && '+s.monophIdCut
    if 'max' in extras:
        baseSel = baseSel.replace('chIso', 'chIsoMax')
        var = ('TMath::Max(0., photons.chIsoMax)',) + var[1:]
    
    outName = os.path.join(plotDir,'chiso_'+inputKey)
    print 'plotiso writing to', outName+'.root'
    outFile = TFile(outName+'.root','RECREATE')
    
    histograms = [ [], [], [], [] ]
    leg = TLegend(0.725,0.7,0.875,0.85 );
    leg.SetFillColor(kWhite);
    leg.SetTextSize(0.03);
    
    colors = [kBlue, kRed, kBlack]
    
    truthSel = '(photons.matchedGenId == -22)'

    # don't use var[3][iloc] for binning
    binning = [0., chIsoCuts[era][loc][pid]] + [0.1 * x for x in range(20, 111, 5)]

    # make the data iso distribution for reference
    extractor = HistExtractor('sphData', Samples['sphData'], var[0])
    print 'setBaseSelection(' + baseSel + ')'
    extractor.plotter.setBaseSelection(baseSel)
    extractor.categories.append((skim[0], skim[2], ''))
    hist = extractor.extract(binning)[0]
    hist.SetName("data")
    histograms[3].append(hist)

    extractor = HistExtractor('gjetsMc', Samples[skim[1]], var[0])
    print 'setBaseSelection(' + baseSel + ' && ' + truthSel + ')'
    extractor.plotter.setBaseSelection(baseSel + ' && ' + truthSel)
    extractor.categories.append((skim[0], skim[2], ''))
    raw = extractor.extract(binning)[0]
    raw.SetName("rawmc")
    histograms[0].append(raw)

#    eSelScratch = "weight * ( (tp.mass > 81 && tp.mass < 101) && "+SigmaIetaIetaSels[era][loc][pid]+' && '+metSel+" && "+sieieSels[era][loc][pid]+")"
    eSelScratch = "(tp.mass > 81 && tp.mass < 101) && "+SigmaIetaIetaSels[era][loc][pid]+' && '+metSel+" && "+sieieSels[era][loc][pid]
    eSel = eSelScratch.replace("photons", "probes")
    eExpr = var[0].replace('photons', 'probes')

    print 'Extracting electron MC distributions'

# tpeg trees lack the weight branch as of now (Jun 07) - looping over samples.
#    mcTree = TChain('events')
#    mcTree.Add(os.path.join(skimDir, 'dy-50-*_tpeg.root'))

    print 'Draw(' + eExpr + ', ' + eSel + ')'
    
    mcHist = raw.Clone("emc")
    mcHist.Reset()
#    mcTree.Draw("TMath::Max(0., probes.chIso)>>emc", eSel, 'goff')
    for sample in allsamples.getmany('dy-50-*'):
        source = TFile.Open(config.skimDir + '/' + sample.name + '_tpeg.root')
        tree = source.Get('events')
        outFile.cd()
        tree.Draw(eExpr + ">>+emc", '%f * (%s)' % (sample.crosssection / sample.sumw, eSel), 'goff')
        source.Close()

    outFile.WriteTObject(mcHist)
    histograms[1].append(mcHist)

    print 'Extracting electron data distributions'
    
    dataTree = TChain('events')
    dataTree.Add(os.path.join(skimDir, 'sph-16*_tpeg.root'))
    dataHist = raw.Clone("edata")
    dataHist.Reset()
    print 'Draw(' + eExpr + ', ' + eSel + ')'
    dataTree.Draw(eExpr + ">>edata", eSel, 'goff')
    outFile.WriteTObject(dataHist)
    histograms[1].append(dataHist)

    scaled = raw.Clone("scaledmc")
    scaleHist = raw.Clone("escale")
    scaleHist.SetTitle("Data/MC Scale Factors from Electrons")
    scaleHist.Reset()
    for iBin in range(1,scaleHist.GetNbinsX()+1):
        dataValue = dataHist.GetBinContent(iBin)
        dataError = dataHist.GetBinError(iBin)
    
        mcValue = mcHist.GetBinContent(iBin)
        mcError = mcHist.GetBinError(iBin)
    
        if mcValue == 0 or dataValue == 0:
            ratio = 1
            error = 0.05
        else:
            ratio = dataValue / mcValue 
            error = ratio * ( (dataError / dataValue)**2 + (mcError / mcValue)**2 )**(0.5)
    
        scaleHist.SetBinContent(iBin, ratio)
        scaled.SetBinContent(iBin, ratio * scaled.GetBinContent(iBin))
        scaleHist.SetBinError(iBin, error)
    
    outFile.WriteTObject(scaleHist)
    histograms[0].append(scaled)
    histograms[2].append(scaleHist)
    
    suffix = [ ("photons", "Events"), ("electrons", "Events"), ("scale", "Scale Factor"), ("data", "Events") ]
    
    for iList, hlist in enumerate(histograms):
        canvas = TCanvas()
        for iHist, hist in enumerate(hlist):
            if (iList < 2): 
                hist.Scale( 1. / hist.GetSumOfWeights())
    
            hist.SetLineColor(iHist+1)
            hist.SetLineWidth(3)
            if (iList < 2): 
                hist.SetLineStyle(kDashed)
            hist.SetStats(False)
        
            hist.GetXaxis().SetTitle("CH Iso (GeV)")
            hist.GetYaxis().SetTitle(suffix[iList][1])
            
            hist.GetXaxis().SetLabelSize(0.045)
            hist.GetXaxis().SetTitleSize(0.045)
            hist.GetYaxis().SetLabelSize(0.045)
            hist.GetYaxis().SetTitleSize(0.045)
    
            outFile.cd()
            hist.Write()
            
            canvas.cd()
            if (iHist == 0):
                if (iList < 2): 
                    hist.Draw("hist")
                else:
                    hist.Draw("")
            else:
                hist.Draw("samehist")
            leg.AddEntry(hist, hist.GetName(), 'L')
    
        canvas.cd()
        if (iList < 2): 
            leg.Draw()
    
        newName = outName+'_'+suffix[iList][0]
    
        canvas.SaveAs(newName+'.pdf')
        canvas.SaveAs(newName+'.png')
        canvas.SaveAs(newName+'.C')
        
        canvas.SetLogy()
        canvas.SaveAs(newName+'_Logy.pdf')
        canvas.SaveAs(newName+'_Logy.png')
        canvas.SaveAs(newName+'_Logy.C')
        
        
        leg.Clear()
    outFile.Close()


if __name__ == '__main__':
    import sys

    loc = sys.argv[1]
    pid = sys.argv[2]
    pt = sys.argv[3]
    met = sys.argv[4]
    
    try:
        era = sys.argv[5]
    except:
        era = 'Spring15'

    plotiso(loc, pid, pt, met, era)
