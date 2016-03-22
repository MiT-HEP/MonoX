#!/bin/bash

samples="dmafs-10-1 dmafs-10-10 dmafs-10-1000 dmafs-10-150 dmafs-10-50 dmafs-10-500 dmafs-100-1 dmafs-100-10 dmafs-1000-1 dmafs-1000-1000 dmafs-1000-150 dmafs-10000-1 dmafs-10000-10 dmafs-10000-1000 dmafs-10000-150 dmafs-10000-50 dmafs-10000-500 dmafs-15-10 dmafs-1995-1000 dmafs-20-1 dmafs-200-1 dmafs-200-150 dmafs-200-50 dmafs-2000-1 dmafs-2000-500 dmafs-295-150 dmafs-300-1 dmafs-300-50 dmafs-50-1 dmafs-50-10 dmafs-50-50 dmafs-500-1 dmafs-500-150 dmafs-500-500 dmafs-95-50 dmafs-995-500 dmvfs-10-1 dmvfs-10-10 dmvfs-10-1000 dmvfs-10-150 dmvfs-10-50 dmvfs-10-500 dmvfs-100-1 dmvfs-100-10 dmvfs-1000-1 dmvfs-1000-1000 dmvfs-1000-150 dmvfs-10000-1 dmvfs-10000-10 dmvfs-10000-1000 dmvfs-10000-50 dmvfs-10000-500 dmvfs-15-10 dmvfs-1995-1000 dmvfs-20-1 dmvfs-200-1 dmvfs-200-150 dmvfs-200-50 dmvfs-2000-1 dmvfs-2000-500 dmvfs-295-150 dmvfs-300-1 dmvfs-300-50 dmvfs-50-1 dmvfs-50-10 dmvfs-50-50 dmvfs-500-1 dmvfs-500-150 dmvfs-500-500 dmvfs-95-50 dmvfs-995-500"

for sample in $samples:
do
    python datasets.py --recalculate $sample --source-dir /scratch5/yiiyama/hist/simpletree13c/t2mit/filefi
done