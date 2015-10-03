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

for file in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $eosDir/$subDir`; do
    ./runSlimmer.py root://eoscms/$eosDir/$subDir/$file $file
done

hadd $subDir.root *.root
cp $subDir.root $outFile