#!/bin/bash

# edit parameters_fakemet.py to point sourcename = injection.root and outname = 'workspace.root' cardname = 'datacard.dat'

SOURCE="$1"
SIGS="$2"
FAKEN="$3"
IJOB=$3

HIST=/data/t3home000/$USER/monophoton
FAKEMET=$MONOPHOTON/fakemet

rm -f $THISDIR/norms.dat

echo $HIST
echo $FAKEMET
echo $PWD

i=0
while [ $i -lt 20 ]
do
    python $FAKEMET/injection_test.py $HIST/plots/gghg${SOURCE}.root $HIST/plots/gghg.root $SIGS $FAKEN $PWD/injection.root
    python $FAKEMET/../fit/workspace.py $FAKEMET/../fit/parameters_fakemet.py
    combine $PWD/datacard.dat -M FitDiagnostics --saveNormalizations --saveShapes --saveWithUncertainties
    mkdir -p $HIST/fakemet/${SOURCE}/fits_${SIGS}_${FAKEN}_${IJOB}
    python $FAKEMET/plotfit.py fitDiagnostics.root $HIST/plots/gghg${SOURCE}.root ${SOURCE}/fits_${SIGS}_${FAKEN}_${IJOB}/${i} $SIGS $FAKEN
    [ $? -eq 0 ] || continue
    echo $SIGS $FAKEN $(python $FAKEMET/fetch_norm.py $PWD/fitDiagnostics.root) >> $PWD/norms.dat
    i=$(($i+1))
done
mv $PWD/norms.dat $HIST/fakemet/${SOURCE}/norms_${SIGS}_${FAKEN}_${IJOB}.dat

