#! /bin/bash

fresh=$1

source CrombieSlimmingConfig.sh

if [ "$fresh" = "fresh" ]
then
    rm $CrombieSkimDir/*.root 2> /dev/null
fi

CrombieFlatSkimmer  --cut 'met>200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 1000000 --numproc $CrombieNLocalProcs --indir $CrombieFullDir --outdir $CrombieSkimDir --json $CrombieGoodRuns --filters 'badResolutionTrack_Jan13.txt' 'csc2015_Dec01.txt' 'ecalscn1043093_Dec01.txt' 'MET_hbheiso.txt' 'MET_hbher2l.txt' 'muonBadTrack_Jan13.txt'

./applyCorrections.py $CrombieSkimDir
