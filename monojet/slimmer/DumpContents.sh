#! /bin/bash

source config.sh

filesPerJob=$MonoJetFilesPerJob
inDir=$MonoJetNeroRegDir
outDir=$MonoJetTmpOut
fullDir=$MonoJetFullOutDir
filesPerTerminal=$MonoJetFilesPerJob

dirList=$MonoJetSubDirList

if [ "$dirList" = "" ]
then
    dirList=$outDir/dirList.txt
    ls $inDir > $dirList
fi

if [ "$CMSSW_BASE" = "" ]
then
    echo "CMSSW_BASE not set. Make sure to cmsenv someplace that you want the jobs to use"
    exit
fi

if [ ! -d $outDir ]; then
    mkdir $outDir
fi

if [ ! -d $fullDir ]; then
    mkdir $fullDir
fi

countFiles=0
countLists=0

if [ ! -d $outDir/TerminalRunning ]
then
    mkdir $outDir/TerminalRunning
fi

if [ MonoJetTree.txt -nt MonoJetTree.h ]
then
    ./makeTree.sh
fi

echo '' > $outDir/myHadd.txt

lastDir=''

for aDir in `cat $dirList`
do
    reasonableName="${aDir%%+dmytro*}"                      # I'm just playing with string cuts here to 
    reasonableName="${reasonableName%%/*}"
    betterName="${reasonableName%%_Tune*}"                  # automatically generate shorter names for 
    bestName="${betterName%%-madgraph*}"                    # the flat N-tuples

    if [ "$bestName" != "$lastDir" ]
    then 
        count=0
        lastDir=$bestName
        echo "$fullDir/monojet_$bestName.root $outDir/monojet_"$bestName"_*.root" >> $outDir/myHadd.txt
        indexFiles=0
    fi

    fileInCount=$filesPerJob

    for inFile in `find $inDir/$aDir -name '*.root'`; do
        if [ "${inFile##*_}" = "pilot.root" ]; then
            continue
        elif [ "${inFile##*.}" == "root" ]; then
            if [ "$fileInCount" -eq "$filesPerJob" ]
            then
                fileInCount=0
                count=$((count + 1))
                currentConfig=$outDir/monojet_$bestName\_$count.txt
                > $currentConfig
            fi
            echo $inFile $outDir/TerminalRunning/monojet_$bestName\_$count\_$indexFiles.root >> $currentConfig
            fileInCount=$((fileInCount + 1))
            indexFiles=$((indexFiles + 1))
        fi
    done
done
