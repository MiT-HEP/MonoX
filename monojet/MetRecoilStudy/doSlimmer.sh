#! /bin/bash

 eosDir=$1
 subDir=$2
outFile=$3
 NCORES=$4

cd /afs/cern.ch/user/d/dabercro/public/CMSSW_7_4_6/src
eval `scram runtime -sh`
cd -

macroDir='/afs/cern.ch/work/d/dabercro/public/Winter15/MonoX/monojet/MetRecoilStudy'

cp $macroDir/MonoJetTree.h .
cp $macroDir/MonoJetTree.cc .
cp $macroDir/NeroTree.h .
cp $macroDir/NeroTree.C .
cp $macroDir/functions.h .
cp $macroDir/NeroSlimmer.cc .
cp $macroDir/runSlimmer.py .

cp $macroDir/kfactor.root .
cp $macroDir/puWeights_13TeV_25ns.root .
cp $macroDir/scalefactors_ele.root .
cp $macroDir/scalefactors_mu.root .
cp $macroDir/fitTest_0.root .

cp "${outFile%.*}".txt . 

echo "Using "$NCORES" cores!"

RUNNING=0
FIRST=1

for file in `cat "${outFile%.*}".txt`; do
    if [ "$FIRST" -eq 1 ]; then
        ./runSlimmer.py root://eoscms/$eosDir/$subDir/$file $file
        if [ "$NCORES" -gt 1 ]; then
            FIRST=0
        fi
    else
        ./runSlimmer.py root://eoscms/$eosDir/$subDir/$file $file &
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

hadd $subDir.root nero*.root
cp $subDir.root $outFile
