"""
Likely an attempt to plot background events using MC. Incomplete.
"""

import sys
import os
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
from plotstyle import SimpleCanvas

import ROOT
ROOT.gROOT.SetBatch(True)

groups = {
    'dy': (['dy-50'], ROOT.TColor.GetColor(0xff, 0x88, 0x44)),
    'top': (['tt'], ROOT.TColor.GetColor(0x66, 0xff, 0xdd))
    'w': (['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600'], ROOT.TColor.GetColor(0xaa, 0xff, 0x77)),
    'vv': (['ww', 'wz', 'zz'], ROOT.TColor.GetColor(0xaa, 0x55, 0xff))
}

for gname in ['vv', 'top', 'w', 'dy']:
    samples, color = groups[gname]

    egTree = ROOT.TChain('events')
    mgTree = ROOT.TChain('events')
    for sname in samples:
        egTree.Add(config.skimDir + '/' + )
    
