#! /bin/bash

source CrombieSlimmingConfig.sh

CrombieFlatSkimmer  --cut 'met > 200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 1000000 --numproc $CrombieNLocalProcs --indir /afs/cern.ch/work/d/dabercro/public/Winter15/FullOut/Purity --outdir /afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/Purity --json $CrombieGoodRuns --filters 'files/badResolutionTrack_Jan13.txt' 'files/csc2015_Dec01.txt' 'files/ecalscn1043093_Dec01.txt' 'files/MET_hbheiso.txt' 'files/MET_hbher2l.txt' 'files/muonBadTrack_Jan13.txt'
