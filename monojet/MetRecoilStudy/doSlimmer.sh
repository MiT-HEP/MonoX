#! /bin/bash

 eosDir=$1
 subDir=$2
outFile=$3

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

RUNNING=0
FIRST=1
for file in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $eosDir/$subDir`; do
    if [ "$FIRST" -eq 1 ]; then
        ./runSlimmer.py root://eoscms/$eosDir/$subDir/$file $file
    else
        ./runSlimmer.py root://eoscms/$eosDir/$subDir/$file $file &
        RUNNING=$((RUNNING+1))
        if [ "$RUNNING" -eq 4 ]; then
            wait
            RUNNING=0
        fi
    fi
done

if [ "$RUNNING" -gt 0 ]; then
    wait
fi

hadd $subDir.root *.root
cp $subDir.root $outFile