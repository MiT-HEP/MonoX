import os
import logging

import config

logger = logging.getLogger(__name__)

import ROOT

## Selector-dependent configurations

from configs.common.selconf import selconf

selconf['emTrigger'] = ''

## Common modifiers

import configs.common.selectors_gen as sg

## Specific modifier

def setSampleId(sample, selector):
    """Set the sample ID on TagAndProbeSelector."""

    if sample.data:
        selector.setSampleId(0)
    elif sample.name.startswith('dy'):
        selector.setSampleId(1)
    elif sample.name.startswith('tt'):
        selector.setSampleId(2)
    elif sample.name.startswith('wg'):
        selector.setSampleId(3)
    elif sample.name.startswith('gg'):
        selector.setSampleId(4)
    else:
        selector.setSampleId(99)

##################
# BASE SELECTORS #
##################

def tightloose(sample, rname):
    """
    One tight lepton, one loose lepton
    """
    selector = ROOT.EventSelector(rname)

    selector.addOperator(ROOT.MetFilters())

    leptons = ROOT.LeptonSelection()
    leptons.setN(1, 1)
    leptons.setStrictEl(False)
    leptons.setStrictMu(False)
    leptons.setRequireTight(False)
    leptons.setRequireMedium(False)
    leptons.setRequireHWWTight(True)
    leptons.setOutMuonType(ROOT.LeptonSelection.kMuTrigger17Safe)
    leptons.setOutElectronType(ROOT.LeptonSelection.kElTrigger17Safe)
    selector.addOperator(leptons)

    jets = ROOT.JetCleaning()
    jets.setCleanAgainst(ROOT.cElectrons, True)
    jets.setCleanAgainst(ROOT.cTaus, True)
    selector.addOperator(jets)

    selector.addOperator(ROOT.CopyMet())

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))

        sg.addPUWeight(sample, selector)
        sg.addPDFVariation(sample, selector)

    return selector
