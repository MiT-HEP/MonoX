#include "MonoJetTree.h"

ClassImp(MonoJetTree)

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(const char *name)
{ 
  t = new TTree(name,name);

  t->Branch("runNum",&runNum,"runNum/I");
  t->Branch("lumiNum",&lumiNum,"lumiNum/I");
  t->Branch("eventNum",&eventNum,"eventNum/I");
  t->Branch("npv",&npv,"npv/I");
  t->Branch("mcWeight",&mcWeight,"mcWeight/F");
  t->Branch("npvWeight",&npvWeight,"npvWeight/F");
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
  t->Branch("photonPtRaw",&photonPtRaw,"photonPtRaw/F");
  t->Branch("photonEta",&photonEta,"photonEta/F");
  t->Branch("photonPhi",&photonPhi,"photonPhi/F");
  t->Branch("photonIsTight",&photonIsTight,"photonIsTight/I");
  t->Branch("n_tightpho",&n_tightpho,"n_tightpho/I");
  t->Branch("n_loosepho",&n_loosepho,"n_loosepho/I");
  t->Branch("met",&met,"met/F");
  t->Branch("metPhi",&metPhi,"metPhi/F");
  t->Branch("u_perp",&u_perp,"u_perp/F");
  t->Branch("u_para",&u_para,"u_para/F");
  t->Branch("n_bjetsLoose",&n_bjetsLoose,"n_bjetsLoose/I");
  t->Branch("n_bjetsMedium",&n_bjetsMedium,"n_bjetsMedium/I");
  t->Branch("n_bjetsTight",&n_bjetsTight,"n_bjetsTight/I");
  t->Branch("leadingjetPt",&leadingjetPt,"leadingjetPt/F");
  t->Branch("leadingjetEta",&leadingjetEta,"leadingjetEta/F");
  t->Branch("leadingjetPhi",&leadingjetPhi,"leadingjetPhi/F");
  t->Branch("leadingjetM",&leadingjetM,"leadingjetM/F");
  t->Branch("leadingjetisMonoJetId",&leadingjetisMonoJetId,"leadingjetisMonoJetId/I");
  t->Branch("n_jets",&n_jets,"n_jets/I");
  t->Branch("jet1Pt",&jet1Pt,"jet1Pt/F");
  t->Branch("jet1Eta",&jet1Eta,"jet1Eta/F");
  t->Branch("jet1Phi",&jet1Phi,"jet1Phi/F");
  t->Branch("jet1M",&jet1M,"jet1M/F");
  t->Branch("jet1BTag",&jet1BTag,"jet1BTag/F");
  t->Branch("jet1PuId",&jet1PuId,"jet1PuId/F");
  t->Branch("jet1isMonoJetId",&jet1isMonoJetId,"jet1isMonoJetId/I");
  t->Branch("jet1isLooseMonoJetId",&jet1isLooseMonoJetId,"jet1isLooseMonoJetId/I");
  t->Branch("jet1DPhiMet",&jet1DPhiMet,"jet1DPhiMet/F");
  t->Branch("jet1DPhiTrueMet",&jet1DPhiTrueMet,"jet1DPhiTrueMet/F");
  t->Branch("jet2Pt",&jet2Pt,"jet2Pt/F");
  t->Branch("jet2Eta",&jet2Eta,"jet2Eta/F");
  t->Branch("jet2Phi",&jet2Phi,"jet2Phi/F");
  t->Branch("jet2M",&jet2M,"jet2M/F");
  t->Branch("jet2BTag",&jet2BTag,"jet2BTag/F");
  t->Branch("jet2PuId",&jet2PuId,"jet2PuId/F");
  t->Branch("jet2isMonoJetId",&jet2isMonoJetId,"jet2isMonoJetId/I");
  t->Branch("jet2isLooseMonoJetId",&jet2isLooseMonoJetId,"jet2isLooseMonoJetId/I");
  t->Branch("jet2DPhiMet",&jet2DPhiMet,"jet2DPhiMet/F");
  t->Branch("jet2DPhiTrueMet",&jet2DPhiTrueMet,"jet2DPhiTrueMet/F");
  t->Branch("n_cleanedjets",&n_cleanedjets,"n_cleanedjets/I");
  t->Branch("dPhi_j1j2",&dPhi_j1j2,"dPhi_j1j2/F");
  t->Branch("minJetMetDPhi",&minJetMetDPhi,"minJetMetDPhi/F");
  t->Branch("minJetTrueMetDPhi",&minJetTrueMetDPhi,"minJetTrueMetDPhi/F");
  t->Branch("n_tau",&n_tau,"n_tau/I");
  t->Branch("boson_pt",&boson_pt,"boson_pt/F");
  t->Branch("boson_phi",&boson_phi,"boson_phi/F");
  t->Branch("genBos_pt",&genBos_pt,"genBos_pt/F");
  t->Branch("genBos_phi",&genBos_phi,"genBos_phi/F");
  t->Branch("genBos_PdgId",&genBos_PdgId,"genBos_PdgId/I");
  t->Branch("genMet",&genMet,"genMet/F");
  t->Branch("genMetPhi",&genMetPhi,"genMetPhi/F");
  t->Branch("kfactor",&kfactor,"kfactor/F");
  t->Branch("u_perpGen",&u_perpGen,"u_perpGen/F");
  t->Branch("u_paraGen",&u_paraGen,"u_paraGen/F");
  t->Branch("correctEvent",&correctEvent,"correctEvent/O");

  Reset();
}

//--------------------------------------------------------------------------------------------------
MonoJetTree::~MonoJetTree()
{
  delete t;
}

//--------------------------------------------------------------------------------------------------
void
MonoJetTree::Reset()
{
  runNum = 0;
  lumiNum = 0;
  eventNum = 0;
  npv = 0;
  mcWeight = 0;
  npvWeight = 1;
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
  photonPtRaw = -5;
  photonEta = -7;
  photonPhi = -5;
  photonIsTight = -1;
  n_tightpho = 0;
  n_loosepho = 0;
  met = -5;
  metPhi = -5;
  u_perp = 0;
  u_para = 0;
  n_bjetsLoose = 0;
  n_bjetsMedium = 0;
  n_bjetsTight = 0;
  leadingjetPt = -5;
  leadingjetEta = -7;
  leadingjetPhi = -5;
  leadingjetM = -5;
  leadingjetisMonoJetId = -1;
  n_jets = 0;
  jet1Pt = -5;
  jet1Eta = -7;
  jet1Phi = -5;
  jet1M = -5;
  jet1BTag = -1;
  jet1PuId = -2;
  jet1isMonoJetId = -1;
  jet1isLooseMonoJetId = -1;
  jet1DPhiMet = -1;
  jet1DPhiTrueMet = -1;
  jet2Pt = -5;
  jet2Eta = -7;
  jet2Phi = -5;
  jet2M = -5;
  jet2BTag = -1;
  jet2PuId = -2;
  jet2isMonoJetId = -1;
  jet2isLooseMonoJetId = -1;
  jet2DPhiMet = -1;
  jet2DPhiTrueMet = -1;
  n_cleanedjets = 0;
  dPhi_j1j2 = -1;
  minJetMetDPhi = 5;
  minJetTrueMetDPhi = 5;
  n_tau = 0;
  boson_pt = -5;
  boson_phi = -5;
  genBos_pt = -5;
  genBos_phi = -5;
  genBos_PdgId = 0;
  genMet = -5;
  genMetPhi = -5;
  kfactor = 1;
  u_perpGen = 0;
  u_paraGen = 0;
  correctEvent = 0;
}
