import ROOT

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.ProcessLine('int val;')
def getEnum(cls, name):
    ROOT.gROOT.ProcessLine('val = panda::' + cls + '::TriggerObject::' + name + ';')
    return ROOT.val

measurements = {
    ('photon', 'sel'): ('sel-16*-m', 'tpeg', 'probes.medium && !probes.pixelVeto && tp.mass > 60. && tp.mass < 120.'),
    ('photon', 'selBCD'): (['sel-16b-m', 'sel-16c-m', 'sel-16d-m'], 'tpeg', 'probes.medium && !probes.pixelVeto && tp.mass > 60. && tp.mass < 120. && runNumber < 276525'), # for photon75
    ('photon', 'dy'): (['dy-50*'], 'tpeg', 'probes.medium && !probes.pixelVeto && tp.mass > 60. && tp.mass < 120.'),
    ('electron', 'sel'): ('sel-16*-m', 'tp2e', 'probes.tight && tp.mass > 60. && tp.mass < 120.'),
    ('muon', 'smu'): ('smu-16*', 'tp2m', 'probes.tight && tp.mass > 60. && tp.mass < 120.'),
    ('vbf', 'selBCD'): (['sel-16b-m', 'sel-16c-m', 'sel-16d-m'], 'vbfe', 'electrons.triggerMatch[][%d] && dijet.size > 0 && runNumber < 276525' % getEnum('Electron', 'fEl75EBR9IsoPh')),
    ('vbf', 'dy'): (['dy-50*'], 'vbfe', 'electrons.triggerMatch[][%d] && dijet.size > 0' % getEnum('Electron', 'fEl75EBR9IsoPh'))
}

confs = {
    'photon': {
        'l1eg40': ('probes.triggerMatch[][%d]' % getEnum('Photon', 'fSEG34IorSEG40'), '', 'L1 seed', {
            'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', (50, 0., 100.)),
            'ptwide': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(10)]),
            'hOverE': ('H/E', 'probes.hOverE', 'probes.pt_ > 175.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', 'probes.pt_ * TMath::CosH(probes.eta_) * probes.hOverE', 'probes.pt_ > 175.', (25, 0., 5))
        }),
        'sph165abs': ('probes.triggerMatch[][%d]' % getEnum('Photon', 'fPh165HE10'), '', 'L1&HLT', {
            'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)] + [300. + 50. * x for x in range(10)]),
            'ptzoom': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
            'hOverE': ('H/E', 'probes.hOverE', 'probes.pt_ > 175.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', 'probes.pt_ * TMath::CosH(probes.eta_) * probes.hOverE', 'probes.pt_ > 175.', (25, 0., 5)),
            'run': ('Run', 'runNumber', 'probes.pt_ > 175.', (26, 271050., 284050.))
        }),
        'ph75r9iso': ('probes.triggerMatch[][%d]' % getEnum('Photon', 'fPh75EBR9Iso'), 'probes.isEB', 'Photon75Iso40R9', {
            'pt': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', 'probes.r9 > 0.9', (50, 0., 100.)),
            'ptwide': ('p_{T}^{#gamma} (GeV)', 'probes.pt_', 'probes.r9 > 0.9', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 25. * x for x in range(6)] + [350. + 100. * x for x in range(4)]),
            'r9': ('R^{9}', 'probes.r9', 'probes.pt_ > 80.', (30, 0.7, 1.))
        })
    },
    'electron': {
        'el27': ('probes.triggerMatch[][%d]' % getEnum('Electron', 'fEl27Tight'), '', 'HLT', {
            'ptzoom': ('p_{T}^{e} (GeV)', 'probes.pt_', '', (50, 0., 50.)),
            'ptwide': ('p_{T}^{e} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
            'hOverE': ('H/E', 'probes.hOverE', 'probes.pt_ > 200.', (25, 0., 0.05)),
            'hcalE': ('E^{HCAL} (GeV)', 'probes.pt_ * TMath::CosH(probes.eta_) * probes.hOverE', 'probes.pt_ > 200.', (25, 0., 5)),
            'run': ('Run', 'runNumber', 'probes.pt_ > 200.', (350, 271000., 274500.)),
            'pt': ('p_{T}^{e} (GeV)', 'probes.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)]),
            'eta': ('#eta^{e}', 'probes.eta_', 'probes.pt_ > 50.', (25, -2.5, 2.5))
        })
    },
    'muon': {
        'mu24ortrk24': ('probes.triggerMatch[][%d] || probes.triggerMatch[][%d]' % (getEnum('Muon', 'fIsoMu24'), getEnum('Muon', 'fIsoTkMu24')), '', 'HLT', {
            'ptzoom': ('p_{T}^{#mu} (GeV)', 'probes.pt_', '', (50, 0., 50.)),
            'ptwide': ('p_{T}^{#mu} (GeV)', 'probes.pt_', '', [30. + 2. * x for x in range(85)] + [200. + 10. * x for x in range(10)]),
            'run': ('Run', 'runNumber', 'probes.pt_ > 200.', (350, 271000., 274500.)),
            'pt': ('p_{T}^{#mu} (GeV)', 'probes.pt_', '', [0. + 5. * x for x in range(10)] + [50. + 10. * x for x in range(6)])
        })
    },
    'vbf': {
        'vbf': ('HLT_Photon75_R9Id90_HE10_Iso40_EBOnly_VBF', 'Sum$(electrons.triggerMatch[][%d]) != 0' % getEnum('Electron', 'fEl75EBR9IsoPh'), 'VBF filter', {
            'dEtajj': ('|#Delta#eta_{jj}|', 'Max$(TMath::Abs(dijet.dEtajj * (dijet.mjj > 800.)))', 'Sum$(dijet.mjj > 500) != 0', (50, 0., 5.)),
            'mjj': ('m_{jj} (GeV)', 'Max$(TMath::Abs(dijet.mjj * (TMath::Abs(dijet.dEtajj) > 3.2)))', 'Sum$(TMath::Abs(dijet.dEtajj) > 3.2) != 0', (50, 0., 1000.))
        })
    }
}

# TTree output for fitting
fitconfs = {}
fitconfs['photon'] = []
fitconfs['electron'] = [
    ('ptzoom', 'el27')
]
fitconfs['muon'] = []
fitconfs['vbf'] = []
