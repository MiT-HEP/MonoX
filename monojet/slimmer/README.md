To download the ROOT files needed in the `files` folder, just do:
```
cd files
cat downloadurls.txt | xargs wget
```

## Installing the slimmer

LXBATCH and terminal slimming tools have been made more generic and moved to 
`github.com/dabercro/CrombieTools.git` because I forsee using these a lot and
don't want to rewrite them for another analysis.
To install the slimming submission scripts, go anywhere you like and do the following:
```
git clone https://github.com/dabercro/CrombieTools.git
cd CrombieTools
./install.sh
```
The install script will add `CrombieTools/bin` to your `$PATH`,
`CrombieTools/python` to your `$PYTHONPATH` and a generic
`$CROMBIEPATH` variable used by the scripts to find the package.
If you do not have a `~/.bashrc` or `~/.bash_profile` file, this will fail.
Alternatively, you can add these variables by hand.

Now you can call `CrombieSubmitLxbatch` or `CrombieTerminalSlimming` commands from anywhere
where a `CrombieSlimmingConfig.sh` file exists.
(If you think the names are goofy, you can rename the scripts in your `CrombieTools/bin` directory.)
Now `CrombieSlimmingConfig.sh` gives all the parameters you need to submit jobs.
`CrombieDirList` is probably the most confusing variable that you will be changing a lot.
It lists the sub-directories or dataset names that you will be running over in the
`CrombieEosDir` or `CrombieRegDir` location.
If you leave `CrombieDirList` blank (by commenting out the initialization for example),
the the submission will run over all subdirectories.
