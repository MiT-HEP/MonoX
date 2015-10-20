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

#ifdef MonoJetReader_cxx
MonoJetReader::MonoJetReader(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../../../../GoodRunsV3/monojet_SingleMuon.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../../../GoodRunsV3/monojet_SingleMuon.root");
      }
      f->GetObject("events",tree);

   }
   Init(tree);
}

MonoJetReader::~MonoJetReader()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t MonoJetReader::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t MonoJetReader::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void MonoJetReader::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   triggerFired = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("runNum", &runNum, &b_runNum);
   fChain->SetBranchAddress("lumiNum", &lumiNum, &b_lumiNum);
   fChain->SetBranchAddress("eventNum", &eventNum, &b_eventNum);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("npv", &npv, &b_npv);
   fChain->SetBranchAddress("npvWeight", &npvWeight, &b_npvWeight);
   fChain->SetBranchAddress("kfactor", &kfactor, &b_kfactor);
   fChain->SetBranchAddress("leptonSF", &leptonSF, &b_leptonSF);
   fChain->SetBranchAddress("jet1Pt", &jet1Pt, &b_jet1Pt);
   fChain->SetBranchAddress("jet1Eta", &jet1Eta, &b_jet1Eta);
   fChain->SetBranchAddress("jet1Phi", &jet1Phi, &b_jet1Phi);
   fChain->SetBranchAddress("jet1M", &jet1M, &b_jet1M);
   fChain->SetBranchAddress("jet1BTag", &jet1BTag, &b_jet1BTag);
   fChain->SetBranchAddress("jet1PuId", &jet1PuId, &b_jet1PuId);
   fChain->SetBranchAddress("jet1isMonoJetIdNew", &jet1isMonoJetIdNew, &b_jet1isMonoJetIdNew);
   fChain->SetBranchAddress("jet1isMonoJetId", &jet1isMonoJetId, &b_jet1isMonoJetId);
   fChain->SetBranchAddress("jet1isLooseMonoJetId", &jet1isLooseMonoJetId, &b_jet1isLooseMonoJetId);
   fChain->SetBranchAddress("jet1DPhiMet", &jet1DPhiMet, &b_jet1DPhiMet);
   fChain->SetBranchAddress("jet1DPhiTrueMet", &jet1DPhiTrueMet, &b_jet1DPhiTrueMet);
   fChain->SetBranchAddress("jet1DPhiUZ", &jet1DPhiUZ, &b_jet1DPhiUZ);
   fChain->SetBranchAddress("jet1DPhiUW", &jet1DPhiUW, &b_jet1DPhiUW);
   fChain->SetBranchAddress("jet1DPhiUPho", &jet1DPhiUPho, &b_jet1DPhiUPho);
   fChain->SetBranchAddress("jet2Pt", &jet2Pt, &b_jet2Pt);
   fChain->SetBranchAddress("jet2Eta", &jet2Eta, &b_jet2Eta);
   fChain->SetBranchAddress("jet2Phi", &jet2Phi, &b_jet2Phi);
   fChain->SetBranchAddress("jet2M", &jet2M, &b_jet2M);
   fChain->SetBranchAddress("jet2BTag", &jet2BTag, &b_jet2BTag);
   fChain->SetBranchAddress("jet2PuId", &jet2PuId, &b_jet2PuId);
   fChain->SetBranchAddress("jet2isMonoJetIdNew", &jet2isMonoJetIdNew, &b_jet2isMonoJetIdNew);
   fChain->SetBranchAddress("jet2isMonoJetId", &jet2isMonoJetId, &b_jet2isMonoJetId);
   fChain->SetBranchAddress("jet2isLooseMonoJetId", &jet2isLooseMonoJetId, &b_jet2isLooseMonoJetId);
   fChain->SetBranchAddress("jet2DPhiMet", &jet2DPhiMet, &b_jet2DPhiMet);
   fChain->SetBranchAddress("jet2DPhiTrueMet", &jet2DPhiTrueMet, &b_jet2DPhiTrueMet);
   fChain->SetBranchAddress("jet2DPhiUZ", &jet2DPhiUZ, &b_jet2DPhiUZ);
   fChain->SetBranchAddress("jet2DPhiUW", &jet2DPhiUW, &b_jet2DPhiUW);
   fChain->SetBranchAddress("jet2DPhiUPho", &jet2DPhiUPho, &b_jet2DPhiUPho);
   fChain->SetBranchAddress("n_cleanedjets", &n_cleanedjets, &b_n_cleanedjets);
   fChain->SetBranchAddress("leadingjetPt", &leadingjetPt, &b_leadingjetPt);
   fChain->SetBranchAddress("leadingjetEta", &leadingjetEta, &b_leadingjetEta);
   fChain->SetBranchAddress("leadingjetPhi", &leadingjetPhi, &b_leadingjetPhi);
   fChain->SetBranchAddress("leadingjetM", &leadingjetM, &b_leadingjetM);
   fChain->SetBranchAddress("leadingjetBTag", &leadingjetBTag, &b_leadingjetBTag);
   fChain->SetBranchAddress("leadingjetPuId", &leadingjetPuId, &b_leadingjetPuId);
   fChain->SetBranchAddress("leadingjetisMonoJetIdNew", &leadingjetisMonoJetIdNew, &b_leadingjetisMonoJetIdNew);
   fChain->SetBranchAddress("leadingjetisMonoJetId", &leadingjetisMonoJetId, &b_leadingjetisMonoJetId);
   fChain->SetBranchAddress("leadingjetisLooseMonoJetId", &leadingjetisLooseMonoJetId, &b_leadingjetisLooseMonoJetId);
   fChain->SetBranchAddress("n_jets", &n_jets, &b_n_jets);
   fChain->SetBranchAddress("n_bjetsLoose", &n_bjetsLoose, &b_n_bjetsLoose);
   fChain->SetBranchAddress("n_bjetsMedium", &n_bjetsMedium, &b_n_bjetsMedium);
   fChain->SetBranchAddress("n_bjetsTight", &n_bjetsTight, &b_n_bjetsTight);
   fChain->SetBranchAddress("dPhi_j1j2", &dPhi_j1j2, &b_dPhi_j1j2);
   fChain->SetBranchAddress("minJetMetDPhi", &minJetMetDPhi, &b_minJetMetDPhi);
   fChain->SetBranchAddress("minJetTrueMetDPhi", &minJetTrueMetDPhi, &b_minJetTrueMetDPhi);
   fChain->SetBranchAddress("minJetUZDPhi", &minJetUZDPhi, &b_minJetUZDPhi);
   fChain->SetBranchAddress("minJetUWDPhi", &minJetUWDPhi, &b_minJetUWDPhi);
   fChain->SetBranchAddress("minJetUPhoDPhi", &minJetUPhoDPhi, &b_minJetUPhoDPhi);
   fChain->SetBranchAddress("lep1Pt", &lep1Pt, &b_lep1Pt);
   fChain->SetBranchAddress("lep1Eta", &lep1Eta, &b_lep1Eta);
   fChain->SetBranchAddress("lep1Phi", &lep1Phi, &b_lep1Phi);
   fChain->SetBranchAddress("lep1PdgId", &lep1PdgId, &b_lep1PdgId);
   fChain->SetBranchAddress("lep1IsTight", &lep1IsTight, &b_lep1IsTight);
   fChain->SetBranchAddress("lep1IsMedium", &lep1IsMedium, &b_lep1IsMedium);
   fChain->SetBranchAddress("lep1DPhiMet", &lep1DPhiMet, &b_lep1DPhiMet);
   fChain->SetBranchAddress("lep1RelIso", &lep1RelIso, &b_lep1RelIso);
   fChain->SetBranchAddress("lep2Pt", &lep2Pt, &b_lep2Pt);
   fChain->SetBranchAddress("lep2Eta", &lep2Eta, &b_lep2Eta);
   fChain->SetBranchAddress("lep2Phi", &lep2Phi, &b_lep2Phi);
   fChain->SetBranchAddress("lep2PdgId", &lep2PdgId, &b_lep2PdgId);
   fChain->SetBranchAddress("lep2IsTight", &lep2IsTight, &b_lep2IsTight);
   fChain->SetBranchAddress("lep2IsMedium", &lep2IsMedium, &b_lep2IsMedium);
   fChain->SetBranchAddress("lep2RelIso", &lep2RelIso, &b_lep2RelIso);
   fChain->SetBranchAddress("dilep_pt", &dilep_pt, &b_dilep_pt);
   fChain->SetBranchAddress("dilep_eta", &dilep_eta, &b_dilep_eta);
   fChain->SetBranchAddress("dilep_phi", &dilep_phi, &b_dilep_phi);
   fChain->SetBranchAddress("dilep_m", &dilep_m, &b_dilep_m);
   fChain->SetBranchAddress("mt", &mt, &b_mt);
   fChain->SetBranchAddress("n_tightlep", &n_tightlep, &b_n_tightlep);
   fChain->SetBranchAddress("n_mediumlep", &n_mediumlep, &b_n_mediumlep);
   fChain->SetBranchAddress("n_looselep", &n_looselep, &b_n_looselep);
   fChain->SetBranchAddress("photonPt", &photonPt, &b_photonPt);
   fChain->SetBranchAddress("photonEta", &photonEta, &b_photonEta);
   fChain->SetBranchAddress("photonPhi", &photonPhi, &b_photonPhi);
   fChain->SetBranchAddress("photonIsTight", &photonIsTight, &b_photonIsTight);
   fChain->SetBranchAddress("n_tightpho", &n_tightpho, &b_n_tightpho);
   fChain->SetBranchAddress("n_loosepho", &n_loosepho, &b_n_loosepho);
   fChain->SetBranchAddress("n_tau", &n_tau, &b_n_tau);
   fChain->SetBranchAddress("met", &met, &b_met);
   fChain->SetBranchAddress("metPhi", &metPhi, &b_metPhi);
   fChain->SetBranchAddress("trueMet", &trueMet, &b_trueMet);
   fChain->SetBranchAddress("trueMetPhi", &trueMetPhi, &b_trueMetPhi);
   fChain->SetBranchAddress("u_perpZ", &u_perpZ, &b_u_perpZ);
   fChain->SetBranchAddress("u_paraZ", &u_paraZ, &b_u_paraZ);
   fChain->SetBranchAddress("u_magZ", &u_magZ, &b_u_magZ);
   fChain->SetBranchAddress("u_phiZ", &u_phiZ, &b_u_phiZ);
   fChain->SetBranchAddress("u_magW", &u_magW, &b_u_magW);
   fChain->SetBranchAddress("u_phiW", &u_phiW, &b_u_phiW);
   fChain->SetBranchAddress("u_perpPho", &u_perpPho, &b_u_perpPho);
   fChain->SetBranchAddress("u_paraPho", &u_paraPho, &b_u_paraPho);
   fChain->SetBranchAddress("u_magPho", &u_magPho, &b_u_magPho);
   fChain->SetBranchAddress("u_phiPho", &u_phiPho, &b_u_phiPho);
   fChain->SetBranchAddress("mcWeight", &mcWeight, &b_mcWeight);
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("genBos_pt", &genBos_pt, &b_genBos_pt);
   fChain->SetBranchAddress("genBos_eta", &genBos_eta, &b_genBos_eta);
   fChain->SetBranchAddress("genBos_phi", &genBos_phi, &b_genBos_phi);
   fChain->SetBranchAddress("genBos_m", &genBos_m, &b_genBos_m);
   fChain->SetBranchAddress("genBos_PdgId", &genBos_PdgId, &b_genBos_PdgId);
   fChain->SetBranchAddress("u_perpGen", &u_perpGen, &b_u_perpGen);
   fChain->SetBranchAddress("u_paraGen", &u_paraGen, &b_u_paraGen);
   Notify();
}

Bool_t MonoJetReader::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void MonoJetReader::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t MonoJetReader::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef MonoJetReader_cxx
