#ifndef MITCROMBIE_MERGED_MERGEDTREE_H
#define MITCROMBIE_MERGED_MERGEDTREE_H

#include "TFile.h"
#include "TTree.h"

class MergedTree
{
public:
  MergedTree( const char *name );
  virtual ~MergedTree();

  int   runNum;
  int   lumiNum;
  int   eventNum;
  float rho;
  int   npv;
  float jet1Pt;
  float jet1Eta;
  float jet1Phi;
  float jet1M;
  float jet1BTag;
  float jet1PuId;
  int   jet1isMonoJetIdNew;
  int   jet1isMonoJetId;
  int   jet1isLooseMonoJetId;
  float jet1DPhiMet;
  float jet1DPhiTrueMet;
  float jet2Pt;
  float jet2Eta;
  float jet2Phi;
  float jet2M;
  float jet2BTag;
  float jet2PuId;
  int   jet2isMonoJetIdNew;
  int   jet2isMonoJetId;
  int   jet2isLooseMonoJetId;
  float jet2DPhiMet;
  float jet2DPhiTrueMet;
  int   n_cleanedjets;
  int   n_jets;
  int   n_bjetsLoose;
  int   n_bjetsMedium;
  int   n_bjetsTight;
  float dPhi_j1j2;
  float minJetMetDPhi;
  float minJetTrueMetDPhi;
  float lep1Pt;
  float lep1Eta;
  float lep1Phi;
  int   lep1PdgId;
  int   lep1IsTight;
  int   lep1IsMedium;
  float lep1DPhiMet;
  float lep1RelIso;
  float lep2Pt;
  float lep2Eta;
  float lep2Phi;
  int   lep2PdgId;
  int   lep2IsTight;
  int   lep2IsMedium;
  float lep2RelIso;
  float dilep_pt;
  float dilep_eta;
  float dilep_phi;
  float dilep_m;
  int   n_tightlep;
  int   n_mediumlep;
  int   n_looselep;
  float photonPtRaw;
  float photonPt;
  float photonPtCheck;
  float photonEta;
  float photonPhi;
  int   photonIsTight;
  int   n_tightpho;
  int   n_loosepho;
  int   n_tau;
  float met;
  float metPhi;
  float trueMet;
  float trueMetPhi;
  float u_perp;
  float u_para;
  std::vector<int>*   triggerFired;
  bool  correctEvent;

  TTree  *ReturnTree()                { return t;                            }
  void    Fill()                      { t->Fill(); Reset();                  }
  void    WriteToFile( TFile *file )  { file->WriteTObject(t, t->GetName()); }

protected:

  TTree *t;
  void   Reset();

  ClassDef(MergedTree,1)
};
#endif
