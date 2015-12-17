#! /bin/bash

fresh=$1

source config.sh

filesPerJob=$MonoJetFilesPerJob
numProc=$MonoJetCoresPerLxbatchJob

outDir=$MonoJetFullOutDir
lfsOut=$MonoJetTmpOut
eosDir=$MonoJetNeroEosDir

dirList=$MonoJetSubDirList

if [ "$dirList" = "" ]
then
    dirList=$outDir/dirList.txt
    /afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $eosDir > $dirList
fi

if [ "$CMSSW_BASE" = "" ]
then
    echo "CMSSW_BASE not set. Make sure to cmsenv someplace that you want the jobs to use"
    exit
fi

if [ ! -d bout ]
then
    echo "Making log output directory as ./bout"
    mkdir bout
fi 

if [ ! -d $outDir ]
then
    mkdir $outDir
fi

if [ ! -d $lfsOut ]
then
    mkdir $lfsOut
else
    rm $lfsOut/*.txt
    if [ "$fresh" = "fresh" ]
    then
        rm $lfsOut/*.root
    fi
fi

if [ MonoJetTree.txt -nt MonoJetTree.h ]
then
    ./makeTree.sh
fi

haddFile=$lfsOut/myHadd.txt

> $haddFile

ranOnFile=0

lastDir=''

count=0

for dir in `cat $dirList`
do

    fileInCount=$filesPerJob

    reasonableName="${dir%%/*}"                             # I'm just playing with string cuts here to 
    betterName="${reasonableName%%_Tune*}"                  # automatically generate shorter names for 
    bestName="${betterName%%-madgraph*}"                    # the flat N-tuples
    #bestName="${otherName%%-Prompt*}"     # bestName is what's used to name ntuples

    if [ "$bestName" != "$lastDir" ]
    then 
        count=0
        lastDir=$bestName
        echo "$outDir/monojet_$bestName.root $lfsOut/monojet_"$bestName"_*.root" >> $haddFile
    fi

    for inFile in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select find $eosDir/$dir`
    do
        if [ "${inFile##*_}" = "pilot.root" -o "${inFile##*.}" != "root" ]
        then
            continue
        fi
        inFile="${inFile##*$eosDir/$dir/}"
        
        if [ "$fileInCount" -eq "$filesPerJob" ]
        then
            fileInCount=0
            count=$((count + 1))
            currentConfig=$lfsOut/monojet_$bestName\_$count.txt
            > $currentConfig
        fi
        echo $eosDir/$dir/$inFile >> $currentConfig
        fileInCount=$((fileInCount + 1))
    done
done

rootNames=`ls $lfsOut/monojet_*_*.txt | sed 's/.txt/.root/'`
    
for outFile in $rootNames
do
    if [ ! -f $outFile -o "$fresh" = "fresh" ]
    then
        echo Making: $outFile
        bsub -q $MonoJetLxBatchQueue -n $numProc -o bout/out.%J doSlimmer.sh $outFile $numProc $CMSSW_BASE $PWD
        ranOnFile=1
    fi
done

if [ "$ranOnFile" -eq 0 ]
then
    cat $haddFile | xargs -n2 -P6 ./haddArgs.sh 
    echo "All files merged!"
fi
