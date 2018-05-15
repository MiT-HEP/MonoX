#~/bin/bash

for point in $(ls ~/hadoop/monophoton/gengridUnmerged)
do
    mkdir ~/hadoop/monophoton/gengrid/${point} /local/ballen/gengrid/${point}
    hadd -f /local/ballen/gengrid/${point}/merged.root ~/hadoop/monophoton/gengridUnmerged/${point}/submit_*.root
    cp /local/ballen/gengrid/${point}/merged.root ~/hadoop/monophoton/gengrid/${point}/merged.root 
done

### clean up
# for point in GenAnalysis_MonoPhoton_V_Mx1_Mv1000-submit_ConfFile_cfg
# do
#    rm -r ~/hadoop/monophoton/gengridUnmerged/${point}
#    rm /local/ballen/gengrid/${point}/merged.root
# done