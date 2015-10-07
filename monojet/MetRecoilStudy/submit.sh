#! /bin/bash

fresh=$1

filesPerJob=13
numProc=6

outDir='/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees'
lfsOut='/afs/cern.ch/work/d/dabercro/public/Winter15/lxbatchOut'
eosDir='/store/user/yiiyama/transfer'
skimmedDir='/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmed'

if [ ! -d $outDir ]; then
    mkdir $outDir
fi

if [ ! -d $lfsOut ]; then
    mkdir $lfsOut
else
    rm $lfsOut/*.txt
fi

if [ ! -d $lfsOut/skimmed ]; then
    mkdir $lfsOut/skimmed
fi

if [ MonoJetTree.txt -nt MonoJetTree.h ]; then
    ./makeTree.sh
fi

haddFile=$lfsOut/myHadd.txt
haddSkimmed=$lfsOut/skimmed/myHadd.txt

> $haddFile

> $haddSkimmed

ranOnFile=0

for dir in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $eosDir`; do

    count=0
    fileInCount=$filesPerJob

    reasonableName="${dir%%+dmytro*}"                       # I'm just playing with string cuts here to 
    betterName="${reasonableName%%_Tune*}"                  # automatically generate shorter names for 
    otherName="${betterName%%-madgraph*}"                   # the flat N-tuples
    bestName="${otherName%%-Prompt*}"

    for inFile in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls -1 $eosDir/$dir`; do
        if [ "$fileInCount" -eq "$filesPerJob" ]; then
            fileInCount=0
            count=$((count + 1))
            currentConfig=$lfsOut/monojet_$bestName\_$count.txt
            > $currentConfig
        fi
        echo $inFile >> $currentConfig
        fileInCount=$((fileInCount + 1))
    done

    rootNames=`ls $lfsOut/monojet_$bestName\_*.txt | sed 's/.txt/.root/'`

    echo "$outDir/monojet_$bestName.root $lfsOut/monojet_"$bestName"_*.root" >> $haddFile
    echo "$skimmedDir/monojet_$bestName.root $lfsOut/skimmed/monojet_"$bestName"_*.root">> $haddSkimmed

    for outFile in $rootNames; do
        if [ ! -f $outFile -o "$fresh" = "fresh" ]; then
            bsub -q 1nh -n $numProc -o bout/out.%J doSlimmer.sh $eosDir $dir $outFile $numProc
            echo Making: $outFile
            ranOnFile=1
        fi
    done
done

if [ "$ranOnFile" -eq 0 ]; then
#    cat $haddSkimmed | xargs -n2 -P6 ./haddArgs.sh 
#    echo "Skimmed files merged!"
    cat $haddFile | xargs -n2 -P6 ./haddArgs.sh 
    echo "All files merged!"
fi
