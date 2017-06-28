import os
import config

def getSkimPath(sample, skim, primary = config.skimDir, alternative = config.localSkimDir):
    sourceName = os.path.join(primary, sample + '_' + skim + '.root')
    if not alternative:
        return sourceName

    altName = os.path.join(alternative, sample + '_' + skim + '.root')
    if os.path.exists(altName) and os.stat(altName).st_mtime > os.stat(sourceName).st_mtime:
        sourceName = altName

    return sourceName

