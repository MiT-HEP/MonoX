#! /bin/bash

CompileCrombieTools LimitTreeMaker

source CrombieAnalysisConfig.sh
mkdir -p $CrombieOutLimitTreeDir 2> /dev/null

./MakeMonoJetIncLimitTree.py &
./MakeMonoJetLimitTree.py &
./MakeMonoVLimitTree.py &

wait

echo "All done!"
