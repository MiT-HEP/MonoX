#! /bin/bash

folder=/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV7/

root -q -l -b xsecWeights.cc+\(\"$folder\"\)                      # This is to just make sure the macro is compiled

cat xsecArgs.txt | xargs -n2 -P6 ./xsecRunner.sh $folder

hadd $folder/monojet_GJets.root $folder/monojet_GJets_HT*.root
hadd $folder/monojet_WJetsToLNu.root $folder/monojet_WJetsToLNu_HT*.root
hadd $folder/monojet_MET.root $folder/monojet_MET+Run201*.root
hadd $folder/monojet_SingleMuon.root $folder/monojet_SingleMuon+Run201*.root
hadd $folder/monojet_SingleElectron.root $folder/monojet_SingleElectron+Run201*.root
hadd $folder/monojet_SinglePhoton.root $folder/monojet_SinglePhoton+Run201*.root
