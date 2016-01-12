#! /bin/bash

source CrombieConfig

CrombieFlatSkimmer --tree 'events' --copy 'htotal' --run 'runNum' --lumi 'lumiNum' --freq 100000 --numproc $CrombieNLocalProcs --indir $CrombieFullDir --outdir $CrombieSkimDir --cut $CrombieSkimCuts 
