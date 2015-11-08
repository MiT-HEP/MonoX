#! /bin/bash

#./FlatSlimmer.py 6 "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/" "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmed"
./FlatSlimmer.py 6 "/afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut" "/afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut/skimmed"

cat /afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut/skimmed/myHadd.txt | xargs -n2 -P6 ./haddArgs.sh
