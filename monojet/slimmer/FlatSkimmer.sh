#! /bin/bash

fresh=$1

source CrombieSlimmingConfig.sh

if [ "$fresh" = "fresh" ]
then
    rm $CrombieSkimDir/*.root 2> /dev/null
    rm $CrombieSkimDir/*/*.root 2> /dev/null
fi

CrombieFlatSkimmer  --cut 'met > 200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 1000000 --numproc $CrombieNLocalProcs --indir $CrombieFullDir --outdir $CrombieSkimDir --json $CrombieGoodRuns --filters 'files/badResolutionTrack_Jan13.txt' 'files/csc2015_Dec01.txt' 'files/ecalscn1043093_Dec01.txt' 'files/MET_hbheiso.txt' 'files/MET_hbher2l.txt' 'files/muonBadTrack_Jan13.txt'

hadd -f /afs/cern.ch/work/d/dabercro/public/Winter15/allData/monojet_Data.root $CrombieSkimDir/monojet_MET+Run* $CrombieSkimDir/monojet_Single*

CrombieFlatSkimmer  --cut 'met > 200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 100000 --numproc 1 --indir /afs/cern.ch/work/d/dabercro/public/Winter15/allData --outdir $CrombieSkimDir --json $CrombieGoodRuns -d

cp $CrombieSkimDir/monojet_TTJets* /afs/cern.ch/work/d/dabercro/public/Winter15/topSkim/.
cp $CrombieSkimDir/monojet_ST* /afs/cern.ch/work/d/dabercro/public/Winter15/topSkim/.

if [ ! -d $CrombieSkimDir/Purity ]
then
    mkdir $CrombieSkimDir/Purity
fi

CrombieFlatSkimmer  --cut 'fatjet1DRGenW < 0.4' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 100000 --numproc $CrombieNLocalProcs --indir /afs/cern.ch/work/d/dabercro/public/Winter15/topSkim --outdir $CrombieSkimDir/topRes --json $CrombieGoodRuns

CrombieFlatSkimmer  --cut 'fatjet1DRGenW > 0.4' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 100000 --numproc $CrombieNLocalProcs --indir /afs/cern.ch/work/d/dabercro/public/Winter15/topSkim --outdir $CrombieSkimDir/topNonRes --json $CrombieGoodRuns

./applyCorrections.py $CrombieSkimDir

./applyCorrections.py $CrombieSkimDir/topRes
./applyCorrections.py $CrombieSkimDir/topNonRes
./applyTriggers.py $CrombieSkimDir/topRes
./applyTriggers.py $CrombieSkimDir/topNonRes

cp $CrombieSkimDir/monojet_GJets* $CrombieSkimDir/Purity/.

./applyTriggers.py $CrombieSkimDir
./applyPurity.py $CrombieSkimDir/Purity
