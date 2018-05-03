import os
import sys
import array
import math
import ROOT

### EWK corrections and uncertainties (1412.7421 and 1510.08742)
###
### Wgamma (1412.7421) factorization is sigma^{NLO} = sigma^{NLO QCD} (1 + delta_{EW,qq~} + delta_{EW,qgamma})
### where delta_{EW,X} = Delta sigma^{NLO EW}_{X} / sigma_{0} (sigma_{0} = LO sigma with NLO PDF) and
### Delta sigma^{NLO EW}_{qq~} = sigma_{real} + sigma_{virtual} + sigma_{col}
### Delta sigma^{NLO EW}_{qgamma} = sigma_{real} + sigma_{col} + sigma_{frag}
### (col: sigma diff from PDF redefinition)
### However in the paper they mention that EW,qgamma contribution is better not factored:
### sigma^{NLO} = sigma^{NLO QCD} (1 + delta_{EW,qq~}) + sigma^{NLO EW}_{qgamma}
### which is how Zgamma (1510.08742) is factorized.
###
### We are provided with delta_{EW,X} numbers and want to derive a weight that is to be multiplied on top
### of the NNLO QCD correction. The formula is therefore
###   w = delta_{EW,qq~} + delta_{EW,qgamma} * sigma_{LO} / sigma_{NNLO}
### sigma_{LO} here is 0 jet LO instead of the MLM merged LO.

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

MAKESOURCE = False

center = 500

#outFile = ROOT.TFile.Open(basedir + '/data/ewk_corr.root', 'recreate' if MAKESOURCE else 'update')
outFile = ROOT.TFile.Open(basedir + '/data/ewk_corr_%d.root' % center, 'recreate')
origFile = ROOT.TFile.Open(basedir + '/data/ewk_corr.root')

outFile.mkdir('source')
origFile.cd('source')
for key in ROOT.gDirectory.GetListOfKeys():
    outFile.cd('source')
    key.ReadObj().Write()

nnloBinning = [175., 190., 250., 400., 700., 1000.]

if MAKESOURCE:
    outFile.mkdir('source')

    ## First we make plots out of provided text files
    sources = {
        'wmqq': 'DELTA_histo_wminusgamma_qqEW_v+r_13TeV_part_nnpdf31lux001_PaperSetup_pt5_new.txt',
        'wmqg': 'DELTA_histo_wminusgamma_qph_v+r_13TeV_part_nnpdf31lux001_PaperSetup_pt5_new.txt',
        'wpqq': 'DELTA_histo_wplusgamma_qqEW_v+r_13TeV_part_nnpdf31lux001_PaperSetup_pt5_new.txt',
        'wpqg': 'DELTA_histo_wplusgamma_qph_v+r_13TeV_nnpdf31lux_part001_PaperSetup_pt5_new.txt',
        'zqq': 'DELTA_histo_zgamma_nn_qqEW_v+r_13TeV_part_nnpdf31lux001_PaperSetup_pt5_new.txt',
        'zqg': 'DELTA_histo_zgamma_nn_qph_v+r_13TeV_part_nnpdf31lux001_PaperSetup_pt5_new.txt'
    }

    for name, filename in sources.items():
        bin_centers = []
        values = []
        errors = []
        with open(basedir + '/data/raw/ewknlo/' + filename) as source:
            for line in source:
                if not line.strip():
                    continue
    
                x, y, dy = map(float, line.split())
                if x < 165.:
                    continue
                if x > 1000.:
                    break
    
                bin_centers.append(x)
                values.append(y)
                errors.append(dy)
    
        outFile.cd('source')
    
        binning = [160.]
        for ix in range(len(bin_centers)):
            binning.append(2. * bin_centers[ix] - binning[ix])
    
        hist = ROOT.TH1D(name, ';p_{T}^{#gamma} (GeV)', len(binning) - 1, array.array('d', binning))
        for ix in range(len(bin_centers)):
            hist.SetBinContent(ix + 1, values[ix])
            hist.SetBinError(ix + 1, errors[ix])
    
        hist.Write()

    losources = {
        #/mnt/hadoop/scratch/yiiyama/monophoton/ewk_corr/VGNoJets_Z.root
        'z': ('/local/yiiyama/VGNoJets_Z.root', 'pid == 22', 0.0095645),
        'wm': ('/local/yiiyama/VGNoJets_W.root', 'pid == 22 && Sum$(pid == 11) != 0', 0.0052236),
        'wp': ('/local/yiiyama/VGNoJets_W.root', 'pid == 22 && Sum$(pid == -11) != 0', 0.0061164)
    }

    for name, (fname, expr, xsec) in losources.items():
        source = ROOT.TFile.Open(fname)
        events = source.Get('events')
    
        outFile.cd('source')
        hist = ROOT.TH1D('%slo' % name, ';p_{T}^{#gamma} (GeV)', len(nnloBinning) - 1, array.array('d', nnloBinning))
        
        events.Draw('TMath::Sqrt(px * px + py * py)>>%slo' % name, expr, 'goff')
        hist.Scale(xsec * 3. / hist.GetEntries(), 'width') # 3 neutrino flavors
        hist.GetYaxis().SetTitle('d#sigma/dp_{T}')
        hist.Write()


## Make wminus, wplus, znn
nnlosources = {
    'wm': 'wmnlg_grazzini.dat',
    'wp': 'wpnlg_grazzini.dat',
    'z': 'znng_grazzini.dat'
}
weights = {
    'wm': 'wnlg-130-o_m',
    'wp': 'wnlg-130-o_p',
    'z': 'znng-130-o'
}

for fs in ['wm', 'wp', 'z']:
    hqq = outFile.Get('source/' + fs + 'qq')
    hqg = outFile.Get('source/' + fs + 'qg')
    hlo = outFile.Get('source/' + fs + 'lo')

    outFile.cd()
    weight = hqq.Clone(weights[fs])

    weight.Reset()

    straightup = weight.Clone(weights[fs] + '_straightUp')
    straightdown = weight.Clone(weights[fs] + '_straightDown')
    twistedup = weight.Clone(weights[fs] + '_twistedUp')
    twisteddown = weight.Clone(weights[fs] + '_twistedDown')
    gammaup = weight.Clone(weights[fs] + '_gammaUp')
    gammadown = weight.Clone(weights[fs] + '_gammaDown')

    nnlos = []
    with open(basedir + '/data/raw/' + nnlosources[fs]) as nnlosource:
        for line in nnlosource:
            if line.startswith('#'):
                continue

            words = line.split()
            nnlos.append(float(words[1]) * 1.e-3 * 3.)

    ptrange = (175., 1000.)
#    center = (ptrange[0] + ptrange[1]) * 0.5
    halfwidth = (ptrange[1] - ptrange[0]) * 0.5

    for ix in range(1, hqq.GetNbinsX() + 1):
        x = weight.GetXaxis().GetBinUpEdge(ix) - 1.
        ilo = hlo.FindFixBin(x)

        dqq = hqq.GetBinContent(hqq.FindFixBin(x))
        lo = hlo.GetBinContent(ilo)
        qg = hqg.GetBinContent(hqg.FindFixBin(x))
        dqg = qg * lo / nnlos[ilo - 1]

        central = 1. + dqq + dqg

        weight.SetBinContent(ix, central)

        ddqq = dqq * dqq / math.sqrt(2.)

        straightup.SetBinContent(ix, central + ddqq)
        straightdown.SetBinContent(ix, central - ddqq)

        twist = ddqq * (x - center) / halfwidth
        twistedup.SetBinContent(ix, central + twist)
        twisteddown.SetBinContent(ix, central - twist)

        gammaup.SetBinContent(ix, central + dqg)
        gammadown.SetBinContent(ix, central - dqg)

    outFile.cd()
    weight.Write()
    straightup.Write()
    straightdown.Write()
    twistedup.Write()
    twisteddown.Write()
    gammaup.Write()
    gammadown.Write()
