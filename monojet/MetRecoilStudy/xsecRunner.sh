#! /bin/bash

 f=$1
xs=$2

root -q -l -b xsecWeights.cc+\(\"$f\",$xs\)
