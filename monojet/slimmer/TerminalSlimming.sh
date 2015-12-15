#! /bin/bash

fresh=$1

source config.sh

outDir=$MonoJetTmpOut
numProc=$MonoJetCoresPerLocalJob

if [ "$fresh" = "fresh" ]
then
    rm $outDir/*.root
    if [ -d $outDir/TerminalRunning ]
    then
        rm $outDir/TerminalRunning/*
    fi
fi

running=0

countFiles=`ls $outDir/TerminalRunning/*.txt.running | wc -l`

if [ "$countFiles" -eq "0" ]
then
    ./DumpContents.sh
    ./runSlimmer.py compile
fi

for inFile in `ls $outDir/monojet_*.txt`
do
    inFile="${inFile##*/}"
    inRoot="${inFile%%.txt}"
    if [ -f $outDir/TerminalRunning/$inFile.done -o -f $outDir/$inRoot.root ]
    then
        continue
    elif [ ! -f $outDir/TerminalRunning/$inFile.running ]
    then
        touch $outDir/TerminalRunning/$inFile.running
        echo "Running on "$inFile
        cat $outDir/$inFile | xargs -n2 -P$numProc ./runSlimmer.py
        hadd $outDir/$inRoot.root $outDir/TerminalRunning/$inRoot\_*.root
        rm $outDir/TerminalRunning/$inRoot\_*.root
        rm $outDir/TerminalRunning/$inFile.running
        touch $outDir/TerminalRunning/$inFile.done
    fi
    running=1
done

if [ "$running" -eq 0 ]
then
    cat $outDir/myHadd.txt | xargs -n2 -P$numProc ./haddArgs.sh
fi
