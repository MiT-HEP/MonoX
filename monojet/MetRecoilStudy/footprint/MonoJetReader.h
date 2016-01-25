//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Mon Nov 16 13:41:11 2015 by ROOT version 6.02/05
// from TTree events/events
// found on file: ../../../../flatTreesSkimmedV7/monojet_ZZ.root
//////////////////////////////////////////////////////////

#ifndef MonoJetReader_h
#define MonoJetReader_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include "vector"

class MonoJetReader {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Int_t           runNum;
   Int_t           lumiNum;
   Int_t           eventNum;
   Int_t           npv;
   Float_t         mcWeight;
   Float_t         npvWeight;
   Float_t         trueMet;
   Float_t         trueMetPhi;
   vector<int>     *triggerFired;
   Float_t         lep1Pt;
   Float_t         lep1Eta;
   Float_t         lep1Phi;
   Int_t           lep1PdgId;
   Int_t           lep1IsTight;
   Int_t           lep1IsMedium;
   Float_t         lep1DPhiTrueMet;
   Float_t         lep1RelIso;
   Float_t         lep2Pt;
   Float_t         lep2Eta;
   Float_t         lep2Phi;
   Int_t           lep2PdgId;
   Int_t           lep2IsTight;
   Int_t           lep2IsMedium;
   Float_t         lep2DPhiTrueMet;
   Float_t         lep2RelIso;
   Float_t         dilep_pt;
   Float_t         dilep_eta;
   Float_t         dilep_phi;
   Float_t         dilep_m;
   Float_t         mt;
   Int_t           n_tightlep;
   Int_t           n_mediumlep;
   Int_t           n_looselep;
   Float_t         leptonSF;
   Float_t         photonPt;
   Float_t         photonEta;
   Float_t         photonPhi;
   Int_t           photonIsMedium;
   Int_t           n_mediumpho;
   Int_t           n_loosepho;
   Float_t         met;
   Float_t         metPhi;
   Float_t         u_perp;
   Float_t         u_para;
   Int_t           n_bjetsLoose;
   Int_t           n_bjetsMedium;
   Int_t           n_bjetsTight;
   Float_t         leadingjetPt;
   Float_t         leadingjetEta;
   Float_t         leadingjetPhi;
   Float_t         leadingjetM;
   Int_t           n_jets;
   Float_t         jet1Pt;
   Float_t         jet1Eta;
   Float_t         jet1Phi;
   Float_t         jet1M;
   Float_t         jet1BTag;
   Float_t         jet1PuId;
   Int_t           jet1isMonoJetId;
   Int_t           jet1isMonoJetIdNew;
   Int_t           jet1isLooseMonoJetId;
   Float_t         jet1DPhiMet;
   Float_t         jet1DPhiTrueMet;
   Float_t         jet2Pt;
   Float_t         jet2Eta;
   Float_t         jet2Phi;
   Float_t         jet2M;
   Float_t         jet2BTag;
   Float_t         jet2PuId;
   Int_t           jet2isMonoJetId;
   Int_t           jet2isMonoJetIdNew;
   Int_t           jet2isLooseMonoJetId;
   Float_t         jet2DPhiMet;
   Float_t         jet2DPhiTrueMet;
   Int_t           n_cleanedjets;
   Float_t         dPhi_j1j2;
   Float_t         minJetMetDPhi;
   Float_t         minJetTrueMetDPhi;
   Int_t           n_tau;
   Float_t         boson_pt;
   Float_t         boson_phi;
   Float_t         genBos_pt;
   Float_t         genBos_phi;
   Int_t           genBos_PdgId;
   Float_t         genMet;
   Float_t         genMetPhi;
   Float_t         kfactor;
   Float_t         ewk_z;
   Float_t         ewk_a;
   Float_t         ewk_w;
   Float_t         wkfactor;
   Float_t         u_perpGen;
   Float_t         u_paraGen;
   Float_t         XSecWeight;

   // List of branches
   TBranch        *b_runNum;   //!
   TBranch        *b_lumiNum;   //!
   TBranch        *b_eventNum;   //!
   TBranch        *b_npv;   //!
   TBranch        *b_mcWeight;   //!
   TBranch        *b_npvWeight;   //!
   TBranch        *b_trueMet;   //!
   TBranch        *b_trueMetPhi;   //!
   TBranch        *b_triggerFired;   //!
   TBranch        *b_lep1Pt;   //!
   TBranch        *b_lep1Eta;   //!
   TBranch        *b_lep1Phi;   //!
   TBranch        *b_lep1PdgId;   //!
   TBranch        *b_lep1IsTight;   //!
   TBranch        *b_lep1IsMedium;   //!
   TBranch        *b_lep1DPhiTrueMet;   //!
   TBranch        *b_lep1RelIso;   //!
   TBranch        *b_lep2Pt;   //!
   TBranch        *b_lep2Eta;   //!
   TBranch        *b_lep2Phi;   //!
   TBranch        *b_lep2PdgId;   //!
   TBranch        *b_lep2IsTight;   //!
   TBranch        *b_lep2IsMedium;   //!
   TBranch        *b_lep2DPhiTrueMet;   //!
   TBranch        *b_lep2RelIso;   //!
   TBranch        *b_dilep_pt;   //!
   TBranch        *b_dilep_eta;   //!
   TBranch        *b_dilep_phi;   //!
   TBranch        *b_dilep_m;   //!
   TBranch        *b_mt;   //!
   TBranch        *b_n_tightlep;   //!
   TBranch        *b_n_mediumlep;   //!
   TBranch        *b_n_looselep;   //!
   TBranch        *b_leptonSF;   //!
   TBranch        *b_photonPt;   //!
   TBranch        *b_photonEta;   //!
   TBranch        *b_photonPhi;   //!
   TBranch        *b_photonIsMedium;   //!
   TBranch        *b_n_mediumpho;   //!
   TBranch        *b_n_loosepho;   //!
   TBranch        *b_met;   //!
   TBranch        *b_metPhi;   //!
   TBranch        *b_u_perp;   //!
   TBranch        *b_u_para;   //!
   TBranch        *b_n_bjetsLoose;   //!
   TBranch        *b_n_bjetsMedium;   //!
   TBranch        *b_n_bjetsTight;   //!
   TBranch        *b_leadingjetPt;   //!
   TBranch        *b_leadingjetEta;   //!
   TBranch        *b_leadingjetPhi;   //!
   TBranch        *b_leadingjetM;   //!
   TBranch        *b_n_jets;   //!
   TBranch        *b_jet1Pt;   //!
   TBranch        *b_jet1Eta;   //!
   TBranch        *b_jet1Phi;   //!
   TBranch        *b_jet1M;   //!
   TBranch        *b_jet1BTag;   //!
   TBranch        *b_jet1PuId;   //!
   TBranch        *b_jet1isMonoJetId;   //!
   TBranch        *b_jet1isMonoJetIdNew;   //!
   TBranch        *b_jet1isLooseMonoJetId;   //!
   TBranch        *b_jet1DPhiMet;   //!
   TBranch        *b_jet1DPhiTrueMet;   //!
   TBranch        *b_jet2Pt;   //!
   TBranch        *b_jet2Eta;   //!
   TBranch        *b_jet2Phi;   //!
   TBranch        *b_jet2M;   //!
   TBranch        *b_jet2BTag;   //!
   TBranch        *b_jet2PuId;   //!
   TBranch        *b_jet2isMonoJetId;   //!
   TBranch        *b_jet2isMonoJetIdNew;   //!
   TBranch        *b_jet2isLooseMonoJetId;   //!
   TBranch        *b_jet2DPhiMet;   //!
   TBranch        *b_jet2DPhiTrueMet;   //!
   TBranch        *b_n_cleanedjets;   //!
   TBranch        *b_dPhi_j1j2;   //!
   TBranch        *b_minJetMetDPhi;   //!
   TBranch        *b_minJetTrueMetDPhi;   //!
   TBranch        *b_n_tau;   //!
   TBranch        *b_boson_pt;   //!
   TBranch        *b_boson_phi;   //!
   TBranch        *b_genBos_pt;   //!
   TBranch        *b_genBos_phi;   //!
   TBranch        *b_genBos_PdgId;   //!
   TBranch        *b_genMet;   //!
   TBranch        *b_genMetPhi;   //!
   TBranch        *b_kfactor;   //!
   TBranch        *b_ewk_z;   //!
   TBranch        *b_ewk_a;   //!
   TBranch        *b_ewk_w;   //!
   TBranch        *b_wkfactor;   //!
   TBranch        *b_u_perpGen;   //!
   TBranch        *b_u_paraGen;   //!
   TBranch        *b_XSecWeight;   //!

   MonoJetReader(TTree *tree=0);
   virtual ~MonoJetReader();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif
