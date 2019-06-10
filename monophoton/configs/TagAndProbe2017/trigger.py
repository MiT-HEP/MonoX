measurements = {
    ('photon', 'sel'): ('sel-17*', 'tpegLowPt', '(tags.hltmatchele27 || tags.hltmatchele32 || tags.hltmatchele35) && probes.medium && !probes.pixelVeto && tp.mass > 60. && tp.mass < 120. && TMath::Abs(TVector2::Phi_mpi_pi(probes.phi_ - tags.phi_)) > 0.6', 'probes'),
    ('photon', 'smu'): ('smu-17*', 'tpmgLowPt', 'tags.hltmatchmu27 && probes.medium', 'probes'),
    ('photon', 'dy'): (['dy-50'], 'tpegLowPt', '(tags.hltmatchele27 || tags.hltmatchele32 || tags.hltmatchele35) && probes.medium && !probes.pixelVeto && tp.mass > 60. && tp.mass < 120. && TMath::Abs(TVector2::Phi_mpi_pi(probes.phi_ - tags.phi_)) > 0.6', 'probes'),
#    ('photon', 'ph75'): (['sph-17b', 'sph-17c', 'sph-17d'], 'ph75', 'photons.medium && HLT_Photon50 && runNumber < 276525', 'photons'),
#    ('photon', 'ph75h'): (['sph-17b', 'sph-17c', 'sph-17d'], 'ph75', 'photons.medium && HLT_Photon75 && runNumber < 276525', 'photons'),
    ('photon', 'mcph75'): (['gj04-*'], 'ph75', 'photons.medium && HLT_Photon50', 'photons'),
    ('electron', 'sel'): ('sel-17*', 'tp2e', 'probes.tight && tp.mass > 60. && tp.mass < 120.', 'probes'),
    ('muon', 'smu'): ('smu-17*', 'tp2m', 'probes.tight && tp.mass > 60. && tp.mass < 120.', 'probes'),
#    ('vbf', 'ph75h'): (['sph-17b', 'sph-17c', 'sph-17d'], 'ph75', 'photons.triggerMatch[][%d] && dijet.size > 0 && runNumber < 276525' % getEnum('Photon', 'fPh75EBR9Iso'), ''),
#    ('vbf', 'dy'): (['dy-50@*', 'dy-50-*'], 'vbfe', 'electrons.triggerMatch[][%d] && dijet.size > 0' % getEnum('Electron', 'fEl75EBR9IsoPh'), ''),
#    ('vbf', 'mcph75h'): (['gj04-*'], 'ph75', 'photons.triggerMatch[][%d] && dijet.size > 0' % getEnum('Photon', 'fPh75EBR9Iso'), ''),
#    ('vbf', 'wlnu'): (['wlnu-*'], 'vbfe', 'electrons.triggerMatch[][%d] && dijet.size > 0' % getEnum('Electron', 'fEl75EBR9IsoPh'), '')
    ('electron', 'mc'): (['dy-50', 'tt2l'], 'tpme', 'tags.hltmatchmu27 && TMath::Abs(probes.eta_) < 2.5 && probes.mvaIsoWP90 && probes.conversionVeto && ((TMath::Abs(probes.eta_) < 1.479 && TMath::Abs(probes.dxy) < 0.05 && TMath::Abs(probes.dz) < 0.1) || (TMath::Abs(probes.eta_) > 1.479 && TMath::Abs(probes.dxy) < 0.1 && TMath::Abs(probes.dz) < 0.2))', 'probes')
}

for era in ['b', 'c', 'd', 'e', 'f']:
    measurements[('muon', 'muoneg' + era)] = (['sel-17' + era], 'tpem', 'tags.hltmatchele35 && probes.tight && TMath::Abs(probes.eta_) < 2.4 && TMath::Abs(probes.dz) < 0.1 && (probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ < 0.15 && ((probes.pt_ <= 20. && TMath::Abs(probes.dxy) < 0.01) || (probes.pt_ > 20. && TMath::Abs(probes.dxy) < 0.02))', 'probes')
    measurements[('muon', 'loosemuoneg' + era)] = (['sel-17' + era], 'tpem', 'tags.hltmatchele35 && probes.global && probes.pf && probes.nMatched >= 2 && TMath::Abs(probes.dxy) < 0.2 && TMath::Abs(probes.dz) < 0.5 && TMath::Abs(probes.eta_) < 2.4 && (probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ < 0.4', 'probes')
    measurements[('muon', 'superloosemuoneg' + era)] = (['sel-17' + era], 'tpem', 'tags.hltmatchele35 && probes.global && probes.pf && probes.nMatched >= 1 && TMath::Abs(probes.dxy) < 0.2 && TMath::Abs(probes.dz) < 0.5 && TMath::Abs(probes.eta_) < 2.4 && (probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ < 0.4', 'probes')

    measurements[('electron', 'muoneg' + era)] = (['smu-17' + era], 'tpme', 'tags.hltmatchmu27 && TMath::Abs(probes.eta_) < 2.5 && probes.mvaIsoWP90 && probes.conversionVeto && ((TMath::Abs(probes.eta_) < 1.479 && TMath::Abs(probes.dxy) < 0.05 && TMath::Abs(probes.dz) < 0.1) || (TMath::Abs(probes.eta_) > 1.479 && TMath::Abs(probes.dxy) < 0.1 && TMath::Abs(probes.dz) < 0.2))', 'probes')
    measurements[('electron', 'loosemuoneg' + era)] = (['smu-17' + era], 'tpme', 'tags.hltmatchmu27 && TMath::Abs(probes.eta_) < 2.5 && probes.veto && ((TMath::Abs(probes.eta_) < 1.479 && TMath::Abs(probes.dxy) < 0.05 && TMath::Abs(probes.dz) < 0.1) || (TMath::Abs(probes.eta_) > 1.479 && TMath::Abs(probes.dxy) < 0.1 && TMath::Abs(probes.dz) < 0.2))', 'probes')
    measurements[('electron', 'superloosemuoneg' + era)] = (['smu-17' + era], 'tpme', 'tags.hltmatchmu27 && TMath::Abs(probes.eta_) < 2.5 && probes.veto', 'probes')

    measurements[('electron', 'smu' + era)] = (['smu-17' + era], 'tpme', 'tags.hltmatchmu27 && TMath::Abs(probes.eta_) < 2.5 && probes.mvaIsoWP90 && probes.conversionVeto && ((TMath::Abs(probes.eta_) < 1.479 && TMath::Abs(probes.dxy) < 0.05 && TMath::Abs(probes.dz) < 0.1) || (TMath::Abs(probes.eta_) > 1.479 && TMath::Abs(probes.dxy) < 0.1 && TMath::Abs(probes.dz) < 0.2))', 'probes')

confs = {
    'photon': {
        'l1eg': ('{col}.hltmatchphoton200L1Seed', '', 'L1 seed', {
            'pt': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '', (50, 0., 100.)),
            'ptwide': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300., 350., 400.]),
            'hOverE': ('H/E', '{col}.hOverE', '{col}.pt_ > 70.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', '{col}.pt_ * TMath::CosH({col}.eta_) * {col}.hOverE', '{col}.pt_ > 70.', (25, 0., 5)),
            'run': ('Run', 'runNumber', '{col}.pt_ > 70.', (26, 294927, 306462))
        }),
        'sph200abs': ('{col}.hltmatchphoton200', '', 'L1&HLT', {
            'pt': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(10)]),
            'ptzoom': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '', [30. + 5. * x for x in range(54)] + [300. + 10. * x for x in range(6)]),
            'hOverE': ('H/E', '{col}.hOverE', '{col}.pt_ > 220.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', '{col}.pt_ * TMath::CosH({col}.eta_) * {col}.hOverE', '{col}.pt_ > 220.', (25, 0., 5)),
            'run': ('Run', 'runNumber', '{col}.pt_ > 220.', (26, 294927, 306462))
        }),
        'ph75r9iso': ('{col}.hltmatchphoton75', '{col}.isEB', 'Photon75Iso40R9', {
            'pt': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '{col}.r9 > 0.9', (50, 0., 100.)),
            'ptwide': ('p_{T}^{#gamma} (GeV)', '{col}.pt_', '{col}.r9 > 0.9', [30. + 10. * x for x in range(7)] + [100., 120., 140., 160., 200., 300., 400., 600.]),
            'r9': ('R^{9}', '{col}.r9', '{col}.pt_ > 80.', (30, 0.7, 1.)),
            'run': ('Run', 'runNumber', '{col}.pt_ > 80.', (26, 294927, 306462))
        })
    },
    'electron': {
#        'el27': ('{col}.triggerMatch[][%d]' % getEnum('Electron', 'fEl27Tight'), '', 'HLT', {
#            'ptzoom': ('p_{T}^{e} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
#            'ptwide': ('p_{T}^{e} (GeV)', '{col}.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
#            'hOverE': ('H/E', '{col}.hOverE', '{col}.pt_ > 200.', (25, 0., 0.05)),
#            'hcalE': ('E^{HCAL} (GeV)', '{col}.pt_ * TMath::CosH({col}.eta_) * {col}.hOverE', '{col}.pt_ > 200.', (25, 0., 5)),
#            'run': ('Run', 'runNumber', '{col}.pt_ > 200.', (350, 271000., 274500.)),
#            'pt': ('p_{T}^{e} (GeV)', '{col}.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)]),
#            'eta': ('#eta^{e}', '{col}.eta_', '{col}.pt_ > 50.', (25, -2.5, 2.5))
#        }),
        'el35': ('{col}.hltmatchele35', '', 'Ele35 L1&HLT', {
            'ptzoom': ('p_{T}^{e} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'ptwide': ('p_{T}^{e} (GeV)', '{col}.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
            'hOverE': ('H/E', '{col}.hOverE', '{col}.pt_ > 200.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', '{col}.pt_ * TMath::CosH({col}.eta_) * {col}.hOverE', '{col}.pt_ > 200.', (25, 0., 5)),
            'pt': ('p_{T}^{e} (GeV)', '{col}.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)]),
            'eta': ('#eta^{e}', '{col}.eta_', '{col}.pt_ > 50.', (25, -2.5, 2.5)),
            'pteta': (('p_{T}^{e} (GeV)', '#eta^{e}'), ('{col}.pt_', '{col}.eta_'), '', ([30. + 2. * x for x in range(10)] + [50. + 4. * x for x in range(16)], (10, -2.5, 2.5)))
        }),
        'mu12ele23L1Seed': ('{col}.hltmatchmu12ele23L1Seed', '', 'Ele23Leg L1', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 35.', (48, -2.4, 2.4))
        }),
        'mu12ele23HLT': ('{col}.hltmatchmu12ele23', '{col}.hltmatchmu12ele23L1Seed', 'Ele23Leg HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 25.', (48, -2.4, 2.4))
        }),
        'mu12ele23': ('{col}.hltmatchmu12ele23', '', 'Ele23Leg L1&HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 35.', (48, -2.4, 2.4)),
            'pteta': (('p_{T}^{e} (GeV)', '#eta^{e}'), ('{col}.pt_', '{col}.eta_'), '', ([20. + x for x in range(20)] + [40. + 2. * x for x in range(11)], (10, -2.5, 2.5)))
        }),
        'mu23ele12L1Seed': ('{col}.hltmatchmu23ele12L1Seed', '', 'Ele12Leg L1', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 11.', (48, -2.4, 2.4))
        }),
        'mu23ele12HLT': ('{col}.hltmatchmu23ele12', '{col}.hltmatchmu23ele12L1Seed', 'Ele12Leg HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 15.', (48, -2.4, 2.4))
        }),
        'mu23ele12': ('{col}.hltmatchmu23ele12', '', 'Ele12Leg L1&HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 15.', (48, -2.4, 2.4)),
            'pteta': (('p_{T}^{e} (GeV)', '#eta^{e}'), ('{col}.pt_', '{col}.eta_'), '', ([10. + x for x in range(20)] + [30. + 2. * x for x in range(11)], (10, -2.5, 2.5)))
        })
    },
    'muon': {
#        'mu24ortrk24': ('{col}.triggerMatch[][%d] || {col}.triggerMatch[][%d]' % (getEnum('Muon', 'fIsoMu24'), getEnum('Muon', 'fIsoTkMu24')), '', 'HLT', {
#            'ptzoom': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
#            'ptwide': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
#            'run': ('Run', 'runNumber', '{col}.pt_ > 200.', (350, 271000., 274500.)),
#            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)])
#        })
        'mu12ele23L1Seed': ('{col}.hltmatchmu12ele23L1Seed', '', 'Mu12Leg L1', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 11.', (48, -2.4, 2.4))
        }),
        'mu12ele23HLT': ('{col}.hltmatchmu12ele23', '{col}.hltmatchmu12ele23L1Seed', 'Mu12Leg HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 15.', (48, -2.4, 2.4))
        }),
        'mu12ele23': ('{col}.hltmatchmu12ele23', '', 'Mu12Leg L1&HLT', {
            'pt': ('p_{T}^{#mu} (GeV)', '{col}.pt_', '', (50, 0., 50.)),
            'eta': ('#eta^{#mu}', '{col}.eta_', '{col}.pt_ > 15.', (48, -2.4, 2.4))
        })
    },
    'vbf': {
        'vbf': ('HLT_Photon75_R9Id90_HE10_Iso40_EBOnly_VBF', '', 'VBF filter', {
            'dEtajj': ('|#Delta#eta_{jj}|', 'Max$(TMath::Abs(dijet.dEtajj * (dijet.mjj > 800.)))', 'Sum$(dijet.mjj > 500) != 0', (50, 0., 5.)),
            'mjj': ('m_{jj} (GeV)', 'Max$(TMath::Abs(dijet.mjj * (TMath::Abs(dijet.dEtajj) > 3.2)))', 'Sum$(TMath::Abs(dijet.dEtajj) > 3.2) != 0', (50, 0., 1000.))
        })
    }
}

# TTree output for fitting
fitconfs = {}
#fitconfs['photon'] = []
#fitconfs['electron'] = [
#    ('ptzoom', 'el27')
#]
#fitconfs['muon'] = []
#fitconfs['vbf'] = []
