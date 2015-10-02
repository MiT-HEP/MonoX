#include "MonoJetTree.h"

ClassImp(MonoJetTree)

//--------------------------------------------------------------------------------------------------
MonoJetTree::MonoJetTree(const char *name)
{ 
  t = new TTree(name,name);

  t->Branch("runNum",&runNum,"runNum/I");
  t->Branch("lumiNum",&lumiNum,"lumiNum/I");
  t->Branch("eventNum",&eventNum,"eventNum/I");
  t->Branch("jet1Pt",&jet1Pt,"jet1Pt/F");
  t->Branch("jet1Eta",&jet1Eta,"jet1Eta/F");
  t->Branch("jet1Phi",&jet1Phi,"jet1Phi/F");
  t->Branch("jet1dRmet",&jet1dRmet,"jet1dRmet/F");
  t->Branch("n_jets",&n_jets,"n_jets/I");
  t->Branch("lep1Pt",&lep1Pt,"lep1Pt/F");
  t->Branch("lep1Eta",&lep1Eta,"lep1Eta/F");
  t->Branch("lep1Phi",&lep1Phi,"lep1Phi/F");
  t->Branch("lep1PdgId",&lep1PdgId,"lep1PdgId/I");
  t->Branch("lep1IsTight",&lep1IsTight,"lep1IsTight/I");
  t->Branch("lep2Pt",&lep2Pt,"lep2Pt/F");
  t->Branch("lep2Eta",&lep2Eta,"lep2Eta/F");
  t->Branch("lep2Phi",&lep2Phi,"lep2Phi/F");
  t->Branch("lep2PdgId",&lep2PdgId,"lep2PdgId/I");
  t->Branch("lep2IsTight",&lep2IsTight,"lep2IsTight/I");
  t->Branch("dilep_pt",&dilep_pt,"dilep_pt/F");
  t->Branch("dilep_eta",&dilep_eta,"dilep_eta/F");
  t->Branch("dilep_phi",&dilep_phi,"dilep_phi/F");
  t->Branch("dilep_m",&dilep_m,"dilep_m/F");
  t->Branch("mt",&mt,"mt/F");
  t->Branch("n_tightlep",&n_tightlep,"n_tightlep/I");
  t->Branch("n_looselep",&n_looselep,"n_looselep/I");
  t->Branch("photonPt",&photonPt,"photonPt/F");
  t->Branch("photonEta",&photonEta,"photonEta/F");
  t->Branch("photonPhi",&photonPhi,"photonPhi/F");
  t->Branch("photonIsTight",&photonIsTight,"photonIsTight/I");
  t->Branch("n_tightpho",&n_tightpho,"n_tightpho/I");
  t->Branch("n_loosepho",&n_loosepho,"n_loosepho/I");
  t->Branch("met",&met,"met/F");
  t->Branch("metPhi",&metPhi,"metPhi/F");
  t->Branch("u_perpZ",&u_perpZ,"u_perpZ/F");
  t->Branch("u_paraZ",&u_paraZ,"u_paraZ/F");
  t->Branch("u_magZ",&u_magZ,"u_magZ/F");
  t->Branch("u_phiZ",&u_phiZ,"u_phiZ/F");
  t->Branch("u_perpW",&u_perpW,"u_perpW/F");
  t->Branch("u_paraW",&u_paraW,"u_paraW/F");
  t->Branch("u_magW",&u_magW,"u_magW/F");
  t->Branch("u_phiW",&u_phiW,"u_phiW/F");
  t->Branch("u_perpPho",&u_perpPho,"u_perpPho/F");
  t->Branch("u_paraPho",&u_paraPho,"u_paraPho/F");
  t->Branch("u_magPho",&u_magPho,"u_magPho/F");
  t->Branch("u_phiPho",&u_phiPho,"u_phiPho/F");
  t->Branch("mcWeight",&mcWeight,"mcWeight/F");
  t->Branch("triggerFired",&triggerFired);

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
  jet1Pt = 0;
  jet1Eta = 0;
  jet1Phi = 0;
  jet1dRmet = 0;
  n_jets = 0;
  lep1Pt = 0;
  lep1Eta = 0;
  lep1Phi = 0;
  lep1PdgId = 0;
  lep1IsTight = 0;
  lep2Pt = 0;
  lep2Eta = 0;
  lep2Phi = 0;
  lep2PdgId = 0;
  lep2IsTight = 0;
  dilep_pt = 0;
  dilep_eta = 0;
  dilep_phi = 0;
  dilep_m = 0;
  mt = 0;
  n_tightlep = 0;
  n_looselep = 0;
  photonPt = 0;
  photonEta = 0;
  photonPhi = 0;
  photonIsTight = 0;
  n_tightpho = 0;
  n_loosepho = 0;
  met = 0;
  metPhi = 0;
  u_perpZ = 0;
  u_paraZ = 0;
  u_magZ = 0;
  u_phiZ = 0;
  u_perpW = 0;
  u_paraW = 0;
  u_magW = 0;
  u_phiW = 0;
  u_perpPho = 0;
  u_paraPho = 0;
  u_magPho = 0;
  u_phiPho = 0;
  mcWeight = 0;
  triggerFired = 0;
}
