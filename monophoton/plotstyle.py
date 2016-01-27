import os
import sys
import ROOT

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTextFont(42)
ROOT.gStyle.SetLabelSize(0.05, 'X')
ROOT.gStyle.SetLabelSize(0.05, 'Y')
ROOT.gStyle.SetTitleSize(0.05, 'X')
ROOT.gStyle.SetTitleSize(0.05, 'Y')
ROOT.gStyle.SetTitleOffset(0.84, 'X')
ROOT.gStyle.SetTitleOffset(1.3, 'Y')
ROOT.gStyle.SetNdivisions(205, 'X')

def makeText(x1, y1, x2, y2, textalign = 22, font = 42):
    pave = ROOT.TPaveText()
    pave.SetX1NDC(x1)
    pave.SetX2NDC(x2)
    pave.SetY1NDC(y1)
    pave.SetY2NDC(y2)
    pave.SetTextAlign(textalign)
    pave.SetFillStyle(0)
    pave.SetBorderSize(0)
    pave.SetMargin(0.)
    pave.SetTextFont(font)

    return pave


def makeAxis(axis, a1, a2, b, vmin = 0., vmax = 1., ndiv = 205, font = 42, log = False):
    if axis == 'X':
        args = (a1, b, a2, b, vmin, vmax, ndiv)
    elif axis == 'Y':
        args = (b, a1, b, a2, vmin, vmax, ndiv)
    else:
        raise RuntimeError('Invalid axis ' + axis)

    if log:
        args = tuple(list(args) + ['G'])

    gaxis = ROOT.TGaxis(*args)

    gaxis.SetLabelFont(font)
    gaxis.SetTitleFont(font)
    gaxis.SetTitleOffset(ROOT.gStyle.GetTitleOffset(axis))
    gaxis.SetTitleSize(0.048)
    gaxis.SetLabelSize(0.042)
    gaxis.SetTickLength(0.)

    return gaxis


class PlotStyle(object):
    def __init__(self, color = -1, lwidth = -1, lstyle = -1, lcolor = -1, fstyle = -1, fcolor = -1, msize = -1, mstyle = -1, mcolor = -1):
        if color >= 0:
            self.lcolor = color
            self.fcolor = color
            self.mcolor = color
        else:
            self.lcolor = lcolor
            self.fcolor = fcolor
            self.mcolor = mcolor

        self.lwidth = lwidth
        self.lstyle = lstyle
        self.fstyle = fstyle
        self.msize = msize
        self.mstyle = mstyle


class Legend(object):

    Attributes = [
        'LineWidth',
        'LineStyle',
        'LineColor',
        'FillStyle',
        'FillColor',
        'MarkerSize',
        'MarkerStyle',
        'MarkerColor'
    ]

    def __init__(self, x1, y1, x2, y2):
        self.legend = ROOT.TLegend(x1, y1, x2, y2)
        self.legend.SetFillStyle(0)
        self.legend.SetBorderSize(0)
        self.legend.SetTextSize(0.04)
        self.legend.SetTextFont(42)
        self.legend.SetTextAlign(12)

        self.entries = {}
        self.defaultOrder = []

    def setPosition(self, x1, y1, x2, y2):
        self.legend.SetX1(x1)
        self.legend.SetY1(y1)
        self.legend.SetX2(x2)
        self.legend.SetY2(y2)

    def add(self, obl, title = '', opt = 'LFP', color = -1, lwidth = -1, lstyle = -1, lcolor = -1, fstyle = -1, fcolor = -1, msize = -1, mstyle = -1, mcolor = -1):
        ent = ROOT.TLegendEntry(0)

        if type(obl) is str:
            name = obl

        else:
            obj = obl
            name = obj.GetName()
            if not title:
                title = obj.GetTitle()

            for at in Legend.Attributes:
                try:
                    getattr(ent, 'Set' + at)(getattr(obj, 'Get' + at)())
                    attr.append(at)
                except AttributeError:
                    pass

        ent.SetLabel(title)
        ent.SetOption(opt)

        args = [lwidth, lstyle, lcolor, fstyle, fcolor, msize, mstyle, mcolor]
        for iA in range(len(args)):
            getattr(ent, 'Set' + Legend.Attributes[iA])(args[iA])

        if color != -1:
            for at in Legend.Attributes:
                if 'Color' in at:
                    getattr(ent, 'Set' + at)(color)
            
        self.entries[name] = ent
        self.defaultOrder.append(name)

    def apply(self, name, obj):
        entry = self.entries[name]

        for at in Legend.Attributes:
            value = getattr(entry, 'Get' + at)()
            if value != -1:
                getattr(obj, 'Set' + at)(value)

    def construct(self, order = []):
        if self.legend.GetListOfPrimitives().GetEntries() != 0:
            return

        if len(order) == 0:
            order = self.defaultOrder

        for name in order:
            ent = self.entries[name]
            self.legend.AddEntry(ent, ent.GetLabel(), ent.GetOption())

    def Clear(self):
        self.legend.Clear()
        self.entries = {}
        self.defaultOrder = []

    def Draw(self, order = []):
        if self.legend.GetListOfPrimitives().GetEntries() == 0:
            self.construct(order)

        self.legend.Draw()

    def __getattr__(self, name):
        return getattr(self.legend, name)


class Histogram(object):
    def __init__(self, histogram, drawOpt, useRooPlot = False):
        self.histogram = histogram
        self.drawOpt = drawOpt
        self.useRooPlot = useRooPlot

    def __getattr__(self, attr):
        return getattr(self.histogram, attr)

    def Clone(self, name = ''):
        clone = self.histogram.Clone(name)
        return Histogram(clone, self.drawOpt, self.useRooPlot)


class SimpleCanvas(object):
    def __init__(self, name = 'cSimple', title = 'simple', lumi = -1., sim = False, cms = True):
        self.canvas = ROOT.TCanvas(name, title, 600, 600)
        self.canvas.SetTopMargin(0.08)
        self.canvas.SetRightMargin(0.05)
        self.canvas.SetBottomMargin(0.12)
        self.canvas.SetLeftMargin(0.15)

        self._histograms = []
        self._objects = []

        self.legend = Legend(0.7, 0.6, 0.95, 0.95)

        self._logy = True

        self.ylimits = (0., -1.)

        self.minimum = -1.

        self.title = ''
        self.textside = 'left'

        self.titlePave = makeText(0.15, 0.92, 0.95, 1.)

        if cms:
            self.cmsPave = makeText(0.18, 0.8, 0.3, 0.91, textalign = 11, font = 62)
            if sim:
                self.cmsPave.AddText('#splitline{CMS}{#font[52]{Simulation}}')
            else:
                self.cmsPave.AddText('#splitline{CMS}{#font[52]{Preliminary}}')
    
            if lumi > 0.:
                self.lumiPave = makeText(0.6, 0.96, 0.92, 1., textalign = 33)
                if lumi > 1000.:
                    self.lumiPave.AddText('%.1f fb^{-1} (13 TeV)' % (lumi / 1000.))
                else:
                    self.lumiPave.AddText('%.1f pb^{-1} (13 TeV)' % lumi)
            else:
                self.lumiPave = None
        else:
            self.cmsPave = None

        gDirectory = ROOT.gDirectory
        ROOT.gROOT.cd()
        self._hStore = ROOT.gROOT.mkdir(name + '_hstore')
        gDirectory.cd()

        self._needUpdate = True
        self._temporaries = []

    def __getattr__(self, name):
        return getattr(self.canvas, name)

    def _modified(self):
        self._needUpdate = True
        
        for obj in self._temporaries:
            try:
                obj.Delete()
            except:
                pass

        self._temporaries = []

    def addHistogram(self, hist, drawOpt = 'HIST', idx = -1, clone = True, asymErr = False):
        gDirectory = ROOT.gDirectory

        if idx < 0:
            idx = len(self._histograms)

        if idx > len(self._histograms):
            raise RuntimeError('Invalid histogram index ' + str(idx))

        elif idx == len(self._histograms):
            # new histogram
            if clone:
                self._hStore.cd()
                self._histograms.append(Histogram(hist.Clone(), drawOpt.upper(), useRooPlot = asymErr))
            else:
                self._histograms.append(Histogram(hist, drawOpt.upper(), useRooPlot = asymErr))

            newHist = self._histograms[-1]
            try:
                if newHist.GetSumw2().fN == 0:
                    newHist.Sumw2()
            except:
                pass

        else:
            self._histograms[idx].Add(hist)

        gDirectory.cd()

        self._modified()

        return idx


    def addObject(self, obj, clone = True):
        if clone:
            self._objects.append(obj.Clone())
        else:
            self._objects.append(obj)

    def addLine(self, x1, y1, x2, y2, color = ROOT.kBlack, width = 1, style = ROOT.kSolid):
        line = ROOT.TLine(x1, y1, x2, y2)
        line.SetLineColor(color)
        line.SetLineWidth(width)
        line.SetLineStyle(style)
        self._objects.append(line)

    def addText(self, text, x1, y1, x2, y2, textalign = 22, font = 42):
        pave = maketext(x1, y1, x2, y2, textalign = textalign, font = font)
        pave.AddText(text)
        self._objects.append(pave)

    def Clear(self, full = False):
        self.canvas.Clear()
        self.minimum = -1.

        if full:
            self.legend.Clear()
            self._logy = True
            self.title = ''
            self.textside = 'left'

        for h in self._histograms:
            h.Delete()

        self._histograms = []

        self._modified()

    def Update(self, hList = [], logy = None):
        if logy is not None:
            self.canvas.SetLogy(logy)
            self.canvas.Update()

        if not self._needUpdate:
            return

        if logy is None:
            logy = self._logy

        gPad = ROOT.gPad
        self.canvas.cd()
        if logy:
            self.canvas.SetLogy(True)

        if len(hList) == 0:
            hList = range(len(self._histograms))

        if len(hList) > 0:
            base = self._histograms[hList[0]]
            if base.histogram.InheritsFrom(ROOT.TGraph.Class()):
                base.Draw('A' + base.drawOpt)
            else:
                base.Draw(base.drawOpt)

            for ih in hList[1:]:
                hist = self._histograms[ih]
                if hist.histogram.InheritsFrom(ROOT.TH1.Class()):
                    hist.Draw(hist.drawOpt + ' SAME')
                else:
                    hist.Draw(hist.drawOpt)
    
                if hist.GetMaximum() > base.GetMaximum():
                    if logy:
                        base.SetMaximum(hist.GetMaximum() * 5.)
                    else:
                        base.SetMaximum(hist.GetMaximum() * 1.3)
        
            self.canvas.Update()

            if self.ylimits[1] < self.ylimits[0]:
                if logy:
                    if self.minimum > 0.:
                        base.SetMinimum(self.minimum)
                else:
                    base.SetMinimum(0.)
            else:
                base.GetYaxis().SetRangeUser(*self.ylimits)

        for obj in self._objects:
            obj.Draw()

        self.drawText()

        if len(self.legend.entries) != 0:
            self.legend.Draw()

        self.canvas.Update()
        gPad.cd()

        self._needUpdate = False

    def SetLogy(self, logy):
        self._logy = logy
        self._modified()

    def drawText(self):
        self.titlePave.Clear()
        self.titlePave.AddText(self.title)
        self.titlePave.Draw()

        if self.cmsPave:
            if self.textside == 'right':
                self.cmsPave.SetX1NDC(0.7)
                self.cmsPave.SetX2NDC(0.92)
                self.cmsPave.SetTextAlign(31)
            else:
                self.cmsPave.SetX1NDC(0.18)
                self.cmsPave.SetX2NDC(0.4)
                self.cmsPave.SetTextAlign(11)
    
            self.cmsPave.Draw()
            if self.lumiPave:
                self.lumiPave.Draw()

    def printWeb(self, directory, name, logy = None, **options):
        self.Update(logy = logy, **options)

        home = os.environ['HOME']
        webdir = home + '/public_html/cmsplots/' + directory
        if not os.path.isdir(webdir):
            os.makedirs(webdir)

        self.canvas.Draw()
        self.canvas.Print(webdir + '/' + name + '.png', 'png')
        self.canvas.Print(webdir + '/' + name + '.pdf', 'pdf')


class RatioCanvas(SimpleCanvas):

    def __init__(self, name = 'cRatio', title = 'Ratio', lumi = -1., sim = False, cms = True):
        SimpleCanvas.__init__(self, name = name, title = title, lumi = lumi, sim = sim, cms = cms)

        self.canvas.SetCanvasSize(600, 680)

        self.xaxis = makeAxis('X', 0.15, 0.95, 0.1)
        self.xtitle = ''

        self.yaxis = makeAxis('Y', 0.31, 0.92, 0.15, vmin = 0.1, vmax = 1., log = True)
        self.ytitle = ''

        self.raxis = makeAxis('Y', 0.1, 0.29, 0.15, vmax = 2.)
        self.rtitle = 'data / MC'

        self.rlimits = (0., 2.)

        self._makePads()

        self._modified()

    def _makePads(self):
        self.canvas.Divide(2)
        
        self.plotPad = self.canvas.cd(1)
        self.plotPad.SetPad(0., 0., 1., 1.)
        self.plotPad.SetMargin(0.15, 0.05, 0.31, 0.08) # lrbt
        self.plotPad.SetLogy(self._logy)
        
        self.ratioPad = self.canvas.cd(2)
        self.ratioPad.SetPad(0.15, 0.1, 0.95, 0.29)
        self.ratioPad.SetMargin(0., 0., 0., 0.)
        self.ratioPad.SetTickx(1)

    def cd(self):
        self.plotPad.cd()

    def Clear(self, full = False):
        SimpleCanvas.Clear(self, full = full)
        self._makePads()
        if full:
            self.legend.Clear()

        self.xaxis.SetWmin(0.)
        self.xaxis.SetWmax(1.)
        self.yaxis.SetWmin(0.1)
        self.yaxis.SetWmax(1.)
        self.raxis.SetWmin(self.rlimits[0])
        self.raxis.SetWmax(self.rlimits[1])

    def Update(self, hList = [], rList = [], logy = None):
        if logy is not None:
            self.plotPad.SetLogy(logy)
            self.canvas.Update()

        if not self._needUpdate:
            return

        if logy is None:
            logy = self._logy

        gPad = ROOT.gPad
        gDirectory = ROOT.gDirectory

        self.canvas.cd()
        self.canvas.Update()

        self.plotPad.cd()
        self.plotPad.SetLogy(logy)

        # list of histograms to draw
        if len(hList) == 0:
            hList = range(len(self._histograms))

        if len(hList) > 0:
            # draw base
            base = self._histograms[hList[0]]
            base.Draw(base.drawOpt)

            self.plotPad.Update()
    
            # draw other histograms
            for ih in hList[1:]:
                hist = self._histograms[ih]
    
                if hist.GetMaximum() > base.GetMaximum():
                    if logy:
                        base.SetMaximum(hist.GetMaximum() * 5.)
                    else:
                        base.SetMaximum(hist.GetMaximum() * 1.3)
    
                hist.Draw(hist.drawOpt + ' SAME')

            self.plotPad.Update()
    
            if logy:
                if self.minimum > 0.:
                    base.SetMinimum(self.minimum)
            else:
                base.SetMinimum(0.)

            base.GetYaxis().SetTitle('')
            base.GetYaxis().SetLabelSize(0.)
            base.GetXaxis().SetTitle('')
            base.GetXaxis().SetLabelSize(0.)

            # will be overridden by self.ytitle
            self.yaxis.SetTitle(base.GetYaxis().GetTitle())

            if len(self.legend.entries) != 0:
                self.legend.Draw()

        # now ratio plots
        self.ratioPad.cd()

        # list of ratio histograms
        if len(rList) == 0:
            rList = list(hList)

        ratios = []

        if len(rList) > 0:
            # set up ratio base
            self._hStore.cd()
            rbase = self._histograms[rList[0]].Clone('rbase')
            ratios.append(rbase)
            self._temporaries.append(rbase)
    
            # first use rbase to normalize others
            for ir in rList[1:]:
                hist = self._histograms[ir]
    
                self._hStore.cd()
                ratio = hist.Clone('ratio_' + hist.GetName())
                ratio.SetTitle('')
                ratios.append(ratio)
                self._temporaries.append(ratio)
    
                if hist.InheritsFrom(ROOT.TH1.Class()):
                    for iX in range(1, rbase.GetNbinsX() + 1):
                        norm = rbase.GetBinContent(iX)
                        if norm > 0.:
                            ratio.SetBinError(iX, hist.GetBinError(iX) / norm)
                            ratio.SetBinContent(iX, hist.GetBinContent(iX) / norm)
                        else:
                            ratio.SetBinError(iX, 0.)
                            ratio.SetBinContent(iX, 0.)
    
                elif hist.InheritsFrom(ROOT.TGraph.Class()):
                    for iP in range(rbase.GetNbinsX()):
                        iX = iP + 1
                        norm = rbase.GetBinContent(iX)
                        x = hist.GetX()[iP]
                        if norm > 0.:
                            ratio.SetPoint(iP, x, hist.GetY()[iP] / norm)
                            errhigh = hist.GetErrorYhigh(iP) / norm
                            errlow = hist.GetErrorYlow(iP) / norm
                            try:
                                ratio.SetPointError(iP, 0., 0., errlow, errhigh)
                            except:
                                try:
                                    ratio.SetPointError(iP, 0., errhigh)
                                except:
                                    pass
                        else:
                            ratio.SetPoint(iP, x, 0.)
                            try:
                                ratio.SetPointError(iP, 0., 0., 0., 0.)
                            except:
                                try:
                                    ratio.SetPointError(iP, 0., 0.)
                                except:
                                    pass
    
            # then normalize rbase
            for iX in range(1, rbase.GetNbinsX() + 1):
                norm = rbase.GetBinContent(iX)
                if norm > 0.:
                    rbase.SetBinError(iX, rbase.GetBinError(iX) / norm)
                    rbase.SetBinContent(iX, 1.)
                else:
                    rbase.SetBinError(iX, 0.)
                    rbase.SetBinContent(iX, 0.)
    
            # draw rbase
            rbase.Draw(rbase.drawOpt)
            rbase.SetMinimum(self.rlimits[0])
            rbase.SetMaximum(self.rlimits[1])
    
            # draw the base line
            if not ('HIST' in rbase.drawOpt and rbase.GetLineWidth() > 0):
                rline = ROOT.TLine(0., 1., 1., 1.)
                rline.Draw()
                self._temporaries.append(rline)
    
            # draw other ratios
            for ratio in ratios[1:]:
                ratio.Draw(ratio.drawOpt + ' SAME')

            rbase.SetTitle('')
            rbase.GetXaxis().SetTitle('')
            rbase.GetXaxis().SetLabelSize(0.)
            rbase.GetXaxis().SetNdivisions(205)
            rbase.GetYaxis().SetLabelSize(0.)
            rbase.GetYaxis().SetNdivisions(302)

            # will be overridden by self.xtitle
            self.xaxis.SetTitle(rbase.GetXaxis().GetTitle())

            self.canvas.Update()

            self.ratioPad.Update()

        self.canvas.cd()

        self.xaxis.SetWmin(self.plotPad.PadtoX(self.plotPad.GetUxmin()))
        self.xaxis.SetWmax(self.plotPad.PadtoX(self.plotPad.GetUxmax()))
        self.xaxis.Draw()

        if logy:
            self.yaxis.SetOption('G')
        else:
            self.yaxis.SetOption('')

        self.yaxis.SetWmin(self.plotPad.PadtoY(self.plotPad.GetUymin()))
        self.yaxis.SetWmax(self.plotPad.PadtoY(self.plotPad.GetUymax()))
        self.yaxis.Draw()

        self.raxis.SetWmin(self.ratioPad.PadtoY(self.ratioPad.GetUymin()))
        self.raxis.SetWmax(self.ratioPad.PadtoY(self.ratioPad.GetUymax()))
        self.raxis.Draw()

        if self.ytitle:
            self.yaxis.SetTitle(self.ytitle)

        if self.xtitle:
            self.xaxis.SetTitle(self.xtitle)

        self.raxis.SetTitle(self.rtitle)

        self.drawText()

        gDirectory.cd()
        gPad.cd()

        self.canvas.Update()

        self._needUpdate = False


class DataMCCanvas(RatioCanvas):

    def __init__(self, name = 'cDataMC', title = 'Data / MC', lumi = -1.):
        RatioCanvas.__init__(self, name = name+'_'+str(lumi), title = title, lumi = lumi)

        self._obs = -1
        self._bkgs = []
        self._sigs = []

        self._stack = ROOT.THStack('stack', '')
        self.addHistogram(self._stack, 'HIST', clone = False)

        self.borderColor = ROOT.kBlack

    def Clear(self, full = False):
        RatioCanvas.Clear(self, full = full)

        self._obs = -1
        self._bkgs = []
        self._sigs = []

        self._stack = ROOT.THStack('stack', '')
        self.addHistogram(self._stack, 'HIST', clone = False)

    def addObs(self, obs, title = 'Observed', color = ROOT.kBlack, drawOpt = 'EP', asymErr = False):
        if self._obs == -1:
            self._hStore.cd()
            self._obs = self.addHistogram(obs, drawOpt, asymErr = asymErr)

            self.legend.add('obs', title = title, opt = 'LP', color = color, mstyle = 8, msize = 0.8)
            self.legend.apply('obs', self._histograms[self._obs].histogram)

        else:
            self.addHistogram(obs, idx = self._obs)

        self._modified()

        return self._obs

    def addStacked(self, bkg, title = '', color = 0, style = 1001, idx = -1):
        idx = self.addHistogram(bkg, idx = idx)

        if idx not in self._bkgs:
            # a new background
            self._bkgs.append(idx)

            bkgHist = self._histograms[idx]
            fillcolor = ROOT.gROOT.GetColor(color)
            if fillcolor:
                r = fillcolor.GetRed() * 0.8
                g = fillcolor.GetGreen() * 0.8
                b = fillcolor.GetBlue() * 0.8
                lcolor = ROOT.TColor.GetColor(r, g, b)
            else:
                lcolor = color

            self.legend.add('bkg%d' % idx, title = title, opt = 'LF', fcolor = color, mcolor = lcolor, lcolor = lcolor, fstyle = style, lwidth = 2, lstyle = ROOT.kSolid)
            self.legend.apply('bkg%d' % idx, bkgHist.histogram)

            self._stack.Add(bkgHist.histogram)

        self._modified()

        return idx

    def addSignal(self, sig, title = '', color = 0, idx = -1, drawOpt = 'HIST'):
        idx = self.addHistogram(sig, drawOpt = drawOpt, idx = idx)

        if idx not in self._sigs:
            # a new signal
            self._sigs.append(idx)

            self.legend.add('sig%d' % idx, title = title, opt = 'L', color = color, lwidth = 2, lstyle = ROOT.kSolid, fstyle = 0)
            self.legend.apply('sig%d' % idx, self._histograms[idx].histogram)

        self._modified()

        return idx

    def Update(self, logy = None):
        if logy is not None:
            self.plotPad.SetLogy(logy)
            self.canvas.Update()

        if not self._needUpdate:
            return

        gDirectory = ROOT.gDirectory

        if len(self._bkgs) != 0:
            first = self._histograms[self._bkgs[0]]

            self._hStore.cd()
            borderHist = first.Clone('border')
            uncertHist = first.Clone('uncert')

            for iBkg in self._bkgs[1:]:
                bkg = self._histograms[iBkg]
                borderHist.Add(bkg.histogram)
                uncertHist.Add(bkg.histogram)
        
            borderHist.SetLineWidth(2)
            borderHist.SetLineColor(self.borderColor)
            borderHist.SetMarkerSize(0)
            borderHist.SetMarkerStyle(0)
            borderHist.SetMarkerColor(self.borderColor)
            borderHist.SetFillStyle(0)

            uncertHist.SetFillStyle(3003)
            uncertHist.SetFillColor(ROOT.kGray + 2)
            uncertHist.SetMarkerSize(0)
            uncertHist.SetMarkerStyle(0)
            uncertHist.SetMarkerColor(ROOT.kGray + 2)
            uncertHist.SetLineWidth(0)

            self.addHistogram(borderHist, drawOpt = 'HIST', clone = False)
            iBorder = len(self._histograms) - 1
            self.addHistogram(uncertHist, drawOpt = 'E2', clone = False)
            iUncert = len(self._histograms) - 1

            # addHistogram calls _modified which clears temporaries - this line has to come after above
            self._temporaries += [borderHist, uncertHist]

            hList = [0, iBorder, iUncert] + self._sigs + [self._obs]
            rList = [iBorder] + [self._obs]

            self.legend.construct(['obs'] + ['bkg%d' % idx for idx in reversed(self._bkgs)] + ['sig%d' % idx for idx in self._sigs])

            RatioCanvas.Update(self, hList = hList, rList = rList, logy = logy)

            self._histograms.pop()
            self._histograms.pop()

        gDirectory.cd()

    def obsHistogram(self):
        if self._obs != -1:
            return self._histograms[self._obs]
        else:
            return None
