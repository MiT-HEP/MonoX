#! /bin/bash

file=$1
 out=$2

if [ "${file##*_}" != "pilot.root" -a "${file##*.}" = "root" ]
then
    echo "Using $file to make $out"
    `dirname $0`/makeJson.py $dir/$file --mask $jsonMask -o $out
fi
