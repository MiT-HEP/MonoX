#!/bin/bash

# edit parameters_ggh.py to point sourcename = injection.root and outname = 'workspace.root' cardname = 'datacard.dat'

THISDIR=$(cd $(dirname $0); pwd)

SIGS="$1"
FAKEN="$2"
IJOB=$3

HIST=/data/t3home000/$USER/monophoton

rm -f norms.dat

for sigs in $SIGS
do
  for faken in $FAKEN
  do
    i=0
    while [ $i -lt 20 ]
    do
      python $THISDIR/injection_test.py $HIST/plots/gghgFakeRandom_blind_combined.root $HIST/plots/gghg_blind_combined.root $sigs $faken injection.root
      python $THISDIR/../fit/workspace.py $THISDIR/../fit/parameters_ggh.py
      combine datacard.dat -M FitDiagnostics --saveNormalizations --saveShapes
      [ $? -eq 0 ] || continue
      echo $sigs $faken $(python $THISDIR/fetch_norm.py $PWD/figDiagnostics.root) >> norms.dat
      i=$(($i+1))
    done
    mv norms.dat $HIST/fakemet/norms_${sigs}_${faken}_${IJOB}.dat
  done
done
