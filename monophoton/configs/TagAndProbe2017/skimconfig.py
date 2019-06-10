import main.skimutils as su
import configs.common.selectors_gen as sg
import selectors

makeSel = su.MakeSelectors(selectors)

data_sph = ['tpeg', 'tpmg']
data_smu = ['zmmJets', 'zmumu', 'tpmmg', 'tpmgLowPt', 'tp2m', 'tpme']
data_sel = ['zeeJets', 'tpegLowPt', 'tp2e', 'tpem']

mc_lep = ['tpeg', 'tpmg', 'tpegLowPt', 'tpmgLowPt']
mc_dilep = ['zmumu', 'zmmJets', 'zeeJets', 'tpmmg', 'tpeg', 'tpmg', 'tpegLowPt', 'tpmgLowPt', 'tp2e', 'tp2m', 'tpem', 'tpme']

skimconfig = {
    # Data
    'sph-17*': makeSel(data_sph),
    'smu-17*': makeSel(data_smu),
    'sel-17*': makeSel(data_sel),
    # MC
    'dy-50': makeSel(mc_dilep, sg.addGenPhotonVeto),
    'dy-50@': makeSel(mc_dilep, sg.addGenPhotonVeto, sg.htTruncator(maximum = 100.)),
    'dy-50-*': makeSel(mc_dilep, sg.addGenPhotonVeto),
    'wlnu{,n}-*': makeSel(mc_lep),
    'tt': makeSel(mc_dilep),
    'tt2l': makeSel(mc_dilep),
#    'ww': makeSel(mc_dilep),
#    'wz': makeSel(mc_dilep),
#    'zz': makeSel(mc_dilep)
}
