#! /bin/bash

inDir=/afs/cern.ch/work/d/dabercro/eos/cms/store/caf/user/yiiyama/nerov3redo
outDir=/afs/cern.ch/work/d/dabercro/public/Winter15/exampleOut
filesPerTerminal=10

######

arr=("DYJetsToNuNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" "MET+Run2015D-PromptReco-v3+AOD" "SingleMuon+Run2015C-PromptReco-v1+AOD" "WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" "WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" "WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3+AODSIM" "WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" "WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM")

if [ ! -d $outDir ]; then
    mkdir $outDir
fi

if [ ! -d $outDir/merged ]; then
    mkdir $outDir/merged
fi

countFiles=0
countLists=0

rm TerminalList_*

echo '' > TerminalList_$countLists.txt
echo '' > $outDir/myHadd.txt

for aDir in `ls $inDir`; do
#    if [ "$aDir" = "DYJetsToNuNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ] || [ "$aDir" = "MET+Run2015D-PromptReco-v3+AOD" ] || [ "$aDir" = "SingleMuon+Run2015C-PromptReco-v1+AOD" ] || [ "$aDir" = "WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ] || [ "$aDir" = "WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ] || [ "$aDir" = "WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3+AODSIM" ] || [ "$aDir" = "WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ] || [ "$aDir" = "WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ]; then
    if [ "$aDir" = "WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM" ]; then

        reasonableName="${aDir%%+dmytro*}"                       # I'm just playing with string cuts here to 
        betterName="${reasonableName%%_Tune*}"                  # automatically generate shorter names for 
        otherName="${betterName%%-madgraph*}"                   # the flat N-tuples

        indexFiles=0
        echo $outDir/merged/monojet_$otherName.root $outDir/$aDir"_*.root" >> $outDir/myHadd.txt
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
                    echo '' > TerminalList_$countLists.txt
                fi
            fi
        done
    fi
done

