# dumpevent file [run:lumi:event | entry]

import os
import sys

import ROOT
ROOT.gSystem.Load('libPandaTreeObjects.so')
## need to instantiate ROOT.panda (otherwise CLING segfaults)
#e = ROOT.panda.Event

if len(sys.argv) == 3:
    if ':' in sys.argv[2]:
        run, lumi, event = map(int, sys.argv[2].split(':'))
    else:
        run = int(sys.argv[2]) # actually the entry number
        lumi = event = 0
else:
    print 'Bad arguments'
    sys.exit(1)

ROOT.gROOT.LoadMacro(os.path.dirname(os.path.realpath(__file__)) + '/dumpevent.C')

ROOT.dumpevent(sys.argv[1], run, lumi, event)
