#! /bin/bash

outDir=/afs/cern.ch/work/d/dabercro/public/Winter15/exampleOut
numProc=6

######

running=0

for inFile in `ls TerminalList_*.txt`; do
    if [ -f $inFile.done ]; then
        continue
    elif [ ! -f $inFile.running ]; then
        touch $inFile.running
        echo "Running on "$inFile
        cat $inFile | xargs -n2 -P$numProc ./runSlimmer.py
        rm $inFile.running
        touch $inFile.done
    fi
    running=1
done

if [ "$running" -eq 0 ]; then
    cat $outDir/myHadd.txt | xargs -n2 -P$numProc ./haddArgs.sh
fi
