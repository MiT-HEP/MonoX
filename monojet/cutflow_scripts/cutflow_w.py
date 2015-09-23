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

  #print deltaPhi(input_tree.jetP4[0].Phi(),input_tree.jetP4[1].Phi() )
  #print 'INFO ------------------------ Event '+str(ientry)+' ------------------------ '

#<<<<<<< HEAD:monojet/cutflow_scripts/cutflow2.py
#  dphi = -10000.
#  
#  if(input_tree.jetP4.GetEntriesFast() > 1 and input_tree.jetP4[0].Pt() > 110 and input_tree.jetMonojetId[0]==1 and input_tree.jetMonojetIdLoose[1]==1) : # and input_tree.jetPuId() > -0.62) : 
#    dphi = deltaPhi( input_tree.jetP4[0].Phi(),input_tree.jetP4[1].Phi() )
#  else:
#     if (input_tree.jetP4.GetEntriesFast() < 2):
#       dphi= -99.999
#     else:
#       dphi = -10000.
#
#  if (input_tree.jetP4.GetEntriesFast() > 0 and input_tree.jetP4[0].Pt() > 110 and input_tree.jetMonojetId[0]==1):
#    n_jet += 1
#    if (input_tree.jetP4.GetEntriesFast() == 1 or (input_tree.jetP4.GetEntriesFast() > 1 and input_tree.jetMonojetIdLoose[1]==1 )):
#      n_2ndjet += 1
#      if( fabs(dphi) < 2.5  or dphi == -99.999 ):
#        n_dphi += 1
#        if(input_tree.metP4[0].Energy() > 200 ):  
#          n_met += 1
#          if(input_tree.jetP4.GetEntriesFast() < 3): 
#            n_njet += 1
#            if(input_tree.lepP4.GetEntriesFast() < 1): 
#              n_nlep += 1
#              if(input_tree.tauP4.GetEntriesFast() < 1): 
#                n_ntau += 1
#                if(input_tree.photonP4.GetEntriesFast() < 1):
#                  n_npho += 1
#                  
#
#
#=======
#>>>>>>> zeynep/master:monojet/cutflow_scripts/cutflow_w.py
### Control Region Calculations ##########
  

  MT = -1
  fakeMET = -1
  foundMu = False
  foundTightMu = False
  foundEl = False
  overlap = False

  new_jetPt = std.vector('double')()
  new_jetPhi = std.vector('double')()
  new_jetTightId = std.vector('int')()
  new_jetSecondId = std.vector('int')()
  new_jetPt.clear()
  new_jetPhi.clear()
  new_jetTightId.clear()
  new_jetSecondId.clear()
  new_tauPt = std.vector('double')()
  new_tauPt.clear()
  new_tightMuPt = std.vector('double')()
  new_tightMuPt.clear()


  if(input_tree.lepP4.GetEntriesFast()>0 ):
    for i in range (0,input_tree.lepP4.GetEntriesFast()):
      if (fabs(input_tree.lepPdgId[i]) == 11 ):
        foundEl = True
#<<<<<<< HEAD:monojet/cutflow_scripts/cutflow2.py
      if (fabs(input_tree.lepPdgId[i]) == 13 and input_tree.lepP4[i].Pt() > 20. and input_tree.lepSelBits[i]  & (0x1 << 5) != 0 ):
                
#=======
#      if (fabs(input_tree.lepPdgId[i]) == 13 and input_tree.lepP4[i].Pt() > 20. and input_tree.lepSelBits[i] & (0x1 << 4) !=0 and (input_tree.lepIso[i]/input_tree.lepP4[i].Pt()) < 0.12):
#>>>>>>> zeynep/master:monojet/cutflow_scripts/cutflow_w.py
        foundTightMu = True
        new_tightMuPt.push_back(input_tree.lepP4[i].Pt())
        MT = transverseMass(input_tree.lepP4[i].Pt(), input_tree.lepP4[i].Phi(),input_tree.metP4[0].Energy(),input_tree.metP4[0].Phi())
        fakeMET = input_tree.metP4[0].Energy() +  input_tree.lepPfPt[i]

        #check for overlapping taus
        if(input_tree.tauP4.GetEntriesFast() > 0):
          for t in range(0,input_tree.tauP4.GetEntriesFast()):
            dRt = deltaR(input_tree.lepP4[i].Phi(),input_tree.lepP4[i].Eta(),input_tree.tauP4[t].Phi(),input_tree.tauP4[t].Eta())
            if (dRt > 0.4):
              new_tauPt.push_back(input_tree.tauP4[t].Pt())

        #check for overlapping jets
        if(input_tree.jetP4.GetEntriesFast() > 0):
           for j in range(0,input_tree.jetP4.GetEntriesFast()):
             dRj = deltaR(input_tree.lepP4[i].Phi(),input_tree.lepP4[i].Eta(),input_tree.jetP4[j].Phi(),input_tree.jetP4[j].Eta())
             if (dRj > 0.4): 
               new_jetPt.push_back(input_tree.jetP4[j].Pt())

               #print input_tree.jetMonojetId[j], input_tree.jetMonojetIdLoose[j]

               new_jetTightId.push_back(int(input_tree.jetMonojetId[j] is True))
               new_jetSecondId.push_back(int(input_tree.jetMonojetIdLoose[j] is True))
               new_jetPhi.push_back(input_tree.jetP4[j].Phi())

  dphi_cr = -10000.
  
  if(new_jetPt.size() > 1 and new_jetPt[0] > 110. and new_jetTightId[0] and new_jetSecondId[1]) :
    dphi_cr = deltaPhi( new_jetPhi[0], new_jetPhi[1])
  else:
     if (new_jetPt.size() < 2):
       dphi_cr= -99.999
     else:
       dphi_cr = -10000.


  if(foundTightMu and new_tightMuPt.size()==1):
    n_mu_tight_cr_sm += 1
    if(new_jetPt.size() > 0 and new_jetPt[0]>110. and new_jetTightId[0]):
      n_jet_cr_sm += 1
      if(new_jetPt.size() == 1 or (new_jetPt.size() > 1 and new_jetSecondId[1]) ):
        n_2ndjet_cr_sm += 1
        if( fabs(dphi_cr) < 2.5  or dphi_cr == -99.999 ):
          n_dphi_cr_sm += 1
          if(input_tree.jetP4.GetEntriesFast() < 3): 
            n_njet_cr_sm += 1
            if( not foundEl ): 
              n_nlep_cr_sm += 1
              if( new_tauPt.size() < 1 ):
                n_ntau_cr_sm += 1
                if(input_tree.photonP4.GetEntriesFast() < 1):
                  n_npho_cr_sm += 1
                  if(foundTightMu):
                    n_mu_tight_cr_sm += 1
                    if(MT > 50):
                      n_mt_cr_sm += 1
                      if(fakeMET > 200):
                        n_fakemet_cr_sm +=1

print " -> Control Region <- "
                  
print 'INFO - Single Mu Control Region Cut Flow Chart: '
print 'INFO - Full     '+ str(n_entries)
print 'INFO - NMu Cut  '+ str(n_mu_tight_cr_sm)
print 'INFO - Jet Cut  '+ str(n_jet_cr_sm)
print 'INFO - 2_j Cut  '+ str(n_2ndjet_cr_sm)
print 'INFO - Phi Cut  '+ str(n_dphi_cr_sm)
print 'INFO - NJet Cut '+ str(n_njet_cr_sm)
print 'INFO - NLep Cut '+ str(n_nlep_cr_sm)
print 'INFO - NTau Cut '+ str(n_ntau_cr_sm)
print 'INFO - NPho Cut '+ str(n_npho_cr_sm)
print 'INFO - NMt Cut  '+ str(n_mt_cr_sm)
print 'INFO - NMet Cut '+ str(n_fakemet_cr_sm)
