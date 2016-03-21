export CrombieFilesPerJob=10
export CrombieNBatchProcs=1
export CrombieQueue=1nh

export CrombieNLocalProcs=5

export CrombieFileBase=monojet
#export CrombieEosDir=/store/user/dabercro/Nero/74X_MonojetSignalProduction
export CrombieEosDir=/store/user/dabercro/Nero/v1.2
#export CrombieEosDir=/store/user/zdemirag/V0005
export CrombieRegDir=/afs/cern.ch/work/d/dabercro/eos/cms$CrombieEosDir
export CrombieTempDir=/afs/cern.ch/work/d/dabercro/public/Winter15/TempOut_160320
export CrombieFullDir=/afs/cern.ch/work/d/dabercro/public/Winter15/FullOut_160320
export CrombieSkimDir=/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160320
export CrombieDirList=SubDirList.txt
#export CrombieDirList=GluGlu.txt

export CrombieSlimmerScript=runSlimmer.py
export CrombieJobScriptList=CrombieScriptList.txt
export CrombieCheckerScript=$CROMBIEPATH/scripts/CrombieTreeFinder.py

export CrombieGoodRuns=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt
