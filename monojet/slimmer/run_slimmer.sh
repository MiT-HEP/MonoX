#! /bin/bash

inFiles=$1
fresh=$2

for fileName in `cat $inFiles`; do
    fileName="${fileName%.*}"
    echo $fileName
    if [ -f "monojet_$fileName.root" -o "$fresh" = "fresh" ]; then
        ./slimmer.py $fileName &
    fi
done

wait

echo "Finished with "$inFiles"!"