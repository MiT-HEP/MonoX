#! /bin/bash

fresh=$1

for inFile in `ls *.txt`; do
    if [ "$fresh" = "fresh" ]; then
        if [ ! -f $inFile.first ]; then
            touch $inFile.first
        else
            continue
        fi
    fi
    ./run_slimmer.sh $inFile $fresh
    wait
done
