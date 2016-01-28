#! /bin/bash

fresh=$1

source CrombieSlimmingConfig.sh

if [ "$fresh" = "fresh" ]
then
    rm $CrombieSkimDir/*.root 2> /dev/null
fi

CrombieFlatSkimmer  --cut 'met>200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 1000000 --numproc $CrombieNLocalProcs --indir $CrombieFullDir --outdir $CrombieSkimDir --json $CrombieGoodRuns --filters 'files/badResolutionTrack_Jan13.txt' 'files/csc2015_Dec01.txt' 'files/ecalscn1043093_Dec01.txt' 'files/MET_hbheiso.txt' 'files/MET_hbher2l.txt' 'files/muonBadTrack_Jan13.txt'

hadd -f /afs/cern.ch/work/d/dabercro/public/Winter15/allData/monojet_Data.root $CrombieSkimDir/monojet_MET+Run* $CrombieSkimDir/monojet_Single*

CrombieFlatSkimmer  --cut 'met>200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 100000 --numproc 1 --indir /afs/cern.ch/work/d/dabercro/public/Winter15/allData --outdir $CrombieSkimDir --json $CrombieGoodRuns -d

./applyCorrections.py $CrombieSkimDir
