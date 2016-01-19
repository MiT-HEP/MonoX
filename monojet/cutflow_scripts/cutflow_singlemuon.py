#! /usr/bin/env python

import os, re, array, ROOT
import sys
from optparse import OptionParser
# Get all the root classes
from ROOT import *
from math import *

# - M A I N ----------------------------------------------------------------------------------------
# Usage: ./cutflow.py -f ROOTFILE -n NUMBEROFEVENTS

# Prepare the command line parser
parser = OptionParser()
parser.add_option("-f", "--file", dest="input_file", default='NeroNtuple.root',
                  help="input root file [default: %default]")
parser.add_option("-t", "--treename", dest="input_tree", default='events',
                  help="root tree name [default: %default]")
parser.add_option("-n", "--nprocs", dest="nprocs", type="int", default=10,
                  help="number of processed entries [default: %default]")
(options, args) = parser.parse_args()

# Open the correct input file and get the event tree
input_file = TFile.Open(options.input_file)
if input_file:
  print 'INFO - Opening input root file: ' + options.input_file
  
else:
  print 'ERROR - Cannot open input root file: ' + options.input_file + ' , exiting!'
  raise SystemExit
  
input_tree = input_file.FindObjectAny(options.input_tree)
if input_tree:
  print 'INFO - Opening root tree: ' + options.input_tree
  
else:
  print 'ERROR - Cannot open root tree: ' + options.input_tree + ' , exiting!'
  raise SystemExit

#initialize 
n_njet=0; n_nmet=0; n_njetid=0; n_nlep=0; n_ntau=0; n_npho=0; n_dphi=0; n_nbjet=0; 
nleptight=0; n_nlepveto=0;n_nleptight=0;

# Check the number of entries in the tree
n_entries = input_tree.GetEntriesFast()
print 'INFO - Input tree entries: ' + str(n_entries)

# Determine number of entries to process
if options.nprocs > 0 and options.nprocs < n_entries:
  n_entries = options.nprocs

print 'INFO - Number of entries to be processed: ' + str(n_entries)

# Loop over the entries
for ientry in range(0,n_entries):
  # Grab the n'th entry
  input_tree.GetEntry(ientry)

  #print 'INFO ------------------------ Event '+str(ientry)+' ------------------------ '

  if not (input_tree.met > 200):
    continue
  n_nmet += 1
  
  if not (input_tree.n_looselep == 1):
    continue
  n_nlep += 1

  if not (input_tree.n_tightlep == 1):
    continue
  n_nleptight += 1

  if not (TMath.Abs(input_tree.lep1PdgId)==13):
    continue
  n_nlepveto += 1

  #if not (input_tree.n_tau == 0):
  #  continue
  #n_ntau += 1
  if (input_tree.n_tau == 0):
    n_ntau += 1

  if not (input_tree.n_loosepho == 0):
    continue
  n_npho += 1
  
  if not (input_tree.n_bjetsMedium == 0):
    continue
  n_nbjet += 1

  #print input_tree.runNum, input_tree.lumiNum, input_tree.eventNum, input_tree.jet1Pt

  if not (input_tree.jet1Pt > 100):
    continue
  n_njet += 1

  if not (input_tree.jet1isMonoJetId == 1):
    continue
  n_njetid += 1


print 'INFO - Single Muon Cut Flow Chart: '
print 'INFO - Full           '+ str(n_entries)
print 'INFO - Met Cut        '+ str(n_nmet)
print 'INFO - NLep Loose Cut '+ str(n_nlep)
print 'INFO - NLep Tight Cut '+ str(n_nleptight)
print 'INFO - NLep Veto Cut  '+ str(n_nlepveto)
print 'INFO - NTau Cut       '+ str(n_ntau)
print 'INFO - NPho Cut       '+ str(n_npho)
print 'INFO - Nbjet          '+ str(n_nbjet)
print 'INFO - Jet Cut        '+ str(n_njet)
print 'INFO - Jet Id Cut     '+ str(n_njetid)
