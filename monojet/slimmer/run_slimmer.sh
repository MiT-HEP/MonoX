#! /bin/bash

inFiles=$1
fresh=$2

if [ ! -f $inFiles.running ]; then

    touch $inFiles.running

    for fileName in `cat $inFiles`; do
        fileName="${fileName%.*}"
        echo $fileName
        if [ -f "monojet_$fileName.root" -o "$fresh" = "fresh" ]; then
            if [ "$fresh" = "taketurns" ]; then
                ./slimmer.py $fileName
            else
                ./slimmer.py $fileName &
            fi
        fi
    done

    wait

    rm $inFiles.running
    echo "Finished with "$inFiles"!"

else

    echo "Already running on "$inFiles"..."

fi