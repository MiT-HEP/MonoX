import sys
import os
import array
import math
import re
import collections
import ROOT

def truncateContour(contour, base):
    x = ROOT.Double()
    y = ROOT.Double()

    iP = contour.GetN() - 1
    while iP >= 0:
        contour.GetPoint(iP, x, y)
        if base.GetBinContent(base.FindBin(x, y)) != 0.:
            break

        iP -= 1
        
    contour.Set(iP + 1)

    iP = 0
    while iP < contour.GetN():
        contour.GetPoint(iP, x, y)
        if base.GetBinContent(base.FindBin(x, y)) != 0.:
            break

        iP += 1

    shift = iP
    for iP in range(contour.GetN() - shift):
        contour.GetPoint(iP + shift, x, y)
        contour.SetPoint(iP, x, y)

    contour.Set(contour.GetN() - shift)

def closeContour(contour, base):
    # currently disabled

    x = ROOT.Double()
    y = ROOT.Double()

    contour.GetPoint(0, x, y)
    xBegin = float(x)
    yBegin = float(y)
    contour.GetPoint(contour.GetN() - 1, x, y)
    xEnd = float(x)
    yEnd = float(y)

    xmin = base.GetXaxis().GetXmin()
    ymin = base.GetYaxis().GetXmin()
    xmax = base.GetXaxis().GetXmax()
    ymax = base.GetYaxis().GetXmax()
    xw = base.GetXaxis().GetBinWidth(1)
    yw = base.GetYaxis().GetBinWidth(1)

    if abs(xBegin - xEnd) < xw and abs(yBegin - yEnd) < yw:
        return

    if xBegin - xmin < xw or yBegin - ymin < yw:
        contour.GetPoint(1, x, y)
        xNext = float(x)
        yNext = float(y)
        xExtr = max(xBegin + (xBegin - xNext) / (yBegin - yNext) * (ymin - yBegin), xmin)
        yExtr = max(yBegin + (yBegin - yNext) / (xBegin - xNext) * (xmin - xBegin), ymin)
        contour.Set(contour.GetN() + 1)
        for iP in range(contour.GetN() - 1, 0, -1):
            contour.GetPoint(iP - 1, x, y)
            contour.SetPoint(iP, x, y)
        x = ROOT.Double(xExtr)
        y = ROOT.Double(yExtr)
        contour.SetPoint(0, x, y)

    if xEnd - xmin < xw or yEnd - ymin < yw:
        contour.GetPoint(contour.GetN() - 2, x, y)
        xNext = float(x)
        yNext = float(y)
        x = ROOT.Double(max(xEnd + (xEnd - xNext) / (yEnd - yNext) * (ymin - yEnd), xmin))
        y = ROOT.Double(max(yEnd + (yEnd - yNext) / (xEnd - xNext) * (xmin - xEnd), ymin))
        contour.Set(contour.GetN() + 1)
        contour.SetPoint(contour.GetN() - 1, x, y)

    if xmax - xBegin < xw or ymax - yBegin < yw:
        contour.GetPoint(1, x, y)
        xNext = float(x)
        yNext = float(y)
        xExtr = min(xBegin + (xBegin - xNext) / (yBegin - yNext) * (ymax - yBegin), xmax)
        yExtr = min(yBegin + (yBegin - yNext) / (xBegin - xNext) * (xmax - xBegin), ymax)
        contour.Set(contour.GetN() + 1)
        for iP in range(contour.GetN() - 1, 0, -1):
            contour.GetPoint(iP - 1, x, y)
            contour.SetPoint(iP, x, y)
        x = ROOT.Double(xExtr)
        y = ROOT.Double(yExtr)
        contour.SetPoint(0, x, y)

    if xmax - xEnd < xw or ymax - yEnd < yw:
        contour.GetPoint(contour.GetN() - 2, x, y)
        xNext = float(x)
        yNext = float(y)
        x = ROOT.Double(max(xEnd + (xEnd - xNext) / (yEnd - yNext) * (ymax - yEnd), xmax))
        y = ROOT.Double(max(yEnd + (yEnd - yNext) / (xEnd - xNext) * (xmax - xEnd), ymax))
        contour.Set(contour.GetN() + 1)
        contour.SetPoint(contour.GetN() - 1, x, y)


model = sys.argv[1]

sourcedir = '/scratch5/yiiyama/studies/monophoton/limits/' + model

limits = {}

for fname in os.listdir(sourcedir):
    matches = re.match('dm[av]fs-([0-9]+)-([0-9]+)', fname)
    if not matches:
        continue

    mmed = float(matches.group(1))
    mdm = float(matches.group(2))

#    if mdm > mmed * 0.5 + 200.:
#        continue

    point = (mmed, mdm)

    source = ROOT.TFile.Open(sourcedir + '/' + fname)
    tree = source.Get('limit')
    if tree.GetEntries() != 6:
        source.Close()
        continue

    tree.SetEstimate(7)
    tree.Draw('limit', '', 'goff')
    limit = tree.GetV1()

    limits[point] = tuple([limit[i] for i in range(6)])

    source.Close()

canvas = ROOT.TCanvas('c1', 'c1', 800, 800)
#canvas.SetLogx()
#canvas.SetLogy()
canvas.SetLogz()

#mmeds = array.array('d', [10. * math.pow(1.1, i) for i in range(51)])
#mdms = array.array('d', [10. * math.pow(1.1, i) for i in range(51)])
mmeds = array.array('d', [100. + 20. * i for i in range(51)])
mdms = array.array('d', [10. * i for i in range(51)])
htemplate = ROOT.TH2D('template', ';M_{med} (GeV);M_{DM} (GeV)', len(mmeds) - 1, mmeds, len(mdms) - 1, mdms)

output = ROOT.TFile.Open('/scratch5/yiiyama/studies/monophoton/limits/' + model + '.root', 'recreate')

#ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetNumberContours(99)
ROOT.TColor.InitializeColors()
stops = array.array('d', [0., 2./3., 1.])
red = array.array('d', [0xff, 0xff, 0x11])
green = array.array('d', [0x33, 0xff, 0x33])
blue = array.array('d', [0x11, 0xff, 0xff])

for a in [red, green, blue]:
    for iP in range(3):
        a[iP] /= 0xff

pstart = ROOT.TColor.CreateGradientColorTable(3, stops, red, green, blue, 255)
colors = array.array('i', [pstart + i for i in range(255)])

ROOT.gStyle.SetPalette(255, colors)

histograms = {}
contours = collections.defaultdict(list)

for iL, name in enumerate(['exp2down', 'exp1down', 'exp', 'exp1up', 'exp2up', 'obs']):
    gr = ROOT.TGraph2D(len(limits))
    gr.SetName(name)

    for iP, (point, larr) in enumerate(limits.items()):
        gr.SetPoint(iP, point[0], point[1], larr[iL])

    output.cd()
    gr.Write(name)

    hist = htemplate.Clone(name + '_int')
    for iX in range(1, hist.GetNbinsX() + 1):
        for iY in range(1, hist.GetNbinsY() + 1):
            z = gr.Interpolate(hist.GetXaxis().GetBinCenter(iX), hist.GetYaxis().GetBinCenter(iY))
            hist.SetBinContent(iX, iY, z)
            
    # ad hoc fix
#    if model == 'dmvfs':
#        lowz = hist.GetBinContent(1, 5)
#        highz = hist.GetBinContent(1, 8)
#        hist.SetBinContent(1, 6, (2. * lowz + 1. * highz) / 3.)
#        hist.SetBinContent(1, 7, (1. * lowz + 2. * highz) / 3.)

    output.cd()
    hist.Write()

    hist.SetMinimum(0.01)
    hist.SetMaximum(10.)
    hist.Draw('colz')

    canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_' + name + '.pdf')
    canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_' + name + '.png')

    histograms[name] = hist

    if name == 'exp':
        pgr = ROOT.TGraph(len(limits))
        for iP, point in enumerate(limits.keys()):
            pgr.SetPoint(iP, point[0], point[1])

        pgr.SetMarkerStyle(4)
        pgr.SetMarkerColor(ROOT.kBlack)

        pgr.Draw('P')

        canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_' + name + '_points.pdf')
        canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_' + name + '_points.png')

    clevel = array.array('d', [1.])
    contsource = hist.Clone('contsource_' + name)
    contsource.SetContour(1, clevel)
    contsource.Draw('CONT LIST')
    canvas.Update()
    contList = ROOT.gROOT.GetListOfSpecials().FindObject('contours').At(0)
    for iC, contour in enumerate(contList):
        if contour.GetY()[0] > contour.GetX()[0] * 0.5 + 100.:
            continue

        cont = contour.Clone()
        output.cd()
        cont.SetName(name + '_cont%d' % iC)
        cont.Write(name + '_cont%d' % iC)
        contours[name].append(cont)
    
    contsource.Delete()

    if name == 'obs':
        for shift, cl in [('obs1up', 0.8), ('obs1down', 1.2)]:
            clevel = array.array('d', [cl])
            contsource = hist.Clone('contsource_' + shift)
            contsource.SetContour(1, clevel)
            contsource.Draw('CONT LIST')
            canvas.Update()
            contList = ROOT.gROOT.GetListOfSpecials().FindObject('contours').At(0)
            for iT, contour in enumerate(contList):
                if contour.GetY()[0] > contour.GetX()[0] * 0.5 + 100.:
                    continue

                cont = contour.Clone()
                output.cd()
                cont.SetName(shift + '_cont%d' % iC)
                cont.Write(shift + '_cont%d' % iC)
                contours[shift].append(cont)
            
            contsource.Delete()
        

histograms['obs'].Draw('COLZ')
for cont in contours['exp']:
    cont.SetLineColor(ROOT.kBlue)
    cont.SetLineWidth(2)
    cont.Draw('CL')
for cont in contours['exp1up']:
    cont.SetLineColor(ROOT.kBlue)
    cont.SetLineWidth(1)
    cont.SetLineStyle(ROOT.kDashed)
    cont.Draw('CL')
for cont in contours['exp1down']:
    cont.SetLineColor(ROOT.kBlue)
    cont.SetLineWidth(1)
    cont.SetLineStyle(ROOT.kDashed)
    cont.Draw('CL')
for cont in contours['obs']:
    cont.SetLineColor(ROOT.kBlack)
    cont.SetLineWidth(2)
    cont.Draw('CL')
for cont in contours['obs1up']:
    cont.SetLineColor(ROOT.kBlack)
    cont.SetLineWidth(1)
    cont.Draw('CL')
for cont in contours['obs1down']:
    cont.SetLineColor(ROOT.kBlack)
    cont.SetLineWidth(1)
    cont.Draw('CL')

legend = ROOT.TLegend(0.15, 0.7, 0.4, 0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.AddEntry(contours['exp'][0], 'Expected #pm 1 #sigma_{exp}', 'L')
legend.AddEntry(contours['obs'][0], 'Observed #pm 1 #sigma_{theory}', 'L')
legend.Draw()

canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_exclusion.pdf')
canvas.Print('/home/yiiyama/public_html/cmsplots/limits/' + model + '_exclusion.png')

output.Close()

