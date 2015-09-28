import os
from ROOT import *
from selections import Variables, Version, Measurement, Selections, TemplateMaker

varName = 'sieie'
var = Variables[varName]

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "MonophotonBkgdComp"
skims = Measurement[skimName] 
selKeys = [skimName]

tempInfo = [ ('total','Total',kSolid,kBlack,'L')
             ,('true','True Photons',kDashed,kGreen,'L')
             ,('hdecay','Hadron Decay',kDashed,kBlue,'L')
             ,('misreco',"Mis-Reco'd",kDashed,kRed,'L') ]

garbage = []
templates = []
for selKey in selKeys:
    for skim,sel,name in zip(skims,Selections[selKey],tempInfo):
        template = TemplateMaker(var,skim,sel,selKey,skimDir,plotDir)   
        garbage.append(template)
        tempPdf = RooHistPdf(name[0],name[0],RooArgSet(var[3]),template)
        templates.append(tempPdf)

canvas = TCanvas()
frame = var[3].frame()
frame.SetTitle('Background Composition of QCD Sideband for Monophoton')

leg = TLegend(0.6,0.6,0.85,0.75 );
leg.SetFillColor(kWhite);
leg.SetTextSize(0.03);

for template,info in zip(templates,tempInfo):
    print info[0], info[1], info[2], info[3], info[4]
    template.plotOn(frame, RooFit.Name(info[0]), RooFit.LineStyle(info[2]), RooFit.LineColor(info[3]))
    leg.AddEntry(frame.findObject(info[0]), info[1], info[4]);

frame.Draw("goff")
leg.Draw("goff");

outName = os.path.join(plotDir,'composition_BkgdQCD_Monophoton.pdf')
canvas.SaveAs(outName)
