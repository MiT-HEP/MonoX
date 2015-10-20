//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Oct 20 14:51:42 2015 by ROOT version 6.05/02
// from TTree events/events
// found on file: ../../../../GoodRunsV3/monojet_SingleMuon.root
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
   Float_t         rho;
   Int_t           npv;
   Float_t         npvWeight;
   Float_t         kfactor;
   Float_t         leptonSF;
   Float_t         jet1Pt;
   Float_t         jet1Eta;
   Float_t         jet1Phi;
   Float_t         jet1M;
   Float_t         jet1BTag;
   Float_t         jet1PuId;
   Int_t           jet1isMonoJetIdNew;
   Int_t           jet1isMonoJetId;
   Int_t           jet1isLooseMonoJetId;
   Float_t         jet1DPhiMet;
   Float_t         jet1DPhiTrueMet;
   Float_t         jet1DPhiUZ;
   Float_t         jet1DPhiUW;
   Float_t         jet1DPhiUPho;
   Float_t         jet2Pt;
   Float_t         jet2Eta;
   Float_t         jet2Phi;
   Float_t         jet2M;
   Float_t         jet2BTag;
   Float_t         jet2PuId;
   Int_t           jet2isMonoJetIdNew;
   Int_t           jet2isMonoJetId;
   Int_t           jet2isLooseMonoJetId;
   Float_t         jet2DPhiMet;
   Float_t         jet2DPhiTrueMet;
   Float_t         jet2DPhiUZ;
   Float_t         jet2DPhiUW;
   Float_t         jet2DPhiUPho;
   Int_t           n_cleanedjets;
   Float_t         leadingjetPt;
   Float_t         leadingjetEta;
   Float_t         leadingjetPhi;
   Float_t         leadingjetM;
   Float_t         leadingjetBTag;
   Float_t         leadingjetPuId;
   Int_t           leadingjetisMonoJetIdNew;
   Int_t           leadingjetisMonoJetId;
   Int_t           leadingjetisLooseMonoJetId;
   Int_t           n_jets;
   Int_t           n_bjetsLoose;
   Int_t           n_bjetsMedium;
   Int_t           n_bjetsTight;
   Float_t         dPhi_j1j2;
   Float_t         minJetMetDPhi;
   Float_t         minJetTrueMetDPhi;
   Float_t         minJetUZDPhi;
   Float_t         minJetUWDPhi;
   Float_t         minJetUPhoDPhi;
   Float_t         lep1Pt;
   Float_t         lep1Eta;
   Float_t         lep1Phi;
   Int_t           lep1PdgId;
   Int_t           lep1IsTight;
   Int_t           lep1IsMedium;
   Float_t         lep1DPhiMet;
   Float_t         lep1RelIso;
   Float_t         lep2Pt;
   Float_t         lep2Eta;
   Float_t         lep2Phi;
   Int_t           lep2PdgId;
   Int_t           lep2IsTight;
   Int_t           lep2IsMedium;
   Float_t         lep2RelIso;
   Float_t         dilep_pt;
   Float_t         dilep_eta;
   Float_t         dilep_phi;
   Float_t         dilep_m;
   Float_t         mt;
   Int_t           n_tightlep;
   Int_t           n_mediumlep;
   Int_t           n_looselep;
   Float_t         photonPt;
   Float_t         photonEta;
   Float_t         photonPhi;
   Int_t           photonIsTight;
   Int_t           n_tightpho;
   Int_t           n_loosepho;
   Int_t           n_tau;
   Float_t         met;
   Float_t         metPhi;
   Float_t         trueMet;
   Float_t         trueMetPhi;
   Float_t         u_perpZ;
   Float_t         u_paraZ;
   Float_t         u_magZ;
   Float_t         u_phiZ;
   Float_t         u_magW;
   Float_t         u_phiW;
   Float_t         u_perpPho;
   Float_t         u_paraPho;
   Float_t         u_magPho;
   Float_t         u_phiPho;
   Float_t         mcWeight;
   vector<int>     *triggerFired;
   Float_t         genBos_pt;
   Float_t         genBos_eta;
   Float_t         genBos_phi;
   Float_t         genBos_m;
   Int_t           genBos_PdgId;
   Float_t         u_perpGen;
   Float_t         u_paraGen;

   // List of branches
   TBranch        *b_runNum;   //!
   TBranch        *b_lumiNum;   //!
   TBranch        *b_eventNum;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_npv;   //!
   TBranch        *b_npvWeight;   //!
   TBranch        *b_kfactor;   //!
   TBranch        *b_leptonSF;   //!
   TBranch        *b_jet1Pt;   //!
   TBranch        *b_jet1Eta;   //!
   TBranch        *b_jet1Phi;   //!
   TBranch        *b_jet1M;   //!
   TBranch        *b_jet1BTag;   //!
   TBranch        *b_jet1PuId;   //!
   TBranch        *b_jet1isMonoJetIdNew;   //!
   TBranch        *b_jet1isMonoJetId;   //!
   TBranch        *b_jet1isLooseMonoJetId;   //!
   TBranch        *b_jet1DPhiMet;   //!
   TBranch        *b_jet1DPhiTrueMet;   //!
   TBranch        *b_jet1DPhiUZ;   //!
   TBranch        *b_jet1DPhiUW;   //!
   TBranch        *b_jet1DPhiUPho;   //!
   TBranch        *b_jet2Pt;   //!
   TBranch        *b_jet2Eta;   //!
   TBranch        *b_jet2Phi;   //!
   TBranch        *b_jet2M;   //!
   TBranch        *b_jet2BTag;   //!
   TBranch        *b_jet2PuId;   //!
   TBranch        *b_jet2isMonoJetIdNew;   //!
   TBranch        *b_jet2isMonoJetId;   //!
   TBranch        *b_jet2isLooseMonoJetId;   //!
   TBranch        *b_jet2DPhiMet;   //!
   TBranch        *b_jet2DPhiTrueMet;   //!
   TBranch        *b_jet2DPhiUZ;   //!
   TBranch        *b_jet2DPhiUW;   //!
   TBranch        *b_jet2DPhiUPho;   //!
   TBranch        *b_n_cleanedjets;   //!
   TBranch        *b_leadingjetPt;   //!
   TBranch        *b_leadingjetEta;   //!
   TBranch        *b_leadingjetPhi;   //!
   TBranch        *b_leadingjetM;   //!
   TBranch        *b_leadingjetBTag;   //!
   TBranch        *b_leadingjetPuId;   //!
   TBranch        *b_leadingjetisMonoJetIdNew;   //!
   TBranch        *b_leadingjetisMonoJetId;   //!
   TBranch        *b_leadingjetisLooseMonoJetId;   //!
   TBranch        *b_n_jets;   //!
   TBranch        *b_n_bjetsLoose;   //!
   TBranch        *b_n_bjetsMedium;   //!
   TBranch        *b_n_bjetsTight;   //!
   TBranch        *b_dPhi_j1j2;   //!
   TBranch        *b_minJetMetDPhi;   //!
   TBranch        *b_minJetTrueMetDPhi;   //!
   TBranch        *b_minJetUZDPhi;   //!
   TBranch        *b_minJetUWDPhi;   //!
   TBranch        *b_minJetUPhoDPhi;   //!
   TBranch        *b_lep1Pt;   //!
   TBranch        *b_lep1Eta;   //!
   TBranch        *b_lep1Phi;   //!
   TBranch        *b_lep1PdgId;   //!
   TBranch        *b_lep1IsTight;   //!
   TBranch        *b_lep1IsMedium;   //!
   TBranch        *b_lep1DPhiMet;   //!
   TBranch        *b_lep1RelIso;   //!
   TBranch        *b_lep2Pt;   //!
   TBranch        *b_lep2Eta;   //!
   TBranch        *b_lep2Phi;   //!
   TBranch        *b_lep2PdgId;   //!
   TBranch        *b_lep2IsTight;   //!
   TBranch        *b_lep2IsMedium;   //!
   TBranch        *b_lep2RelIso;   //!
   TBranch        *b_dilep_pt;   //!
   TBranch        *b_dilep_eta;   //!
   TBranch        *b_dilep_phi;   //!
   TBranch        *b_dilep_m;   //!
   TBranch        *b_mt;   //!
   TBranch        *b_n_tightlep;   //!
   TBranch        *b_n_mediumlep;   //!
   TBranch        *b_n_looselep;   //!
   TBranch        *b_photonPt;   //!
   TBranch        *b_photonEta;   //!
   TBranch        *b_photonPhi;   //!
   TBranch        *b_photonIsTight;   //!
   TBranch        *b_n_tightpho;   //!
   TBranch        *b_n_loosepho;   //!
   TBranch        *b_n_tau;   //!
   TBranch        *b_met;   //!
   TBranch        *b_metPhi;   //!
   TBranch        *b_trueMet;   //!
   TBranch        *b_trueMetPhi;   //!
   TBranch        *b_u_perpZ;   //!
   TBranch        *b_u_paraZ;   //!
   TBranch        *b_u_magZ;   //!
   TBranch        *b_u_phiZ;   //!
   TBranch        *b_u_magW;   //!
   TBranch        *b_u_phiW;   //!
   TBranch        *b_u_perpPho;   //!
   TBranch        *b_u_paraPho;   //!
   TBranch        *b_u_magPho;   //!
   TBranch        *b_u_phiPho;   //!
   TBranch        *b_mcWeight;   //!
   TBranch        *b_triggerFired;   //!
   TBranch        *b_genBos_pt;   //!
   TBranch        *b_genBos_eta;   //!
   TBranch        *b_genBos_phi;   //!
   TBranch        *b_genBos_m;   //!
   TBranch        *b_genBos_PdgId;   //!
   TBranch        *b_u_perpGen;   //!
   TBranch        *b_u_paraGen;   //!

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
