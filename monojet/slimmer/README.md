# Slimmer Tool

Located in `MonoX/monojet/slimmer` is a set of tools that can be used to generate very flat trees from Nero.

## Generating flat trees

### Configuring Trees

The variables that you want to include in a flat tree can be specified in `MonoJetTree.txt`.
The format of the configuration file is `<branchName>/<type>=<default>`.
`<branchName>` should be easy to understand.
Valid entries for `<type>` include `F`, `I`, or `O` for float, integer, and boolean, respectively.
You can also use `VF`, `VI`, or `VO` for (pointers of) vectors of these types.
After writing a tree configuration file with name `MonoJetTree.txt`, just run
```
./makeTree.sh
```
This makes a class that contains your tree.
You can call each branch of the tree via a public member with the same name of the `<branchName>` and fill it with function `Fill()` at the end of each event.
You can then write the tree to a file via `WriteToFile(*TFile,"<WhatYouWantToCallTree>")`.
If you do not set a value for a particular event, the branch will be filled with `<default>`.
See `NeroSlimmer.cc` for an example of how to write a flat tree writer using this class.

To actually run `NeroSlimmer.cc`, you need to run
```
./runSlimmer.py <NeroFileLocation> <OutputFileLocation>
```
This loads the `MonoJetTree` class as well as the `NeroTree` class, generated from a Nero file.
Simply running
```
./runSlimmer.py test
```
also runs over one Nero file.
Use this to debug.

### Making Trees

Assuming everything in this repository works, you can start turning Nero files into MonoJetTrees right away.
Configure `submit.sh` to submit batch jobs on LXPLUS.
`FilesPerJob` determines the maximum number of files on a single job.
Don't change the number of files per job unless you are starting a fresh run over Nero.
Otherwise, the script can't keep track of which files are finished.
`numProc` determines the number of processers you want to use if you really need to speed up your jobs.
`outDir` specifies your eventual output (with hadded files).
`lfsOut` is the directory files will be stored in the meanwhile.
Make sure this is empty before a fresh run, or corresponding jobs won't be submitted.
`eosDir` is the directory all of your Nero samples are in.
`skimmedDir` is the directory you might want your skimmed files eventually.
I'll get to that later.
Once these are set, run
```
./submit.sh
```
Once these jobs finish, run the same script again.
If any jobs failed, they will be resubmitted.
If all files are successfully completed, the files in `lfsOut` will be hadded into `outDir`.

### Slimming Trees

To slim trees, configure `FlatSlimmer.py`.
`inDir` is where the unslimmed root files are.
`outDir` is where they will be placed.
Make sure `outDir` exists.
Set a `GoodRunsFile` that will be used to apply a filter on data, and `cut` to make any additional cut on the slimmed trees.
Then just run
```
./FlatSlimmer.py <NumProc>
```
Your slimmed files will appear soon.

If you set `inDir` and `outDir` to match the `lfsOut` and `lfsOut/skimmed` from `submit.sh`, then you can do the following from `MonoX/monojet/MetRecoilStudy`
```
cat <lfsOut>/skimmed/myHadd.txt | xargs -n2 -P<NumProc> ./haddArgs.sh
```
I use `localSlimmer.sh` to do that, actually.
This will hadd skimmed files into the `skimmedDir` set in `submit.sh`.

If you just want to apply the good runs filter without slimming other trees, set `inDir`, `outDir`, and `GoodRunsFile` in `goodRunSlimmer.py` and run
```
./goodRunSlimmer.py <NumProc>
```

### NLO Corrections to GJets

In order to apply NLO corrections to your GJets files, set the directory where your samples are located in `runNLOGamma.sh`.
Make sure you have the `kfactor.root` file in your directory.
I'll try to keep a copy at `/afs/cern.ch/work/d/dabercro/public/Winter15/MonoX/monojet/MetRecoilStudy/kfactor.root`.
Or you can edit `nloGamma.cc` to just load this file directly.
Anyway
```
./runNLOGamma.sh
```
will also put an hadded sample `monojet_GJets.root` into your sample directory.
This file has `XSecWeight` and `nloFactor` branches in the friendly treey `nloTree`.
`XSecWeight` is just a relative weight for plotting all of GJets on the same histogram.

