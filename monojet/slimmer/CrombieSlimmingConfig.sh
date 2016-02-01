export CrombieFilesPerJob=10
export CrombieNumberProcs=1
export CrombieQueue=8nh

export CrombieNLocalProcs=5

export CrombieFileBase=monojet
#export CrombieEosDir=/store/caf/user/yiiyama/nerov5
#export CrombieEosDir=/store/user/zdemirag/V0004
export CrombieEosDir=/store/user/amarini/Nero/v1.3.1
export CrombieRegDir=/afs/cern.ch/work/d/dabercro/eos/cms$CrombieEosDir
export CrombieTempDir=/afs/cern.ch/work/d/dabercro/public/Winter15/TempMiniAOD
export CrombieFullDir=/afs/cern.ch/work/d/dabercro/public/Winter15/MiniAODOut
export CrombieSkimDir=/afs/cern.ch/work/d/dabercro/public/Winter15/MiniAODSkimmed
#export CrombieDirList=TTbarSync.txt
export CrombieDirList=TestMET.txt

export CrombieSlimmerScript=runSlimmer.py
export CrombieJobScriptList=CrombieScriptList.txt
export CrombieCheckerScript=$CROMBIEPATH/scripts/CrombieTreeFinder.py

export CrombieGoodRuns=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt
