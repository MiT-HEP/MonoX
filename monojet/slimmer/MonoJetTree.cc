#include "MonoJetTree.h"

ClassImp(MonoJetTree)

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(TTree* tree) :
  fFile(0)
{
  t = tree;
  SetupTree();
}

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(const char* name) :
  fFile(0)
{
  t = new TTree(name,name);
  SetupTree();
}

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(const char* name, TString outFileName)
{
  fFile = new TFile(outFileName,"RECREATE");
  fFile->cd();
  t = new TTree(name,name);
  SetupTree();
}

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(const char* name, TFile* outFile)
{
  fFile = outFile;
  fFile->cd();
  t = new TTree(name,name);
  SetupTree();
}

//--------------------------------------------------------------------------------------------------
MonoJetTree::~MonoJetTree()
{
  delete t;
  delete fFile;
}

//--------------------------------------------------------------------------------------------------
void
MonoJetTree::Reset()
{
  runNum = 0;
  lumiNum = 0;
  eventNum = 0;
  npv = 0;
  rho = 0;
  mcWeight = 0;
  trueMet = -5;
  trueMetPhi = -5;
  triggerFired = 0;
  lep1Pt = -5;
  lep1Eta = -7;
  lep1Phi = -5;
  lep1PdgId = 0;
  lep1IsTight = -1;
  lep1IsMedium = -1;
  lep1DPhiTrueMet = 5;
  lep1RelIso = 10;
  lep2Pt = -5;
  lep2Eta = -7;
  lep2Phi = -5;
  lep2PdgId = 0;
  lep2IsTight = -1;
  lep2IsMedium = -1;
  lep2DPhiTrueMet = 5;
  lep2RelIso = 10;
  dilep_pt = -5;
  dilep_eta = -7;
  dilep_phi = -5;
  dilep_m = -5;
  mt = -5;
  n_tightlep = 0;
  n_mediumlep = 0;
  n_looselep = 0;
  leptonSF = 1;
  photonPt = -5;
  photonEta = -7;
  photonPhi = -5;
  photonIsMedium = -1;
  n_mediumpho = 0;
  n_loosepho = 0;
  met = -5;
  metPhi = -5;
  u_perp = 0;
  u_para = 0;
  n_bjetsLoose = 0;
  n_bjetsMedium = 0;
  n_bjetsTight = 0;
  leadingJet_outaccp = 0;
  leadingjetPt = -5;
  leadingjetEta = -7;
  leadingjetPhi = -5;
  leadingjetM = -5;
  n_jets = 0;
  jet1Pt = -5;
  jet1Eta = -7;
  jet1Phi = -5;
  jet1M = -5;
  jet1BTag = -1;
  jet1PuId = -2;
  jet1isMonoJetId = -1;
  jet1isMonoJetIdNew = -1;
  jet1isLooseMonoJetId = -1;
  jet1DPhiMet = -1;
  jet1DPhiTrueMet = -1;
  jet1QGL = -2;
  jet1Flavor = -1;
  jet2Pt = -5;
  jet2Eta = -7;
  jet2Phi = -5;
  jet2M = -5;
  jet2BTag = -1;
  jet2PuId = -2;
  jet2isMonoJetId = -1;
  jet2isMonoJetIdNew = -1;
  jet2isLooseMonoJetId = -1;
  jet2DPhiMet = -1;
  jet2DPhiTrueMet = -1;
  jet2QGL = -2;
  n_cleanedjets = 0;
  ht_cleanedjets = 0;
  dPhi_j1j2 = -1;
  minJetMetDPhi = 5;
  minJetMetDPhi_clean = 5;
  minJetTrueMetDPhi = 5;
  minJetMetDPhi_withendcap = 5;
  minJetTrueMetDPhi_withendcap = 5;
  n_tau = 0;
  boson_pt = -5;
  boson_phi = -5;
  genBos_pt = -5;
  genBos_eta = -5;
  genBos_phi = -5;
  genBos_mass = -5;
  genBos_PdgId = 0;
  genMet = -5;
  genMetPhi = -5;
  u_perpGen = 0;
  u_paraGen = 0;
  fatjet1Pt = -5;
  fatjet1Eta = -7;
  fatjet1Phi = -5;
  fatjet1Mass = -5;
  fatjet1TrimmedM = -5;
  fatjet1PrunedM = -5;
  fatjet1FilteredM = -5;
  fatjet1SoftDropM = -5;
  fatjet1tau2 = 0;
  fatjet1tau1 = 0;
  fatjet1tau21 = 1;
  fatjet1MonojetId = -1;
  fatjet1QGL = -2;
  fatjet1QVol = -1;
  fatjet1DRGenW = 5;
  fatjet1GenWPt = -5;
  fatjet1GenWMass = -5;
  fatjet1DRLooseB = 5;
  fatjet1DRMediumB = 5;
  fatjet1DRTightB = 5;
  fatjet1isLeading = -1;
  fatjet1DPhiMet = 5;
  fatjet1DPhiTrueMet = 5;
  genDM_pt = -5;
  genDM_eta = -5;
  genDM_phi = -5;
  genDM_mass = -5;
  genDM_PdgId = 0;
  genJet_pt = -5;
  genJet_eta = -5;
  genJet_phi = -5;
  genJet_mass = -5;
  genJetDRjet1 = 10;
  rawMet = -5;
  rawMetPhi = -5;
  genFatJet_pt = -5;
  genFatJet_eta = -5;
  genFatJet_phi = -5;
  genFatJet_mass = -5;
  genFatJetDRfatjet1 = 10;
}

//--------------------------------------------------------------------------------------------------
void
MonoJetTree::SetupTree()
{
  t->Branch("runNum",&runNum,"runNum/I");
  t->Branch("lumiNum",&lumiNum,"lumiNum/I");
  t->Branch("eventNum",&eventNum,"eventNum/l");
  t->Branch("npv",&npv,"npv/I");
  t->Branch("rho",&rho,"rho/F");
  t->Branch("mcWeight",&mcWeight,"mcWeight/F");
  t->Branch("trueMet",&trueMet,"trueMet/F");
  t->Branch("trueMetPhi",&trueMetPhi,"trueMetPhi/F");
  t->Branch("triggerFired",&triggerFired);
  t->Branch("lep1Pt",&lep1Pt,"lep1Pt/F");
  t->Branch("lep1Eta",&lep1Eta,"lep1Eta/F");
  t->Branch("lep1Phi",&lep1Phi,"lep1Phi/F");
  t->Branch("lep1PdgId",&lep1PdgId,"lep1PdgId/I");
  t->Branch("lep1IsTight",&lep1IsTight,"lep1IsTight/I");
  t->Branch("lep1IsMedium",&lep1IsMedium,"lep1IsMedium/I");
  t->Branch("lep1DPhiTrueMet",&lep1DPhiTrueMet,"lep1DPhiTrueMet/F");
  t->Branch("lep1RelIso",&lep1RelIso,"lep1RelIso/F");
  t->Branch("lep2Pt",&lep2Pt,"lep2Pt/F");
  t->Branch("lep2Eta",&lep2Eta,"lep2Eta/F");
  t->Branch("lep2Phi",&lep2Phi,"lep2Phi/F");
  t->Branch("lep2PdgId",&lep2PdgId,"lep2PdgId/I");
  t->Branch("lep2IsTight",&lep2IsTight,"lep2IsTight/I");
  t->Branch("lep2IsMedium",&lep2IsMedium,"lep2IsMedium/I");
  t->Branch("lep2DPhiTrueMet",&lep2DPhiTrueMet,"lep2DPhiTrueMet/F");
  t->Branch("lep2RelIso",&lep2RelIso,"lep2RelIso/F");
  t->Branch("dilep_pt",&dilep_pt,"dilep_pt/F");
  t->Branch("dilep_eta",&dilep_eta,"dilep_eta/F");
  t->Branch("dilep_phi",&dilep_phi,"dilep_phi/F");
  t->Branch("dilep_m",&dilep_m,"dilep_m/F");
  t->Branch("mt",&mt,"mt/F");
  t->Branch("n_tightlep",&n_tightlep,"n_tightlep/I");
  t->Branch("n_mediumlep",&n_mediumlep,"n_mediumlep/I");
  t->Branch("n_looselep",&n_looselep,"n_looselep/I");
  t->Branch("leptonSF",&leptonSF,"leptonSF/F");
  t->Branch("photonPt",&photonPt,"photonPt/F");
  t->Branch("photonEta",&photonEta,"photonEta/F");
  t->Branch("photonPhi",&photonPhi,"photonPhi/F");
  t->Branch("photonIsMedium",&photonIsMedium,"photonIsMedium/I");
  t->Branch("n_mediumpho",&n_mediumpho,"n_mediumpho/I");
  t->Branch("n_loosepho",&n_loosepho,"n_loosepho/I");
  t->Branch("met",&met,"met/F");
  t->Branch("metPhi",&metPhi,"metPhi/F");
  t->Branch("u_perp",&u_perp,"u_perp/F");
  t->Branch("u_para",&u_para,"u_para/F");
  t->Branch("n_bjetsLoose",&n_bjetsLoose,"n_bjetsLoose/I");
  t->Branch("n_bjetsMedium",&n_bjetsMedium,"n_bjetsMedium/I");
  t->Branch("n_bjetsTight",&n_bjetsTight,"n_bjetsTight/I");
  t->Branch("leadingJet_outaccp",&leadingJet_outaccp,"leadingJet_outaccp/I");
  t->Branch("leadingjetPt",&leadingjetPt,"leadingjetPt/F");
  t->Branch("leadingjetEta",&leadingjetEta,"leadingjetEta/F");
  t->Branch("leadingjetPhi",&leadingjetPhi,"leadingjetPhi/F");
  t->Branch("leadingjetM",&leadingjetM,"leadingjetM/F");
  t->Branch("n_jets",&n_jets,"n_jets/I");
  t->Branch("jet1Pt",&jet1Pt,"jet1Pt/F");
  t->Branch("jet1Eta",&jet1Eta,"jet1Eta/F");
  t->Branch("jet1Phi",&jet1Phi,"jet1Phi/F");
  t->Branch("jet1M",&jet1M,"jet1M/F");
  t->Branch("jet1BTag",&jet1BTag,"jet1BTag/F");
  t->Branch("jet1PuId",&jet1PuId,"jet1PuId/F");
  t->Branch("jet1isMonoJetId",&jet1isMonoJetId,"jet1isMonoJetId/I");
  t->Branch("jet1isMonoJetIdNew",&jet1isMonoJetIdNew,"jet1isMonoJetIdNew/I");
  t->Branch("jet1isLooseMonoJetId",&jet1isLooseMonoJetId,"jet1isLooseMonoJetId/I");
  t->Branch("jet1DPhiMet",&jet1DPhiMet,"jet1DPhiMet/F");
  t->Branch("jet1DPhiTrueMet",&jet1DPhiTrueMet,"jet1DPhiTrueMet/F");
  t->Branch("jet1QGL",&jet1QGL,"jet1QGL/F");
  t->Branch("jet1Flavor",&jet1Flavor,"jet1Flavor/I");
  t->Branch("jet2Pt",&jet2Pt,"jet2Pt/F");
  t->Branch("jet2Eta",&jet2Eta,"jet2Eta/F");
  t->Branch("jet2Phi",&jet2Phi,"jet2Phi/F");
  t->Branch("jet2M",&jet2M,"jet2M/F");
  t->Branch("jet2BTag",&jet2BTag,"jet2BTag/F");
  t->Branch("jet2PuId",&jet2PuId,"jet2PuId/F");
  t->Branch("jet2isMonoJetId",&jet2isMonoJetId,"jet2isMonoJetId/I");
  t->Branch("jet2isMonoJetIdNew",&jet2isMonoJetIdNew,"jet2isMonoJetIdNew/I");
  t->Branch("jet2isLooseMonoJetId",&jet2isLooseMonoJetId,"jet2isLooseMonoJetId/I");
  t->Branch("jet2DPhiMet",&jet2DPhiMet,"jet2DPhiMet/F");
  t->Branch("jet2DPhiTrueMet",&jet2DPhiTrueMet,"jet2DPhiTrueMet/F");
  t->Branch("jet2QGL",&jet2QGL,"jet2QGL/F");
  t->Branch("n_cleanedjets",&n_cleanedjets,"n_cleanedjets/I");
  t->Branch("ht_cleanedjets",&ht_cleanedjets,"ht_cleanedjets/F");
  t->Branch("dPhi_j1j2",&dPhi_j1j2,"dPhi_j1j2/F");
  t->Branch("minJetMetDPhi",&minJetMetDPhi,"minJetMetDPhi/F");
  t->Branch("minJetMetDPhi_clean",&minJetMetDPhi_clean,"minJetMetDPhi_clean/F");
  t->Branch("minJetTrueMetDPhi",&minJetTrueMetDPhi,"minJetTrueMetDPhi/F");
  t->Branch("minJetMetDPhi_withendcap",&minJetMetDPhi_withendcap,"minJetMetDPhi_withendcap/F");
  t->Branch("minJetTrueMetDPhi_withendcap",&minJetTrueMetDPhi_withendcap,"minJetTrueMetDPhi_withendcap/F");
  t->Branch("n_tau",&n_tau,"n_tau/I");
  t->Branch("boson_pt",&boson_pt,"boson_pt/F");
  t->Branch("boson_phi",&boson_phi,"boson_phi/F");
  t->Branch("genBos_pt",&genBos_pt,"genBos_pt/F");
  t->Branch("genBos_eta",&genBos_eta,"genBos_eta/F");
  t->Branch("genBos_phi",&genBos_phi,"genBos_phi/F");
  t->Branch("genBos_mass",&genBos_mass,"genBos_mass/F");
  t->Branch("genBos_PdgId",&genBos_PdgId,"genBos_PdgId/I");
  t->Branch("genMet",&genMet,"genMet/F");
  t->Branch("genMetPhi",&genMetPhi,"genMetPhi/F");
  t->Branch("u_perpGen",&u_perpGen,"u_perpGen/F");
  t->Branch("u_paraGen",&u_paraGen,"u_paraGen/F");
  t->Branch("fatjet1Pt",&fatjet1Pt,"fatjet1Pt/F");
  t->Branch("fatjet1Eta",&fatjet1Eta,"fatjet1Eta/F");
  t->Branch("fatjet1Phi",&fatjet1Phi,"fatjet1Phi/F");
  t->Branch("fatjet1Mass",&fatjet1Mass,"fatjet1Mass/F");
  t->Branch("fatjet1TrimmedM",&fatjet1TrimmedM,"fatjet1TrimmedM/F");
  t->Branch("fatjet1PrunedM",&fatjet1PrunedM,"fatjet1PrunedM/F");
  t->Branch("fatjet1FilteredM",&fatjet1FilteredM,"fatjet1FilteredM/F");
  t->Branch("fatjet1SoftDropM",&fatjet1SoftDropM,"fatjet1SoftDropM/F");
  t->Branch("fatjet1tau2",&fatjet1tau2,"fatjet1tau2/F");
  t->Branch("fatjet1tau1",&fatjet1tau1,"fatjet1tau1/F");
  t->Branch("fatjet1tau21",&fatjet1tau21,"fatjet1tau21/F");
  t->Branch("fatjet1MonojetId",&fatjet1MonojetId,"fatjet1MonojetId/I");
  t->Branch("fatjet1QGL",&fatjet1QGL,"fatjet1QGL/F");
  t->Branch("fatjet1QVol",&fatjet1QVol,"fatjet1QVol/F");
  t->Branch("fatjet1DRGenW",&fatjet1DRGenW,"fatjet1DRGenW/F");
  t->Branch("fatjet1GenWPt",&fatjet1GenWPt,"fatjet1GenWPt/F");
  t->Branch("fatjet1GenWMass",&fatjet1GenWMass,"fatjet1GenWMass/F");
  t->Branch("fatjet1DRLooseB",&fatjet1DRLooseB,"fatjet1DRLooseB/F");
  t->Branch("fatjet1DRMediumB",&fatjet1DRMediumB,"fatjet1DRMediumB/F");
  t->Branch("fatjet1DRTightB",&fatjet1DRTightB,"fatjet1DRTightB/F");
  t->Branch("fatjet1isLeading",&fatjet1isLeading,"fatjet1isLeading/I");
  t->Branch("fatjet1DPhiMet",&fatjet1DPhiMet,"fatjet1DPhiMet/F");
  t->Branch("fatjet1DPhiTrueMet",&fatjet1DPhiTrueMet,"fatjet1DPhiTrueMet/F");
  t->Branch("genDM_pt",&genDM_pt,"genDM_pt/F");
  t->Branch("genDM_eta",&genDM_eta,"genDM_eta/F");
  t->Branch("genDM_phi",&genDM_phi,"genDM_phi/F");
  t->Branch("genDM_mass",&genDM_mass,"genDM_mass/F");
  t->Branch("genDM_PdgId",&genDM_PdgId,"genDM_PdgId/I");
  t->Branch("genJet_pt",&genJet_pt,"genJet_pt/F");
  t->Branch("genJet_eta",&genJet_eta,"genJet_eta/F");
  t->Branch("genJet_phi",&genJet_phi,"genJet_phi/F");
  t->Branch("genJet_mass",&genJet_mass,"genJet_mass/F");
  t->Branch("genJetDRjet1",&genJetDRjet1,"genJetDRjet1/F");

  Reset();
}
