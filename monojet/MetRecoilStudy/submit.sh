#! /bin/bash

outDir='/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees'
eosDir='/store/user/yiiyama/transfer'

for dir in `/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $eosDir`; do

    reasonableName="${dir%%+dmytro*}"
    betterName="${reasonableName%%_Tune*}"
    otherName="${betterName%%-madgraph*}"
    outFile=$outDir/monojet_"${otherName%%-Prompt*}".root

    if [ ! -f $outFile ]; then
        bsub -q 8nh -o bout/out.%J doSlimmer.sh $eosDir $dir $outFile
        echo Making: $outFile
    fi

done