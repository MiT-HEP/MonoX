"""
 Workspace configuration class (optional parameters in parentheses)
 <input>
  sourcename - Where to find the ROOT files containing histograms. Wildcards {region} and {process} can be used.
  histname - Format of histogram names to be found in the source files. Wildcards {region} and {process} can be used.
  (signalHistname) - Format of signal histogram names.
  (data) - Process name of the observed data. If not set, default value of 'data_obs' will be used.
  (binWidthNormalized) - boolean specifying whether the input histograms are already bin-width normalized.
 <output>
  outname - Workspace ROOT file name.
  (carddir) - When given, data card files are produced and saved in this directory.
  (cardname) - Name of the data card files. Wild card {signal} can be used as a placeholder for signal model name.
  (plotsOutname) - When given, a ROOT file with histograms visualizing the workspace content is created.
  (xtitle) - X axis title of the histograms.
  (xunit) - Unit of the X axis variable.
 <physics>
  regions - List of signal and control region names. Replaces the {region} wildcard in the input definitions.
  bkgProcesses - Full list of background process names. Not all processes have to appear in every region.
  signals - List of signal point names.
  (links) - List of links between samples. [(target process, target region), (source process, source region)].
  (staticBase) - List of base samples who are not allowed to change shape.
  (floatProcesses) - List of processes with floating normalization but does not participate in any links.
 <nuisance control>
  (ignoredNuisances) - For each (process, region), list the nuisances that can be found in the input files as histograms but should be ignored. {(process, region): [nuisance]}.
  (scaleNuisances) - List of nuisances that affect the normalization only. All of them must have corresponding histograms.
  (ratioCorrelations) - Nuisances are fully correlated between samples in a link by default. Use this to specify partial correlations. {((target sample), (source sample), nuisance): correlation}.
  (deshapedNuisances) - List of nuisances to be artificially bin-decorrelated. Systematic variations in this list will have nuisance a parameter for each bin.
  (flatParams) - List of nuisances that can vary without penalty.
"""

import sys

class WorkspaceConfig(object):
    def __init__(self, **kwd):
        def mandatory(key):
            try:
                setattr(self, key, kwd[key])
            except KeyError:
                print 'Parameter %s missing in workspace configuration' % key
                sys.exit(1)

        def optional(key, default = None):
            try:
                setattr(self, key, kwd[key])
            except KeyError:
                setattr(self, key, default)

        # input
        mandatory('sourcename')
        mandatory('histname')
        optional('signalHistname')
        optional('data', 'data_obs')
        optional('binWidthNormalized', False)

        # output
        mandatory('outname')
        optional('cardname')
        optional('plotsOutname')
        optional('xname', 'x')
        optional('xtitle')
        optional('xunit')

        # physics
        mandatory('regions')
        mandatory('bkgProcesses')
        mandatory('signals')
        optional('links', [])
        optional('staticBase', [])
        optional('floatProcesses', [])

        # nuisance control
        optional('ignoredNuisances', {})
        optional('scaleNuisances', [])
        optional('ratioCorrelations', {})
        optional('deshapedNuisances', [])
        optional('flatParams', [])

# Set this to a WorkspaceConfig instance
config = None
