#!/bin/bash

# edit parameters_ggh.py to point sourcename = injection.root and outname = 'workspace.root' cardname = 'datacard.dat'

THISDIR=$(cd $(dirname $0); pwd)

SIGS="$1"
FAKEN="$2"
IJOB=$3
SOURCE=$4

HIST=/data/t3home000/$USER/monophoton

rm -f norms.dat

for sigs in $SIGS
do
  for faken in $FAKEN
  do
    i=0
    while [ $i -lt 20 ]
    do
      python $THISDIR/injection_test.py $HIST/plots/${SOURCE}.root $HIST/plots/gghg.root $sigs $faken injection.root
      python $THISDIR/../fit/workspace.py $THISDIR/../fit/parameters_ggh.py
      combine datacard.dat -M FitDiagnostics --saveNormalizations --saveShapes
      mkdir -p $HIST/fakemet/fits_${sigs}_${faken}_${IJOB}
      python $THISDIR/plotfit.py fitDiagnostics.root $HIST/plots/${SOURCE}.root fits_${sigs}_${faken}_${IJOB}/${i} $sigs $faken
      [ $? -eq 0 ] || continue
      echo $sigs $faken $(python $THISDIR/fetch_norm.py $PWD/fitDiagnostics.root) >> norms.dat
      i=$(($i+1))
    done
    mv norms.dat $HIST/fakemet/norms_${sigs}_${faken}_${IJOB}.dat
  done
done
