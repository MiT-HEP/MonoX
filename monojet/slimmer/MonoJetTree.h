#ifndef CROMBIE_MONOJETTREE_H
#define CROMBIE_MONOJETTREE_H

#include "TFile.h"
#include "TTree.h"

class MonoJetTree
{
 public:
  MonoJetTree( TTree* tree );
  MonoJetTree( const char* name );
  MonoJetTree( const char* name, TString outFileName );
  MonoJetTree( const char* name, TFile* outFile );
  virtual ~MonoJetTree();

  int   runNum;
  int   lumiNum;
  unsigned long eventNum;
  int   npv;
  float rho;
  float mcWeight;
  float npvWeight;
  float trueMet;
  float trueMetPhi;
  std::vector<int>*   triggerFired;
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
  int   n_tightlep;
  int   n_mediumlep;
  int   n_looselep;
  float leptonSF;
  float photonPt;
  float photonEta;
  float photonPhi;
  int   photonIsMedium;
  int   n_mediumpho;
  int   n_loosepho;
  float met;
  float metPhi;
  int   n_bjetsLoose;
  int   n_bjetsMedium;
  int   n_bjetsTight;
  int   leadingJet_outaccp;
  int   n_jets;
  float jet1Pt;
  float jet1Eta;
  float jet1Phi;
  float jet1M;
  float jet1BTag;
  float jet1PuId;
  int   jet1isMonoJetId;
  int   jet1isMonoJetIdNew;
  float jet2Pt;
  float jet2Eta;
  float jet2Phi;
  float jet2M;
  float jet2BTag;
  float jet2PuId;
  int   jet2isMonoJetId;
  int   jet2isMonoJetIdNew;
  int   n_cleanedjets;
  float dPhi_j1j2;
  float minJetMetDPhi_clean;
  float minJetMetDPhi_withendcap;
  int   n_tau;
  float genBos_pt;
  float genBos_phi;
  int   genBos_PdgId;
  float fatjet1Pt;
  float fatjet1Eta;
  float fatjet1Phi;
  float fatjet1Mass;
  float fatjet1TrimmedM;
  float fatjet1PrunedM;
  float fatjet1SoftDropM;
  float fatjet1tau21;
  int   fatjet1overlapB;
  int   fatleading;

  TTree*  ReturnTree()                { return t;                             }
  void    Fill()                      { t->Fill(); Reset();                   }
  void    Reset();
  void    WriteToFile   ( TFile *f )  { f->WriteTObject(t, t->GetName());     }
  void    Write()                     { fFile->WriteTObject(t, t->GetName());
                                        fFile->Close();                       }

 private:
  TFile* fFile;
  TTree* t;
  void   SetupTree();

  ClassDef(MonoJetTree,1)
};
#endif
