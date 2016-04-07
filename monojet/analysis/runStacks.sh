#! /bin/bash

CompileCrombieTools PlotStack

./Stack.py &
./GJetsStack.py &
./StackNoBVeto.py &
./GJetsNoBVetoStack.py &

wait

echo "All done!"
