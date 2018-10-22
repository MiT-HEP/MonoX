import main.skimutils as su
import selectors as s

makeSel = su.MakeSelectors(s)

data_sph = ['tpeg', 'tpmg']
data_smu = ['zmmJets', 'zmumu', 'tpmmg', 'tpmgLowPt', 'tp2m']
data_sel = ['zeeJets', 'tpegLowPt', 'tp2e']

mc_lep = ['tpeg', 'tpmg', 'tpegLowPt', 'tpmgLowPt']
mc_dilep = ['zmumu', 'zmmJets', 'zeeJets', 'tpmmg', 'tpeg', 'tpmg', 'tpegLowPt', 'tpmgLowPt', 'tp2e', 'tp2m']

skimconfig = {
    # Data
    'sph-17*': makeSel(data_sph),
    'smu-17*': makeSel(data_smu),
    'sel-17*': makeSel(data_sel),
    # MC
    'dy-50': makeSel(mc_dilep, s.addGenPhotonVeto),
    'dy-50@': makeSel(mc_dilep, s.addGenPhotonVeto, su.htTruncator(maximum = 100.)),
    'dy-50-*': makeSel(mc_dilep, s.addGenPhotonVeto),
    'wlnu{,n}-*': makeSel(mc_lep),
    'tt': makeSel(mc_dilep)
}
