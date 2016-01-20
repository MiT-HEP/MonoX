#! /bin/bash

 dir=$1
file=$2
 out=$3

`dirname $0`/makeJson.py $dir/$file --mask /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt -o $out
