#! /bin/bash

export dir=$1
export jsonMask=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt

output=lumiz.txt
nCores=6

if [ "$CMSSW_BASE" = "" ]                             # Check for mergeJSON.py
then
    echo "No CMSSW_BASE defined. Need to cmsrel somewhere to use this tool."
    exit 1
fi

ArgList=ArgList.txt

> $ArgList
count=0

tempBase='tempJson_'
for argFile in `ls $dir`
do
    echo "$argFile $tempBase$count.txt" >> $ArgList   # Dump stuff to pass to wrapper later
    count=$((count+1))
done

cat $ArgList | xargs -n2 -P$nCores `dirname $0`/wrapperMakeJson.sh

# Merge Stuff here
mergeJSON.py $tempBase*.txt --output=$output

# Clean
rm $ArgList $tempBase*.txt
