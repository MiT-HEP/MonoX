#! /bin/bash

inDir=/afs/cern.ch/work/d/dabercro/eos/cms/store/caf/user/yiiyama/nerov3redo
outDir=/afs/cern.ch/work/d/dabercro/public/Winter15/exampleOut
filesPerTerminal=50

######

if [ ! -d $outDir ]; then
    mkdir $outDir
fi

if [ ! -d $outDir/merged ]; then
    mkdir $outDir/merged
fi

countFiles=0
countLists=0

rm TerminalList_*

touch TerminalList_$countLists.txt
touch $outDir/myHadd.txt

for aDir in `ls $inDir`; do
    indexFiles=0
    echo $outDir/merged/$aDir.root $outDir/$aDir\_*.root >> $outDir/myHadd.txt
    for inFile in `ls $inDir/$aDir`; do
        extension="${inFile##*_}"
        if [ "${inFile##*_}" = "pilot.root" ]; then
            echo $inFile
            continue
        elif [ "${inFile##*.}" == "root" ]; then
            echo $inDir/$aDir/$inFile $outDir/$aDir\_$indexFiles.root >> TerminalList_$countLists.txt
            indexFiles=$((indexFiles + 1))
            countFiles=$((countFiles + 1))
            if [ "$countFiles" = "$filesPerTerminal" ]; then
                countFiles=0
                countLists=$((countLists + 1))
                touch TerminalList_$countLists.txt
            fi
        fi
    done
done

