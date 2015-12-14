#! /bin/bash

# This is where the slimmer will look for Nero files
# EOS logical path for using LXBATCH
export MonoJetNeroEosDir=/store/user/dmytro/Nero/v1.1.1
# Physical path for interactive running
export MonoJetNeroRegDir=/afs/cern.ch/work/d/dabercro/eos/cms/store/user/dmytro/Nero/v1.1.1
# If you have a list of subdirectories that you want to run on, put it here
# If this is blank, all Nero files in all subdirectories will be run on
export MonoJetSubDirList=example.txt


# This is where you will be putting files
# This is where files will be stored temporarily while skimming over Nero
export MonoJetTmpOut=/afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut
# This is where the full (all events) flat, cleaned ntuples will be stored
export MonoJetFullOutDir=/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesMiniAOD
# This is where you will put skimmed flat ntuples if you skim farther
export MonoJetSkimOutDir=/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmed


# Configuring LXBATCH jobs
# Fewer files means more, faster jobs, but dont change to resubmit
export MonoJetFilesPerLxbatchJob=10
# If you really need to change to make resubmit faster, use this
export MonoJetCoresPerLxbatchJob=1
# Configure which queue you submit to
export MonoJetLxBatchQueue=8nh
