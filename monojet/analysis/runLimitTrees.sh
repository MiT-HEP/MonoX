#! /bin/bash

CompileCrombieTools LimitTreeMaker

./MakeMonoJetIncLimitTree.py &
./MakeMonoJetLimitTree.py &
./MakeMonoVLimitTree.py &

wait

echo "All done!"
