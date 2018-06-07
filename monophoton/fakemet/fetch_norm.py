import sys
import ROOT

fitDiagnostics = sys.argv[1]

source = ROOT.TFile.Open(fitDiagnostics)

norms = source.Get('norm_fit_s')

sig = norms.find('gghg/dph-nlo-125')
fake = norms.find('gghg/fakemet')

print sig.getVal(), fake.getVal()
