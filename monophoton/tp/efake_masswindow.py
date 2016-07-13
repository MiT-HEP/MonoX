import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from tp.efake_conf import skimDir, skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

source = ROOT.TFile.Open(sys.argv[1])
work = source.Get('work')
tree = source.Get('yields')

a_alpha = array.array('d', [0.])
a_m0 = array.array('d', [0.])
a_n = array.array('d', [0.])
a_sigma = array.array('d', [0.])

tree.SetBranchAddress('alpha', a_alpha)
tree.SetBranchAddress('m0', a_m0)
tree.SetBranchAddress('n', a_n)
tree.SetBranchAddress('sigma', a_sigma)

pdf = work.pdf('sigModel_pt_100_6500')
alpha = work.arg('alpha')
m0 = work.arg('m0')
n = work.arg('n')
sigma = work.arg('sigma')
mass = work.arg('mass')

mass.setBinning(ROOT.RooUniformBinning(60., 120., 60), 'fitWindow')
norm = pdf.createIntegral(ROOT.RooArgSet(mass), 'fitWindow')

windows = [(62., 120.), (67., 115.), (72., 110.), (77., 105.), (81., 101.), (83., 99.)]
yields = {}

for iconf, conf in [(0, 'ee'), (1, 'eg')]:
    tree.GetEntry(iconf)
    
    alpha.setVal(a_alpha[0])
    m0.setVal(a_m0[0])
    n.setVal(a_n[0])
    sigma.setVal(a_sigma[0])

    yields[conf] = []

    for wmin, wmax in windows:
        mass.setBinning(ROOT.RooUniformBinning(wmin, wmax, 100), 'compWindow')
        integral = pdf.createIntegral(ROOT.RooArgSet(mass), 'compWindow')
        yields[conf].append(integral.getVal() / norm.getVal())

print yields

for iW in range(len(windows)):
    print yields['eg'][iW] / yields['ee'][iW]
