#define MonoJetReader_cxx
#include "MonoJetReader.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void MonoJetReader::Loop()
{
//   In a ROOT session, you can do:
//      root> .L MonoJetReader.C
//      root> MonoJetReader t
//      root> t.GetEntry(12); // Fill t data members with entry number 12
//      root> t.Show();       // Show values of entry 12
//      root> t.Show(16);     // Read and show values of entry 16
//      root> t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      // if (Cut(ientry) < 0) continue;
   }
}

MonoJetReader::MonoJetReader(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../../../../flatTreesSkimmedV7/monojet_ZZ.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../../../flatTreesSkimmedV7/monojet_ZZ.root");
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
   fChain->SetBranchAddress("npv", &npv, &b_npv);
   fChain->SetBranchAddress("mcWeight", &mcWeight, &b_mcWeight);
   fChain->SetBranchAddress("npvWeight", &npvWeight, &b_npvWeight);
   fChain->SetBranchAddress("trueMet", &trueMet, &b_trueMet);
   fChain->SetBranchAddress("trueMetPhi", &trueMetPhi, &b_trueMetPhi);
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("lep1Pt", &lep1Pt, &b_lep1Pt);
   fChain->SetBranchAddress("lep1Eta", &lep1Eta, &b_lep1Eta);
   fChain->SetBranchAddress("lep1Phi", &lep1Phi, &b_lep1Phi);
   fChain->SetBranchAddress("lep1PdgId", &lep1PdgId, &b_lep1PdgId);
   fChain->SetBranchAddress("lep1IsTight", &lep1IsTight, &b_lep1IsTight);
   fChain->SetBranchAddress("lep1IsMedium", &lep1IsMedium, &b_lep1IsMedium);
   fChain->SetBranchAddress("lep1DPhiTrueMet", &lep1DPhiTrueMet, &b_lep1DPhiTrueMet);
   fChain->SetBranchAddress("lep1RelIso", &lep1RelIso, &b_lep1RelIso);
   fChain->SetBranchAddress("lep2Pt", &lep2Pt, &b_lep2Pt);
   fChain->SetBranchAddress("lep2Eta", &lep2Eta, &b_lep2Eta);
   fChain->SetBranchAddress("lep2Phi", &lep2Phi, &b_lep2Phi);
   fChain->SetBranchAddress("lep2PdgId", &lep2PdgId, &b_lep2PdgId);
   fChain->SetBranchAddress("lep2IsTight", &lep2IsTight, &b_lep2IsTight);
   fChain->SetBranchAddress("lep2IsMedium", &lep2IsMedium, &b_lep2IsMedium);
   fChain->SetBranchAddress("lep2DPhiTrueMet", &lep2DPhiTrueMet, &b_lep2DPhiTrueMet);
   fChain->SetBranchAddress("lep2RelIso", &lep2RelIso, &b_lep2RelIso);
   fChain->SetBranchAddress("dilep_pt", &dilep_pt, &b_dilep_pt);
   fChain->SetBranchAddress("dilep_eta", &dilep_eta, &b_dilep_eta);
   fChain->SetBranchAddress("dilep_phi", &dilep_phi, &b_dilep_phi);
   fChain->SetBranchAddress("dilep_m", &dilep_m, &b_dilep_m);
   fChain->SetBranchAddress("mt", &mt, &b_mt);
   fChain->SetBranchAddress("n_tightlep", &n_tightlep, &b_n_tightlep);
   fChain->SetBranchAddress("n_mediumlep", &n_mediumlep, &b_n_mediumlep);
   fChain->SetBranchAddress("n_looselep", &n_looselep, &b_n_looselep);
   fChain->SetBranchAddress("leptonSF", &leptonSF, &b_leptonSF);
   fChain->SetBranchAddress("photonPt", &photonPt, &b_photonPt);
   fChain->SetBranchAddress("photonEta", &photonEta, &b_photonEta);
   fChain->SetBranchAddress("photonPhi", &photonPhi, &b_photonPhi);
   fChain->SetBranchAddress("photonIsMedium", &photonIsMedium, &b_photonIsMedium);
   fChain->SetBranchAddress("n_mediumpho", &n_mediumpho, &b_n_mediumpho);
   fChain->SetBranchAddress("n_loosepho", &n_loosepho, &b_n_loosepho);
   fChain->SetBranchAddress("met", &met, &b_met);
   fChain->SetBranchAddress("metPhi", &metPhi, &b_metPhi);
   fChain->SetBranchAddress("u_perp", &u_perp, &b_u_perp);
   fChain->SetBranchAddress("u_para", &u_para, &b_u_para);
   fChain->SetBranchAddress("n_bjetsLoose", &n_bjetsLoose, &b_n_bjetsLoose);
   fChain->SetBranchAddress("n_bjetsMedium", &n_bjetsMedium, &b_n_bjetsMedium);
   fChain->SetBranchAddress("n_bjetsTight", &n_bjetsTight, &b_n_bjetsTight);
   fChain->SetBranchAddress("leadingjetPt", &leadingjetPt, &b_leadingjetPt);
   fChain->SetBranchAddress("leadingjetEta", &leadingjetEta, &b_leadingjetEta);
   fChain->SetBranchAddress("leadingjetPhi", &leadingjetPhi, &b_leadingjetPhi);
   fChain->SetBranchAddress("leadingjetM", &leadingjetM, &b_leadingjetM);
   fChain->SetBranchAddress("n_jets", &n_jets, &b_n_jets);
   fChain->SetBranchAddress("jet1Pt", &jet1Pt, &b_jet1Pt);
   fChain->SetBranchAddress("jet1Eta", &jet1Eta, &b_jet1Eta);
   fChain->SetBranchAddress("jet1Phi", &jet1Phi, &b_jet1Phi);
   fChain->SetBranchAddress("jet1M", &jet1M, &b_jet1M);
   fChain->SetBranchAddress("jet1BTag", &jet1BTag, &b_jet1BTag);
   fChain->SetBranchAddress("jet1PuId", &jet1PuId, &b_jet1PuId);
   fChain->SetBranchAddress("jet1isMonoJetId", &jet1isMonoJetId, &b_jet1isMonoJetId);
   fChain->SetBranchAddress("jet1isMonoJetIdNew", &jet1isMonoJetIdNew, &b_jet1isMonoJetIdNew);
   fChain->SetBranchAddress("jet1isLooseMonoJetId", &jet1isLooseMonoJetId, &b_jet1isLooseMonoJetId);
   fChain->SetBranchAddress("jet1DPhiMet", &jet1DPhiMet, &b_jet1DPhiMet);
   fChain->SetBranchAddress("jet1DPhiTrueMet", &jet1DPhiTrueMet, &b_jet1DPhiTrueMet);
   fChain->SetBranchAddress("jet2Pt", &jet2Pt, &b_jet2Pt);
   fChain->SetBranchAddress("jet2Eta", &jet2Eta, &b_jet2Eta);
   fChain->SetBranchAddress("jet2Phi", &jet2Phi, &b_jet2Phi);
   fChain->SetBranchAddress("jet2M", &jet2M, &b_jet2M);
   fChain->SetBranchAddress("jet2BTag", &jet2BTag, &b_jet2BTag);
   fChain->SetBranchAddress("jet2PuId", &jet2PuId, &b_jet2PuId);
   fChain->SetBranchAddress("jet2isMonoJetId", &jet2isMonoJetId, &b_jet2isMonoJetId);
   fChain->SetBranchAddress("jet2isMonoJetIdNew", &jet2isMonoJetIdNew, &b_jet2isMonoJetIdNew);
   fChain->SetBranchAddress("jet2isLooseMonoJetId", &jet2isLooseMonoJetId, &b_jet2isLooseMonoJetId);
   fChain->SetBranchAddress("jet2DPhiMet", &jet2DPhiMet, &b_jet2DPhiMet);
   fChain->SetBranchAddress("jet2DPhiTrueMet", &jet2DPhiTrueMet, &b_jet2DPhiTrueMet);
   fChain->SetBranchAddress("n_cleanedjets", &n_cleanedjets, &b_n_cleanedjets);
   fChain->SetBranchAddress("dPhi_j1j2", &dPhi_j1j2, &b_dPhi_j1j2);
   fChain->SetBranchAddress("minJetMetDPhi", &minJetMetDPhi, &b_minJetMetDPhi);
   fChain->SetBranchAddress("minJetTrueMetDPhi", &minJetTrueMetDPhi, &b_minJetTrueMetDPhi);
   fChain->SetBranchAddress("n_tau", &n_tau, &b_n_tau);
   fChain->SetBranchAddress("boson_pt", &boson_pt, &b_boson_pt);
   fChain->SetBranchAddress("boson_phi", &boson_phi, &b_boson_phi);
   fChain->SetBranchAddress("genBos_pt", &genBos_pt, &b_genBos_pt);
   fChain->SetBranchAddress("genBos_phi", &genBos_phi, &b_genBos_phi);
   fChain->SetBranchAddress("genBos_PdgId", &genBos_PdgId, &b_genBos_PdgId);
   fChain->SetBranchAddress("genMet", &genMet, &b_genMet);
   fChain->SetBranchAddress("genMetPhi", &genMetPhi, &b_genMetPhi);
   fChain->SetBranchAddress("kfactor", &kfactor, &b_kfactor);
   fChain->SetBranchAddress("ewk_z", &ewk_z, &b_ewk_z);
   fChain->SetBranchAddress("ewk_a", &ewk_a, &b_ewk_a);
   fChain->SetBranchAddress("ewk_w", &ewk_w, &b_ewk_w);
   fChain->SetBranchAddress("wkfactor", &wkfactor, &b_wkfactor);
   fChain->SetBranchAddress("u_perpGen", &u_perpGen, &b_u_perpGen);
   fChain->SetBranchAddress("u_paraGen", &u_paraGen, &b_u_paraGen);
   fChain->SetBranchAddress("XSecWeight", &XSecWeight, &b_XSecWeight);
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
