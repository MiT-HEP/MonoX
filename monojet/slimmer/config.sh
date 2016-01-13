#! /bin/bash

# This is where the slimmer will look for Nero files
# EOS logical path for using LXBATCH
export MonoJetNeroEosDir=/store/user/amarini/Nero/v1.2
# Physical path for interactive running
export MonoJetNeroRegDir=/afs/cern.ch/work/d/dabercro/eos/cms$MonoJetNeroEosDir
# If you have a list of subdirectories that you want to run on, put it here
# If this is blank, all Nero files in all subdirectories will be run on
export MonoJetSubDirList=SubDirList.txt

# This is where you will be putting files
# This is where files will be stored temporarily while skimming over Nero
export MonoJetTmpOut=/afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut
# This is where the full (all events) flat, cleaned ntuples will be stored
export MonoJetFullOutDir=/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesMiniAOD

# Configuring LXBATCH/interactive jobs
# Fewer files means more, faster jobs, but don't change to resubmit
export MonoJetFilesPerJob=10
# If you really need to change to make resubmit faster, use this
export MonoJetCoresPerLxbatchJob=1
# Configure which queue you submit to
export MonoJetLxBatchQueue=1nh
# This is for local slimming. Make this higher to take advantage of lxplus computers
# I personally usually make this less than `nproc` just so I don't inconvenience other users, but you might just want to set this to `nproc`
export MonoJetCoresPerLocalJob=6

# Additional configuration for skimming and applying GoodRuns
# Note skimming also uses $MonoJetCoresPerLocalJob set for interactive jobs
export MonoJetGoodRunsFile=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt
# View MonoJetTree.txt to see possible branches to cut on
export MonoJetSkimmingCut='met>150&&jet1isMonoJetId==1&&jet1isMonoJetIdNew==1'
# This is where you will put skimmed flat ntuples if you skim farther
export MonoJetSkimOutDir=/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmed
