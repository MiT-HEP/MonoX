#ifndef MITCROMBIE__TREE_H
#define MITCROMBIE__TREE_H

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"

class MonoJetTree
{
public:
  MonoJetTree( const char *name );
  virtual ~MonoJetTree();

  int   runNum;
  int   lumiNum;
  int   eventNum;
  float rho;
  int   npv;
  float jet1Pt;
  float jet1Eta;
  float jet1Phi;
  float jet1M;
  float jet1PuId;
  int   jet1isMonoJetId;
  int   jet1isLooseMonoJetId;
  float jet1DPhiMet;
  float jet1DPhiTrueMet;
  float jet1DPhiUZ;
  float jet1DPhiUW;
  float jet1DPhiUPho;
  float jet2Pt;
  float jet2Eta;
  float jet2Phi;
  float jet2M;
  float jet2PuId;
  int   jet2isMonoJetId;
  int   jet2isLooseMonoJetId;
  float jet2DPhiMet;
  float jet2DPhiTrueMet;
  float jet2DPhiUZ;
  float jet2DPhiUW;
  float jet2DPhiUPho;
  float jet3Pt;
  float jet3Eta;
  float jet3Phi;
  float jet3M;
  float jet3PuId;
  int   jet3isMonoJetId;
  int   jet3isLooseMonoJetId;
  int   n_cleanedjets;
  float leadingjetPt;
  float leadingjetEta;
  float leadingjetPhi;
  float leadingjetM;
  float leadingjetPuId;
  int   leadingjetisMonoJetId;
  int   leadingjetisLooseMonoJetId;
  float trailingjetPt;
  float trailingjetEta;
  float trailingjetPhi;
  float trailingjetM;
  float trailingjetPuId;
  int   trailingjetisMonoJetId;
  int   trailingjetisLooseMonoJetId;
  int   n_jets;
  float dPhi_j1j2;
  float dR_j1j2;
  float lep1Pt;
  float lep1Eta;
  float lep1Phi;
  int   lep1PdgId;
  int   lep1IsTight;
  int   lep1IsMedium;
  float lep2Pt;
  float lep2Eta;
  float lep2Phi;
  int   lep2PdgId;
  int   lep2IsTight;
  int   lep2IsMedium;
  float dilep_pt;
  float dilep_eta;
  float dilep_phi;
  float dilep_m;
  float mt;
  float genW_pt;
  float genW_phi;
  int   n_tightlep;
  int   n_mediumlep;
  int   n_looselep;
  float photonPt;
  float photonEta;
  float photonPhi;
  int   photonIsTight;
  int   n_tightpho;
  int   n_loosepho;
  float met;
  float metPhi;
  float trueMet;
  float trueMetPhi;
  int   n_tau;
  float u_perpZ;
  float u_paraZ;
  float u_magZ;
  float u_phiZ;
  float u_perpW;
  float u_paraW;
  float u_magW;
  float u_phiW;
  float u_perpPho;
  float u_paraPho;
  float u_magPho;
  float u_phiPho;
  float mcWeight;
  std::vector<int>*   triggerFired;
  std::vector<TLorentzVector*>* test;

  TTree  *ReturnTree()                { return t;                            }
  void    Fill()                      { t->Fill(); Reset();                  }
  void    WriteToFile( TFile *file )  { file->WriteTObject(t, t->GetName()); }

protected:

  TTree *t;
  void   Reset();

  ClassDef(MonoJetTree,1)
};
#endif
