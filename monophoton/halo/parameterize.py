import os
import sys
sys.dont_write_bytecode = True
import math
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
import config

selection = '{sel} && photons.pt > 175. && t1Met.met > 140.'

def makeFoldedPlot(tree, name, sel):
    plot = ROOT.TH1D(name, ";#phi''", 15, -math.pi * 0.5, math.pi * 0.5)
    plot.Sumw2()
    plot.SetLineColor(ROOT.kBlack)
    plot.SetLineWidth(2)
    tree.Draw('TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796>>' + name, selection.format(sel = sel), 'goff')

    return plot

canvas = ROOT.TCanvas('c1', 'c1', 800, 800)

sph = allsamples['sph-16b2']

targTree = ROOT.TChain('events')
targTree.Add(config.photonSkimDir + '/sph-16b2.root')
targTree.Add(config.photonSkimDir + '/sph-16c2.root')
targTree.Add(config.photonSkimDir + '/sph-16d2.root')

work = ROOT.RooWorkspace('work', 'work')
phi = work.factory('phi[%f,%f]' % (-math.pi * 0.5, math.pi * 0.5))
philist = ROOT.RooArgList(phi)
phiset = ROOT.RooArgSet(phi)

targData = ROOT.RooDataSet('targ', 'targ', phiset)
targTree.SetEstimate(targTree.GetEntries() + 1)
nTarg = targTree.Draw('TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796', 'photons.mipEnergy > 4.9 && photons.isEB && photons.pt > 175. && t1Met.met > 140.', 'goff')

print nTarg, 'target events'
targPhi = targTree.GetV1()
for iTarg in range(nTarg):
    phi.setVal(targPhi[iTarg])
    targData.add(phiset)

#base = work.factory('Polynomial::base(phi, {slope[0.,-10.,10.], curv[-1., -10., 0.]})')
base = work.factory('Uniform::base({phi})')
#peak = work.factory('BifurGauss::peak(phi, mean[0.,-3.,3.], sigmal[1.,0.,10.], sigmar[1.,0.,10.])')
#peakbase = work.factory('BreitWigner::peakbase(phi, mean[0.,-3.,3.], width[1., 0., 10.])')
#peak = work.factory('FCONV::peak(phi, peakbase, CBShape::smear(phi, phi0[0.,-10.,10.],sigma[1.,0.,10.],alpha[1.,0.,5.],n[2.,1.,10.]))')
peak = work.factory('SUM::peak(p1[0.1,0.,1.]*Gaussian::peak1(phi, mean1[0.,-3.,3.], sigma1[0.1,0.,1.]),Gaussian::peak2(phi, mean2[0.,-3.,3.], sigma2[0.001,0.,0.1]))')
model = work.factory('SUM::model(fbase[0.1,0.,1.]*base, peak)')

model.fitTo(targData)

frame = phi.frame()
targData.plotOn(frame)
model.plotOn(frame)

canvas = ROOT.TCanvas('c1', 'c1', 800, 800)
frame.Draw()
canvas.Print('/home/yiiyama/public_html/cmsplots/monophoton/halo/phiHaloFoldedFit.pdf')
canvas.Print('/home/yiiyama/public_html/cmsplots/monophoton/halo/phiHaloFoldedFit.png')

