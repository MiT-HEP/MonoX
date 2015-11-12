#! /bin/bash

folder=$1
     f=$2
    xs=$3

root -q -l -b xsecWeights.cc+\(\"$folder\",\"$f\",$xs\)
