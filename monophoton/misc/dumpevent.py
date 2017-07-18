import os
import sys

import ROOT
ROOT.gSystem.Load('libPandaTreeObjects.so')
## need to instantiate ROOT.panda (otherwise CLING segfaults)
#e = ROOT.panda.Event

if len(sys.argv) > 2:
    run, lumi, event = map(int, sys.argv[2].split(':'))
else:
    run, lumi, event = 0, 0, 0

ROOT.gROOT.LoadMacro(os.path.dirname(os.path.realpath(__file__)) + '/dumpevent.C')

ROOT.dumpevent(sys.argv[1], run, lumi, event)
