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

# Configuring LXBATCH/interactive jobs
# Fewer files means more, faster jobs, but don't change to resubmit
export MonoJetFilesPerJob=10
# If you really need to change to make resubmit faster, use this
export MonoJetCoresPerLxbatchJob=1
# This is for local slimming. Make this higher to take advantage of lxplus computers
# I personally usually make this less than `nproc` just so I don't inconvenience other users, but you might just want to set this to `nproc`
export MonoJetCoresPerLocalJob=6
# Configure which queue you submit to
export MonoJetLxBatchQueue=8nh

# Additional configuration for skimming
export MonoJetGoodRunsFile=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON.txt
# View MonoJetTree.txt to see possible branches to cut on
export MonoJetSkimmingCut='met>50'
# Note skimming also uses $MonoJetCoresPerLocalJob set for interactive jobs
