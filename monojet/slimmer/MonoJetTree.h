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
  int   npvTrue;
  float rho;
  float mcWeight;
  float trueMet;
  float trueMetPhi;
  std::vector<int>*   triggerFired;
  float lep1Pt;
  float lep1Eta;
  float lep1Phi;
  int   lep1PdgId;
  int   lep1IsTight;
  int   lep1IsMedium;
  float lep1DPhiTrueMet;
  float lep1RelIso;
  float lep2Pt;
  float lep2Eta;
  float lep2Phi;
  int   lep2PdgId;
  int   lep2IsTight;
  int   lep2IsMedium;
  float lep2DPhiTrueMet;
  float lep2RelIso;
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
  float u_perp;
  float u_para;
  int   n_bjetsLoose;
  int   n_bjetsMedium;
  int   n_bjetsTight;
  int   leadingJet_outaccp;
  float leadingjetPt;
  float leadingjetEta;
  float leadingjetPhi;
  float leadingjetM;
  int   n_jets;
  int   n_jetsCleanWithEndcap;
  float jet1Pt;
  float jet1Eta;
  float jet1Phi;
  float jet1M;
  float jet1BTag;
  float jet1PuId;
  int   jet1isMonoJetId;
  int   jet1isMonoJetIdNew;
  int   jet1isLooseMonoJetId;
  float jet1DPhiMet;
  float jet1DPhiTrueMet;
  float jet1QGL;
  int   jet1Flavor;
  float jet2Pt;
  float jet2Eta;
  float jet2Phi;
  float jet2M;
  float jet2BTag;
  float jet2PuId;
  int   jet2isMonoJetId;
  int   jet2isMonoJetIdNew;
  int   jet2isLooseMonoJetId;
  float jet2DPhiMet;
  float jet2DPhiTrueMet;
  float jet2QGL;
  int   n_cleanedjets;
  float ht_cleanedjets;
  float dPhi_j1j2;
  float minJetMetDPhi;
  float minJetTrueMetDPhi;
  float minJetMetDPhi_withendcap;
  float minJetTrueMetDPhi_withendcap;
  int   n_tau;
  float boson_pt;
  float boson_phi;
  float genBos_pt;
  float genBos_eta;
  float genBos_phi;
  float genBos_mass;
  int   genBos_PdgId;
  float genMet;
  float genMetPhi;
  float u_perpGen;
  float u_paraGen;
  float fatjet1Pt;
  float fatjet1Eta;
  float fatjet1Phi;
  float fatjet1Mass;
  float fatjet1TrimmedM;
  float fatjet1PrunedM;
  float fatjet1FilteredM;
  float fatjet1SoftDropM;
  float fatjet1tau2;
  float fatjet1tau1;
  float fatjet1tau21;
  int   fatjet1MonojetId;
  float fatjet1QGL;
  float fatjet1QVol;
  float fatjet1DRGenW;
  float fatjet1GenWPt;
  float fatjet1GenWMass;
  float fatjet1DRLooseB;
  float fatjet1DRMediumB;
  float fatjet1DRTightB;
  int   fatjet1isLeading;
  float fatjet1DPhiMet;
  float fatjet1DPhiTrueMet;
  float genDM_pt;
  float genDM_eta;
  float genDM_phi;
  float genDM_mass;
  int   genDM_PdgId;
  float genJet_pt;
  float genJet_eta;
  float genJet_phi;
  float genJet_mass;
  float genJetDRjet1;
  float rawMet;
  float rawMetPhi;
  float genFatJet_pt;
  float genFatJet_eta;
  float genFatJet_phi;
  float genFatJet_mass;
  float genFatJetDRfatjet1;
  bool  IsVBF;
  float jot1Pt;
  float jot1Eta;
  float jot1Phi;
  float jot1M;
  float jot2Pt;
  float jot2Eta;
  float jot2Phi;
  float jot2M;
  float mjj;
  float jjDEta;
  float minJetMetDPhi_clean;

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
