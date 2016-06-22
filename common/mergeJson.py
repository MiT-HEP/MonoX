import sys
import os
import json
import collections

directory = sys.argv[1]

allLumis = collections.defaultdict(list)

for fname in os.listdir(directory):
    with open(directory + '/' + fname) as f:
        j = json.loads(f.read())
        for run, intervals in j.items():
            run = int(run)
            for interval in intervals:
                for lumi in range(interval[0], interval[1] + 1):
                    allLumis[run].append(lumi)

runBlocks = []

for run in sorted(allLumis.keys()):
    lumis = allLumis[run]

    intervals = []

    begin = 0
    end = -1
    for lumi in sorted(lumis):
        if lumi != end + 1:
            if begin != 0:
                intervals.append((begin, end))

            begin = lumi

        end = lumi

    intervals.append((begin, end))

    runBlock = '  "%d": [\n' % run
    runBlock += ',\n'.join(['    [%d, %d]' % interval for interval in intervals])
    runBlock += '\n  ]'

    runBlocks.append(runBlock)

with open('merged.txt', 'w') as output:
    output.write('{\n')
    output.write(',\n'.join(runBlocks))
    output.write('\n}\n')
