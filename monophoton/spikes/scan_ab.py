"""
Scan along the alpha-beta correlation line and plot sieie:t0 for each point.
"""

import ROOT

ROOT.gStyle.SetOptStat(0)

points = [
    (0.4, 2.8),
    (0.4, 2.4),
    (0.5, 2.8),
    (0.6, 2.),
    (0.7, 2.),
    (0.8, 1.9),
    (0.85, 1.8),
    (0.8, 2.),
    (0.95, 1.8),
    (1., 1.75),
    (1.05, 1.7),
    (1.1, 1.7),
    (1.2, 1.6),
    (1.3, 1.6),
    (1.5, 1.6),
    (1.7, 1.5),
    (2., 1.4)
]

canvas = ROOT.TCanvas('c1', 'c1', 600, 600)

source = ROOT.TFile.Open('/data/t3home000/yiiyama/spike_notopo/SinglePhoton.root')
tree = source.Get('hits')

for alpha, beta in points:
    canvas.cd()
    tree.Draw('sieie:t0>>abcd(100,4.,6.,100,0.,0.025)', 'alpha > %f && alpha < %f && beta > %f && beta < %f' % (alpha - 0.05, alpha + 0.05, beta - 0.05, beta + 0.05), 'colz')
    canvas.Print('/home/yiiyama/public_html/cmsplots/scan_ab/%.2f_%.2f.pdf' % (alpha, beta))
    canvas.Print('/home/yiiyama/public_html/cmsplots/scan_ab/%.2f_%.2f.png' % (alpha, beta))

    canvas.Clear()
