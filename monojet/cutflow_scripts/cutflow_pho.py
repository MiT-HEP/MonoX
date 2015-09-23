#! /usr/bin/env python

import os, re, array, ROOT
import sys
from optparse import OptionParser
# Get all the root classes
from ROOT import *
from math import *

gROOT.ProcessLine(".x functions.C");

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
n_jet=0; n_met=0; n_njet=0; n_nlep=0; n_ntau=0; n_npho=0; n_dphi=0;n_2ndjet=0;
n_mu_tight=0; n_mt=0; n_fakemet=0;

n_pho=0;

n_jet_cr_sm=0; n_2ndjet_cr_sm=0; n_dphi_cr_sm=0; n_njet_cr_sm=0;  n_nlep_cr_sm=0; n_ntau_cr_sm=0; n_npho_cr_sm=0; n_mu_tight_cr_sm=0; n_mt_cr_sm=0;n_fakemet_cr_sm=0;

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

  fakeMET = -1

  new_jetPt = std.vector('double')()
  new_jetPhi = std.vector('double')()
  new_jetTightId = std.vector('bool')()
  new_jetSecondId = std.vector('bool')()
  new_jetPt.clear()
  new_jetPhi.clear()
  new_jetTightId.clear()
  new_jetSecondId.clear()

  foundPhoton = False

  if(input_tree.photonP4.GetEntriesFast()>0 ):
    for i in range (0,input_tree.photonP4.GetEntriesFast()):
      if (input_tree.photonP4[i].Pt() > 175 and fabs(input_tree.photonP4[i].Eta()) < 2.4):
        foundPhoton = True
        fakeMET = vectorSumPt(input_tree.metP4[0].Pt(), input_tree.metP4[0].Phi(),input_tree.photonP4[i].Pt(), input_tree.photonP4[i].Phi())

        #check for overlapping taus
        #if(input_tree.tauP4.GetEntriesFast() > 0):
        #  for t in range(0,input_tree.tauP4.GetEntriesFast()):
        #    dRt = deltaR(input_tree.lepP4[i].Phi(),input_tree.lepP4[i].Eta(),input_tree.tauP4[t].Phi(),input_tree.tauP4[t].Eta())
        #    if (dRt > 0.4):
        #      new_tauPt.push_back(input_tree.tauP4[t].Pt())

        #check for overlapping jets
        if(input_tree.jetP4.GetEntriesFast() > 0):
           for j in range(0,input_tree.jetP4.GetEntriesFast()):
             dRj = deltaR(input_tree.photonP4[i].Phi(),input_tree.photonP4[i].Eta(),input_tree.jetP4[j].Phi(),input_tree.jetP4[j].Eta())
             if (dRj > 0.4): 
               new_jetPt.push_back(input_tree.jetP4[j].Pt())
               #print j, input_tree.jetMonojetId[j], input_tree.jetMonojetIdLoose[j]
               new_jetTightId.push_back(input_tree.jetMonojetId[j])
               new_jetSecondId.push_back(input_tree.jetMonojetIdLoose[j])
               new_jetPhi.push_back(input_tree.jetP4[j].Phi())

  dphi = -10000.
  
  if(new_jetPt.size() > 1 and new_jetPt[0] > 110. and new_jetTightId[0] and new_jetSecondId[1]) :
    dphi = deltaPhi( new_jetPhi[0], new_jetPhi[1])
  else:
     if (new_jetPt.size() < 2):
       dphi= -99.999
     else:
       dphi = -10000.


  if(input_tree.photonP4.GetEntriesFast()==1 and foundPhoton):
    n_pho +=1
    if(new_jetPt.size() > 0 and new_jetPt[0]>110. and new_jetTightId[0]):
      n_jet += 1
      if(new_jetPt.size() == 1 or (new_jetPt.size() > 1 and new_jetSecondId[1]) ):
        n_2ndjet += 1
        if( fabs(dphi) < 2.5  or dphi == -99.999 ):
          n_dphi += 1
          if(new_jetPt.size() < 3):
            n_njet += 1
            if(input_tree.lepP4.GetEntriesFast() < 1): 
              n_nlep += 1
#             if( new_tauPt.size() < 1 ):
              if( input_tree.tauP4.GetEntriesFast() < 1 ):
                n_ntau += 1
                if(fakeMET > 200):
                  n_fakemet +=1




print " -> Control Region <- "                  
print 'INFO - Photon Control Region Cut Flow Chart: '
print 'INFO - Full     '+ str(n_entries)
print 'INFO - NPh Cut  '+ str(n_pho)
print 'INFO - Jet Cut  '+ str(n_jet)
