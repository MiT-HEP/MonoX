#! /bin/bash

dir=/afs/cern.ch/work/d/dabercro/eos/cms/store/caf/user/yiiyama/nerov5/SingleElectron+Run2015D-PromptReco-v3+AOD
out=lumiz.txt
nCores=6

if [ ! -d $dir ]
then
    echo "Please configure paraJson and doJson by hand."
    echo "Sorry, I don't like typing in commands at the command line."
fi

ArgList=ArgList.txt

> $ArgList
count=0

tempBase='tempJson_'
for argFile in `ls $dir`
do
    echo "$argFile $tempBase$count.txt" >> $ArgList
    count=$((count+1))
done

cat $ArgList | xargs -n2 -P$nCores `dirname $0`/doJson.sh $dir
