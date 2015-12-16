#! /bin/bash

 outFile=$1
  NCORES=$2
 cmsbase=$3
macroDir=$4

cd $cmsbase/src
eval `scram runtime -sh`
cd -

cp $macroDir/MonoJetTree.h .
cp $macroDir/MonoJetTree.cc .
cp $macroDir/NeroTree.h .
cp $macroDir/NeroTree.C .
cp $macroDir/functions.h .
cp $macroDir/NeroSlimmer.cc .
cp $macroDir/runSlimmer.py .

mkdir files
cp $macroDir/files/*.root files/.

cp "${outFile%.*}".txt . 

echo "Trying to make $outFile"
echo ""
echo "Using "$NCORES" cores!"

RUNNING=0
FIRST=1
NUM=0

for file in `cat "${outFile%.*}".txt`; do
    if [ "$FIRST" -eq 1 ]; then
        ./runSlimmer.py root://eoscms/$file output_$NUM.root
        NUM=$((NUM+1))
        if [ "$NCORES" -gt 1 ]; then
            FIRST=0
        fi
    else
        ./runSlimmer.py root://eoscms/$file output_$NUM.root &
        NUM=$((NUM+1))
        RUNNING=$((RUNNING+1))
        if [ "$RUNNING" -eq "$NCORES" ]; then
            wait
            RUNNING=0
        fi
    fi
done

if [ "$RUNNING" -gt 0 ]; then
    wait
fi

hadd hadded.root output_*.root

echo ""
echo "Copying to $outFile"

cp hadded.root $outFile
