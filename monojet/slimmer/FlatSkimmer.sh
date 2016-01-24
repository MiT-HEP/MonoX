#! /bin/bash

fresh=$1

source CrombieSlimmingConfig.sh

if [ "$fresh" = "fresh" ]
then
    rm $CrombieSkimDir/*.root 2> /dev/null
fi

CrombieFlatSkimmer  --cut 'met>200' --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 1000000 --numproc $CrombieNLocalProcs --indir $CrombieFullDir --outdir $CrombieSkimDir --json $CrombieGoodRuns
