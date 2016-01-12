#define NeroTree_cxx
#include "NeroTree.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void NeroTree::Loop()
{
//   In a ROOT session, you can do:
//      root> .L NeroTree.C
//      root> NeroTree t
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

NeroTree::NeroTree(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("root://eoscms//eos/cms/store/user/dmytro/Nero/v1.1.1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring15MiniAODv2_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_p2/151104_133348/0000/NeroNtuples_skimmed_3.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("root://eoscms//eos/cms/store/user/dmytro/Nero/v1.1.1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring15MiniAODv2_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_p2/151104_133348/0000/NeroNtuples_skimmed_3.root");
      }
      TDirectory * dir = (TDirectory*)f->Get("root://eoscms//eos/cms/store/user/dmytro/Nero/v1.1.1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring15MiniAODv2_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_p2/151104_133348/0000/NeroNtuples_skimmed_3.root:/nero");
      dir->GetObject("events",tree);

   }
   Init(tree);
}

NeroTree::~NeroTree()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t NeroTree::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t NeroTree::LoadTree(Long64_t entry)
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

void NeroTree::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   jetP4 = 0;
   jetMatch = 0;
   jetRawPt = 0;
   jetBdiscr = 0;
   jetBdiscrLegacy = 0;
   jetPuId = 0;
   jetUnc = 0;
   jetQGL = 0;
   jetFlavour = 0;
   jetMatchedPartonPdgId = 0;
   jetMotherPdgId = 0;
   jetGrMotherPdgId = 0;
   jetSelBits = 0;
   jetQ = 0;
   jetQnoPU = 0;
   tauP4 = 0;
   tauMatch = 0;
   tauSelBits = 0;
   tauQ = 0;
   tauM = 0;
   tauIso = 0;
   tauChargedIsoPtSum = 0;
   tauNeutralIsoPtSum = 0;
   tauIsoDeltaBetaCorr = 0;
   lepP4 = 0;
   lepMatch = 0;
   lepPdgId = 0;
   lepIso = 0;
   lepSelBits = 0;
   lepPfPt = 0;
   lepChIso = 0;
   lepNhIso = 0;
   lepPhoIso = 0;
   lepPuIso = 0;
   fatjetP4 = 0;
   fatjetRawPt = 0;
   fatjetFlavour = 0;
   fatjetTau1 = 0;
   fatjetTau2 = 0;
   fatjetTau3 = 0;
   fatjetTrimmedMass = 0;
   fatjetPrunedMass = 0;
   fatjetFilteredMass = 0;
   fatjetSoftdropMass = 0;
   ak8_subjet = 0;
   ak8jet_hasSubjet = 0;
   ak8subjet_btag = 0;
   fatjetHbb = 0;
   fatjettopMVA = 0;
   metP4 = 0;
   metPtJESUP = 0;
   metPtJESDOWN = 0;
   metP4_GEN = 0;
   metPuppi = 0;
   metPuppiSyst = 0;
   metNoMu = 0;
   metNoHF = 0;
   pfMet_e3p0 = 0;
   trackMet = 0;
   photonP4 = 0;
   photonIso = 0;
   photonSieie = 0;
   photonSelBits = 0;
   photonChIso = 0;
   photonChIsoRC = 0;
   photonNhIso = 0;
   photonNhIsoRC = 0;
   photonPhoIso = 0;
   photonPhoIsoRC = 0;
   photonPuIso = 0;
   photonPuIsoRC = 0;
   genP4 = 0;
   genjetP4 = 0;
   genPdgId = 0;
   triggerFired = 0;
   triggerPrescale = 0;
   triggerLeps = 0;
   triggerJets = 0;
   triggerTaus = 0;
   triggerPhotons = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("isRealData", &isRealData, &b_isRealData);
   fChain->SetBranchAddress("runNum", &runNum, &b_runNum);
   fChain->SetBranchAddress("lumiNum", &lumiNum, &b_lumiNum);
   fChain->SetBranchAddress("eventNum", &eventNum, &b_eventNum);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("npv", &npv, &b_npv);
   fChain->SetBranchAddress("jetP4", &jetP4, &b_jetP4);
   fChain->SetBranchAddress("jetMatch", &jetMatch, &b_jetMatch);
   fChain->SetBranchAddress("jetRawPt", &jetRawPt, &b_jetRawPt);
   fChain->SetBranchAddress("jetBdiscr", &jetBdiscr, &b_jetBdiscr);
   fChain->SetBranchAddress("jetBdiscrLegacy", &jetBdiscrLegacy, &b_jetBdiscrLegacy);
   fChain->SetBranchAddress("jetPuId", &jetPuId, &b_jetPuId);
   fChain->SetBranchAddress("jetUnc", &jetUnc, &b_jetUnc);
   fChain->SetBranchAddress("jetQGL", &jetQGL, &b_jetQGL);
   fChain->SetBranchAddress("jetFlavour", &jetFlavour, &b_jetFlavour);
   fChain->SetBranchAddress("jetMatchedPartonPdgId", &jetMatchedPartonPdgId, &b_jetMatchedPartonPdgId);
   fChain->SetBranchAddress("jetMotherPdgId", &jetMotherPdgId, &b_jetMotherPdgId);
   fChain->SetBranchAddress("jetGrMotherPdgId", &jetGrMotherPdgId, &b_jetGrMotherPdgId);
   fChain->SetBranchAddress("jetSelBits", &jetSelBits, &b_jetSelBits);
   fChain->SetBranchAddress("jetQ", &jetQ, &b_jetQ);
   fChain->SetBranchAddress("jetQnoPU", &jetQnoPU, &b_jetQnoPU);
   fChain->SetBranchAddress("tauP4", &tauP4, &b_tauP4);
   fChain->SetBranchAddress("tauMatch", &tauMatch, &b_tauMatch);
   fChain->SetBranchAddress("tauSelBits", &tauSelBits, &b_tauSelBits);
   fChain->SetBranchAddress("tauQ", &tauQ, &b_tauQ);
   fChain->SetBranchAddress("tauM", &tauM, &b_tauM);
   fChain->SetBranchAddress("tauIso", &tauIso, &b_tauIso);
   fChain->SetBranchAddress("tauChargedIsoPtSum", &tauChargedIsoPtSum, &b_tauChargedIsoPtSum);
   fChain->SetBranchAddress("tauNeutralIsoPtSum", &tauNeutralIsoPtSum, &b_tauNeutralIsoPtSum);
   fChain->SetBranchAddress("tauIsoDeltaBetaCorr", &tauIsoDeltaBetaCorr, &b_tauIsoDeltaBetaCorr);
   fChain->SetBranchAddress("lepP4", &lepP4, &b_lepP4);
   fChain->SetBranchAddress("lepMatch", &lepMatch, &b_lepMatch);
   fChain->SetBranchAddress("lepPdgId", &lepPdgId, &b_lepPdgId);
   fChain->SetBranchAddress("lepIso", &lepIso, &b_lepIso);
   fChain->SetBranchAddress("lepSelBits", &lepSelBits, &b_lepSelBits);
   fChain->SetBranchAddress("lepPfPt", &lepPfPt, &b_lepPfPt);
   fChain->SetBranchAddress("lepChIso", &lepChIso, &b_lepChIso);
   fChain->SetBranchAddress("lepNhIso", &lepNhIso, &b_lepNhIso);
   fChain->SetBranchAddress("lepPhoIso", &lepPhoIso, &b_lepPhoIso);
   fChain->SetBranchAddress("lepPuIso", &lepPuIso, &b_lepPuIso);
   fChain->SetBranchAddress("fatjetP4", &fatjetP4, &b_fatjetP4);
   fChain->SetBranchAddress("fatjetRawPt", &fatjetRawPt, &b_fatjetRawPt);
   fChain->SetBranchAddress("fatjetFlavour", &fatjetFlavour, &b_fatjetFlavour);
   fChain->SetBranchAddress("fatjetTau1", &fatjetTau1, &b_fatjetTau1);
   fChain->SetBranchAddress("fatjetTau2", &fatjetTau2, &b_fatjetTau2);
   fChain->SetBranchAddress("fatjetTau3", &fatjetTau3, &b_fatjetTau3);
   fChain->SetBranchAddress("fatjetTrimmedMass", &fatjetTrimmedMass, &b_fatjetTrimmedMass);
   fChain->SetBranchAddress("fatjetPrunedMass", &fatjetPrunedMass, &b_fatjetPrunedMass);
   fChain->SetBranchAddress("fatjetFilteredMass", &fatjetFilteredMass, &b_fatjetFilteredMass);
   fChain->SetBranchAddress("fatjetSoftdropMass", &fatjetSoftdropMass, &b_fatjetSoftdropMass);
   fChain->SetBranchAddress("ak8_subjet", &ak8_subjet, &b_ak8_subjet);
   fChain->SetBranchAddress("ak8jet_hasSubjet", &ak8jet_hasSubjet, &b_ak8jet_hasSubjet);
   fChain->SetBranchAddress("ak8subjet_btag", &ak8subjet_btag, &b_ak8subjet_btag);
   fChain->SetBranchAddress("fatjetHbb", &fatjetHbb, &b_fatjetHbb);
   fChain->SetBranchAddress("fatjettopMVA", &fatjettopMVA, &b_fatjettopMVA);
   fChain->SetBranchAddress("metP4", &metP4, &b_metP4);
   fChain->SetBranchAddress("metPtJESUP", &metPtJESUP, &b_metPtJESUP);
   fChain->SetBranchAddress("metPtJESDOWN", &metPtJESDOWN, &b_metPtJESDOWN);
   fChain->SetBranchAddress("metP4_GEN", &metP4_GEN, &b_metP4_GEN);
   fChain->SetBranchAddress("metPuppi", &metPuppi, &b_metPuppi);
   fChain->SetBranchAddress("metPuppiSyst", &metPuppiSyst, &b_metPuppiSyst);
   fChain->SetBranchAddress("metNoMu", &metNoMu, &b_metNoMu);
   fChain->SetBranchAddress("metNoHF", &metNoHF, &b_metNoHF);
   fChain->SetBranchAddress("pfMet_e3p0", &pfMet_e3p0, &b_pfMet_e3p0);
   fChain->SetBranchAddress("trackMet", &trackMet, &b_trackMet);
   fChain->SetBranchAddress("caloMet_Pt", &caloMet_Pt, &b_caloMet_Pt);
   fChain->SetBranchAddress("caloMet_Phi", &caloMet_Phi, &b_caloMet_Phi);
   fChain->SetBranchAddress("caloMet_SumEt", &caloMet_SumEt, &b_caloMet_SumEt);
   fChain->SetBranchAddress("photonP4", &photonP4, &b_photonP4);
   fChain->SetBranchAddress("photonIso", &photonIso, &b_photonIso);
   fChain->SetBranchAddress("photonSieie", &photonSieie, &b_photonSieie);
   fChain->SetBranchAddress("photonSelBits", &photonSelBits, &b_photonSelBits);
   fChain->SetBranchAddress("photonChIso", &photonChIso, &b_photonChIso);
   fChain->SetBranchAddress("photonChIsoRC", &photonChIsoRC, &b_photonChIsoRC);
   fChain->SetBranchAddress("photonNhIso", &photonNhIso, &b_photonNhIso);
   fChain->SetBranchAddress("photonNhIsoRC", &photonNhIsoRC, &b_photonNhIsoRC);
   fChain->SetBranchAddress("photonPhoIso", &photonPhoIso, &b_photonPhoIso);
   fChain->SetBranchAddress("photonPhoIsoRC", &photonPhoIsoRC, &b_photonPhoIsoRC);
   fChain->SetBranchAddress("photonPuIso", &photonPuIso, &b_photonPuIso);
   fChain->SetBranchAddress("photonPuIsoRC", &photonPuIsoRC, &b_photonPuIsoRC);
   fChain->SetBranchAddress("genP4", &genP4, &b_genP4);
   fChain->SetBranchAddress("genjetP4", &genjetP4, &b_genjetP4);
   fChain->SetBranchAddress("genPdgId", &genPdgId, &b_genPdgId);
   fChain->SetBranchAddress("puTrueInt", &puTrueInt, &b_puTrueInt);
   fChain->SetBranchAddress("mcWeight", &mcWeight, &b_mcWeight);
   fChain->SetBranchAddress("pdfQscale", &pdfQscale, &b_pdfQscale);
   fChain->SetBranchAddress("pdfAlphaQED", &pdfAlphaQED, &b_pdfAlphaQED);
   fChain->SetBranchAddress("pdfAlphaQCD", &pdfAlphaQCD, &b_pdfAlphaQCD);
   fChain->SetBranchAddress("pdfX1", &pdfX1, &b_pdfX1);
   fChain->SetBranchAddress("pdfX2", &pdfX2, &b_pdfX2);
   fChain->SetBranchAddress("pdfId1", &pdfId1, &b_pdfId1);
   fChain->SetBranchAddress("pdfId2", &pdfId2, &b_pdfId2);
   fChain->SetBranchAddress("pdfScalePdf", &pdfScalePdf, &b_pdfScalePdf);
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("triggerPrescale", &triggerPrescale, &b_triggerPrescale);
   fChain->SetBranchAddress("triggerLeps", &triggerLeps, &b_triggerLeps);
   fChain->SetBranchAddress("triggerJets", &triggerJets, &b_triggerJets);
   fChain->SetBranchAddress("triggerTaus", &triggerTaus, &b_triggerTaus);
   fChain->SetBranchAddress("triggerPhotons", &triggerPhotons, &b_triggerPhotons);
   Notify();
}

Bool_t NeroTree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void NeroTree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t NeroTree::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
