#define NeroTree76_cxx
#include "NeroTree76.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void NeroTree76::Loop()
{
//   In a ROOT session, you can do:
//      root> .L NeroTree76.C
//      root> NeroTree76 t
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

NeroTree76::NeroTree76(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("/scratch5/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("/scratch5/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root");
      }
      TDirectory * dir = (TDirectory*)f->Get("/scratch5/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root:/nero");
      dir->GetObject("events",tree);

   }
   Init(tree);
}

NeroTree76::~NeroTree76()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t NeroTree76::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t NeroTree76::LoadTree(Long64_t entry)
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

void NeroTree76::Init(TTree *tree)
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
   jetpuppiP4 = 0;
   jetpuppiRawPt = 0;
   jetpuppiBdiscr = 0;
   jetpuppiBdiscrLegacy = 0;
   jetpuppiPuId = 0;
   jetpuppiUnc = 0;
   jetpuppiQGL = 0;
   jetpuppiFlavour = 0;
   jetpuppiMatchedPartonPdgId = 0;
   jetpuppiMotherPdgId = 0;
   jetpuppiGrMotherPdgId = 0;
   jetpuppiSelBits = 0;
   jetpuppiQ = 0;
   jetpuppiQnoPU = 0;
   fatjetAK8CHSP4 = 0;
   fatjetAK8CHSRawPt = 0;
   fatjetAK8CHSFlavour = 0;
   fatjetAK8CHSTau1 = 0;
   fatjetAK8CHSTau2 = 0;
   fatjetAK8CHSTau3 = 0;
   fatjetAK8CHSTrimmedMass = 0;
   fatjetAK8CHSPrunedMass = 0;
   fatjetAK8CHSFilteredMass = 0;
   fatjetAK8CHSSoftdropMass = 0;
   fatjetAK8CHSsubjet = 0;
   fatjetAK8CHSnSubjets = 0;
   fatjetAK8CHSfirstSubjet = 0;
   fatjetAK8CHSsubjet_btag = 0;
   fatjetAK8CHSHbb = 0;
   fatjetAK8CHStopMVA = 0;
   fatjetCA15CHSP4 = 0;
   fatjetCA15CHSRawPt = 0;
   fatjetCA15CHSFlavour = 0;
   fatjetCA15CHSTau1 = 0;
   fatjetCA15CHSTau2 = 0;
   fatjetCA15CHSTau3 = 0;
   fatjetCA15CHSTrimmedMass = 0;
   fatjetCA15CHSPrunedMass = 0;
   fatjetCA15CHSFilteredMass = 0;
   fatjetCA15CHSSoftdropMass = 0;
   fatjetCA15CHSsubjet = 0;
   fatjetCA15CHSnSubjets = 0;
   fatjetCA15CHSfirstSubjet = 0;
   fatjetCA15CHSsubjet_btag = 0;
   fatjetCA15CHSHbb = 0;
   fatjetCA15CHStopMVA = 0;
   fatjetAK8PuppiP4 = 0;
   fatjetAK8PuppiRawPt = 0;
   fatjetAK8PuppiFlavour = 0;
   fatjetAK8PuppiTau1 = 0;
   fatjetAK8PuppiTau2 = 0;
   fatjetAK8PuppiTau3 = 0;
   fatjetAK8PuppiTrimmedMass = 0;
   fatjetAK8PuppiPrunedMass = 0;
   fatjetAK8PuppiFilteredMass = 0;
   fatjetAK8PuppiSoftdropMass = 0;
   fatjetAK8Puppisubjet = 0;
   fatjetAK8PuppinSubjets = 0;
   fatjetAK8PuppifirstSubjet = 0;
   fatjetAK8Puppisubjet_btag = 0;
   fatjetAK8PuppiHbb = 0;
   fatjetAK8PuppitopMVA = 0;
   fatjetCA15PuppiP4 = 0;
   fatjetCA15PuppiRawPt = 0;
   fatjetCA15PuppiFlavour = 0;
   fatjetCA15PuppiTau1 = 0;
   fatjetCA15PuppiTau2 = 0;
   fatjetCA15PuppiTau3 = 0;
   fatjetCA15PuppiTrimmedMass = 0;
   fatjetCA15PuppiPrunedMass = 0;
   fatjetCA15PuppiFilteredMass = 0;
   fatjetCA15PuppiSoftdropMass = 0;
   fatjetCA15Puppisubjet = 0;
   fatjetCA15PuppinSubjets = 0;
   fatjetCA15PuppifirstSubjet = 0;
   fatjetCA15Puppisubjet_btag = 0;
   fatjetCA15PuppiHbb = 0;
   fatjetCA15PuppitopMVA = 0;
   lepP4 = 0;
   lepPdgId = 0;
   lepIso = 0;
   lepSelBits = 0;
   lepPfPt = 0;
   lepChIso = 0;
   lepNhIso = 0;
   lepPhoIso = 0;
   lepPuIso = 0;
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
   genP4 = 0;
   genjetP4 = 0;
   genPdgId = 0;
   genFlags = 0;
   pdfRwgt = 0;
   genIso = 0;
   genIsoFrixione = 0;
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
   photonRawPt = 0;
   photonR9 = 0;
   tauP4 = 0;
   tauSelBits = 0;
   tauQ = 0;
   tauM = 0;
   tauIso = 0;
   tauChargedIsoPtSum = 0;
   tauNeutralIsoPtSum = 0;
   tauIsoDeltaBetaCorr = 0;
   tauIsoPileupWeightedRaw = 0;
   triggerFired = 0;
   triggerPrescale = 0;
   triggerLeps = 0;
   triggerJets = 0;
   triggerTaus = 0;
   triggerPhotons = 0;
   triggerNoneTaus = 0;
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
   fChain->SetBranchAddress("jetP4", &jetP4, &b_jetP4);
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
   fChain->SetBranchAddress("jetpuppiP4", &jetpuppiP4, &b_jetpuppiP4);
   fChain->SetBranchAddress("jetpuppiRawPt", &jetpuppiRawPt, &b_jetpuppiRawPt);
   fChain->SetBranchAddress("jetpuppiBdiscr", &jetpuppiBdiscr, &b_jetpuppiBdiscr);
   fChain->SetBranchAddress("jetpuppiBdiscrLegacy", &jetpuppiBdiscrLegacy, &b_jetpuppiBdiscrLegacy);
   fChain->SetBranchAddress("jetpuppiPuId", &jetpuppiPuId, &b_jetpuppiPuId);
   fChain->SetBranchAddress("jetpuppiUnc", &jetpuppiUnc, &b_jetpuppiUnc);
   fChain->SetBranchAddress("jetpuppiQGL", &jetpuppiQGL, &b_jetpuppiQGL);
   fChain->SetBranchAddress("jetpuppiFlavour", &jetpuppiFlavour, &b_jetpuppiFlavour);
   fChain->SetBranchAddress("jetpuppiMatchedPartonPdgId", &jetpuppiMatchedPartonPdgId, &b_jetpuppiMatchedPartonPdgId);
   fChain->SetBranchAddress("jetpuppiMotherPdgId", &jetpuppiMotherPdgId, &b_jetpuppiMotherPdgId);
   fChain->SetBranchAddress("jetpuppiGrMotherPdgId", &jetpuppiGrMotherPdgId, &b_jetpuppiGrMotherPdgId);
   fChain->SetBranchAddress("jetpuppiSelBits", &jetpuppiSelBits, &b_jetpuppiSelBits);
   fChain->SetBranchAddress("jetpuppiQ", &jetpuppiQ, &b_jetpuppiQ);
   fChain->SetBranchAddress("jetpuppiQnoPU", &jetpuppiQnoPU, &b_jetpuppiQnoPU);
   fChain->SetBranchAddress("fatjetAK8CHSP4", &fatjetAK8CHSP4, &b_fatjetAK8CHSP4);
   fChain->SetBranchAddress("fatjetAK8CHSRawPt", &fatjetAK8CHSRawPt, &b_fatjetAK8CHSRawPt);
   fChain->SetBranchAddress("fatjetAK8CHSFlavour", &fatjetAK8CHSFlavour, &b_fatjetAK8CHSFlavour);
   fChain->SetBranchAddress("fatjetAK8CHSTau1", &fatjetAK8CHSTau1, &b_fatjetAK8CHSTau1);
   fChain->SetBranchAddress("fatjetAK8CHSTau2", &fatjetAK8CHSTau2, &b_fatjetAK8CHSTau2);
   fChain->SetBranchAddress("fatjetAK8CHSTau3", &fatjetAK8CHSTau3, &b_fatjetAK8CHSTau3);
   fChain->SetBranchAddress("fatjetAK8CHSTrimmedMass", &fatjetAK8CHSTrimmedMass, &b_fatjetAK8CHSTrimmedMass);
   fChain->SetBranchAddress("fatjetAK8CHSPrunedMass", &fatjetAK8CHSPrunedMass, &b_fatjetAK8CHSPrunedMass);
   fChain->SetBranchAddress("fatjetAK8CHSFilteredMass", &fatjetAK8CHSFilteredMass, &b_fatjetAK8CHSFilteredMass);
   fChain->SetBranchAddress("fatjetAK8CHSSoftdropMass", &fatjetAK8CHSSoftdropMass, &b_fatjetAK8CHSSoftdropMass);
   fChain->SetBranchAddress("fatjetAK8CHSsubjet", &fatjetAK8CHSsubjet, &b_fatjetAK8CHSsubjet);
   fChain->SetBranchAddress("fatjetAK8CHSnSubjets", &fatjetAK8CHSnSubjets, &b_fatjetAK8CHSnSubjets);
   fChain->SetBranchAddress("fatjetAK8CHSfirstSubjet", &fatjetAK8CHSfirstSubjet, &b_fatjetAK8CHSfirstSubjet);
   fChain->SetBranchAddress("fatjetAK8CHSsubjet_btag", &fatjetAK8CHSsubjet_btag, &b_fatjetAK8CHSsubjet_btag);
   fChain->SetBranchAddress("fatjetAK8CHSHbb", &fatjetAK8CHSHbb, &b_fatjetAK8CHSHbb);
   fChain->SetBranchAddress("fatjetAK8CHStopMVA", &fatjetAK8CHStopMVA, &b_fatjetAK8CHStopMVA);
   fChain->SetBranchAddress("fatjetCA15CHSP4", &fatjetCA15CHSP4, &b_fatjetCA15CHSP4);
   fChain->SetBranchAddress("fatjetCA15CHSRawPt", &fatjetCA15CHSRawPt, &b_fatjetCA15CHSRawPt);
   fChain->SetBranchAddress("fatjetCA15CHSFlavour", &fatjetCA15CHSFlavour, &b_fatjetCA15CHSFlavour);
   fChain->SetBranchAddress("fatjetCA15CHSTau1", &fatjetCA15CHSTau1, &b_fatjetCA15CHSTau1);
   fChain->SetBranchAddress("fatjetCA15CHSTau2", &fatjetCA15CHSTau2, &b_fatjetCA15CHSTau2);
   fChain->SetBranchAddress("fatjetCA15CHSTau3", &fatjetCA15CHSTau3, &b_fatjetCA15CHSTau3);
   fChain->SetBranchAddress("fatjetCA15CHSTrimmedMass", &fatjetCA15CHSTrimmedMass, &b_fatjetCA15CHSTrimmedMass);
   fChain->SetBranchAddress("fatjetCA15CHSPrunedMass", &fatjetCA15CHSPrunedMass, &b_fatjetCA15CHSPrunedMass);
   fChain->SetBranchAddress("fatjetCA15CHSFilteredMass", &fatjetCA15CHSFilteredMass, &b_fatjetCA15CHSFilteredMass);
   fChain->SetBranchAddress("fatjetCA15CHSSoftdropMass", &fatjetCA15CHSSoftdropMass, &b_fatjetCA15CHSSoftdropMass);
   fChain->SetBranchAddress("fatjetCA15CHSsubjet", &fatjetCA15CHSsubjet, &b_fatjetCA15CHSsubjet);
   fChain->SetBranchAddress("fatjetCA15CHSnSubjets", &fatjetCA15CHSnSubjets, &b_fatjetCA15CHSnSubjets);
   fChain->SetBranchAddress("fatjetCA15CHSfirstSubjet", &fatjetCA15CHSfirstSubjet, &b_fatjetCA15CHSfirstSubjet);
   fChain->SetBranchAddress("fatjetCA15CHSsubjet_btag", &fatjetCA15CHSsubjet_btag, &b_fatjetCA15CHSsubjet_btag);
   fChain->SetBranchAddress("fatjetCA15CHSHbb", &fatjetCA15CHSHbb, &b_fatjetCA15CHSHbb);
   fChain->SetBranchAddress("fatjetCA15CHStopMVA", &fatjetCA15CHStopMVA, &b_fatjetCA15CHStopMVA);
   fChain->SetBranchAddress("fatjetAK8PuppiP4", &fatjetAK8PuppiP4, &b_fatjetAK8PuppiP4);
   fChain->SetBranchAddress("fatjetAK8PuppiRawPt", &fatjetAK8PuppiRawPt, &b_fatjetAK8PuppiRawPt);
   fChain->SetBranchAddress("fatjetAK8PuppiFlavour", &fatjetAK8PuppiFlavour, &b_fatjetAK8PuppiFlavour);
   fChain->SetBranchAddress("fatjetAK8PuppiTau1", &fatjetAK8PuppiTau1, &b_fatjetAK8PuppiTau1);
   fChain->SetBranchAddress("fatjetAK8PuppiTau2", &fatjetAK8PuppiTau2, &b_fatjetAK8PuppiTau2);
   fChain->SetBranchAddress("fatjetAK8PuppiTau3", &fatjetAK8PuppiTau3, &b_fatjetAK8PuppiTau3);
   fChain->SetBranchAddress("fatjetAK8PuppiTrimmedMass", &fatjetAK8PuppiTrimmedMass, &b_fatjetAK8PuppiTrimmedMass);
   fChain->SetBranchAddress("fatjetAK8PuppiPrunedMass", &fatjetAK8PuppiPrunedMass, &b_fatjetAK8PuppiPrunedMass);
   fChain->SetBranchAddress("fatjetAK8PuppiFilteredMass", &fatjetAK8PuppiFilteredMass, &b_fatjetAK8PuppiFilteredMass);
   fChain->SetBranchAddress("fatjetAK8PuppiSoftdropMass", &fatjetAK8PuppiSoftdropMass, &b_fatjetAK8PuppiSoftdropMass);
   fChain->SetBranchAddress("fatjetAK8Puppisubjet", &fatjetAK8Puppisubjet, &b_fatjetAK8Puppisubjet);
   fChain->SetBranchAddress("fatjetAK8PuppinSubjets", &fatjetAK8PuppinSubjets, &b_fatjetAK8PuppinSubjets);
   fChain->SetBranchAddress("fatjetAK8PuppifirstSubjet", &fatjetAK8PuppifirstSubjet, &b_fatjetAK8PuppifirstSubjet);
   fChain->SetBranchAddress("fatjetAK8Puppisubjet_btag", &fatjetAK8Puppisubjet_btag, &b_fatjetAK8Puppisubjet_btag);
   fChain->SetBranchAddress("fatjetAK8PuppiHbb", &fatjetAK8PuppiHbb, &b_fatjetAK8PuppiHbb);
   fChain->SetBranchAddress("fatjetAK8PuppitopMVA", &fatjetAK8PuppitopMVA, &b_fatjetAK8PuppitopMVA);
   fChain->SetBranchAddress("fatjetCA15PuppiP4", &fatjetCA15PuppiP4, &b_fatjetCA15PuppiP4);
   fChain->SetBranchAddress("fatjetCA15PuppiRawPt", &fatjetCA15PuppiRawPt, &b_fatjetCA15PuppiRawPt);
   fChain->SetBranchAddress("fatjetCA15PuppiFlavour", &fatjetCA15PuppiFlavour, &b_fatjetCA15PuppiFlavour);
   fChain->SetBranchAddress("fatjetCA15PuppiTau1", &fatjetCA15PuppiTau1, &b_fatjetCA15PuppiTau1);
   fChain->SetBranchAddress("fatjetCA15PuppiTau2", &fatjetCA15PuppiTau2, &b_fatjetCA15PuppiTau2);
   fChain->SetBranchAddress("fatjetCA15PuppiTau3", &fatjetCA15PuppiTau3, &b_fatjetCA15PuppiTau3);
   fChain->SetBranchAddress("fatjetCA15PuppiTrimmedMass", &fatjetCA15PuppiTrimmedMass, &b_fatjetCA15PuppiTrimmedMass);
   fChain->SetBranchAddress("fatjetCA15PuppiPrunedMass", &fatjetCA15PuppiPrunedMass, &b_fatjetCA15PuppiPrunedMass);
   fChain->SetBranchAddress("fatjetCA15PuppiFilteredMass", &fatjetCA15PuppiFilteredMass, &b_fatjetCA15PuppiFilteredMass);
   fChain->SetBranchAddress("fatjetCA15PuppiSoftdropMass", &fatjetCA15PuppiSoftdropMass, &b_fatjetCA15PuppiSoftdropMass);
   fChain->SetBranchAddress("fatjetCA15Puppisubjet", &fatjetCA15Puppisubjet, &b_fatjetCA15Puppisubjet);
   fChain->SetBranchAddress("fatjetCA15PuppinSubjets", &fatjetCA15PuppinSubjets, &b_fatjetCA15PuppinSubjets);
   fChain->SetBranchAddress("fatjetCA15PuppifirstSubjet", &fatjetCA15PuppifirstSubjet, &b_fatjetCA15PuppifirstSubjet);
   fChain->SetBranchAddress("fatjetCA15Puppisubjet_btag", &fatjetCA15Puppisubjet_btag, &b_fatjetCA15Puppisubjet_btag);
   fChain->SetBranchAddress("fatjetCA15PuppiHbb", &fatjetCA15PuppiHbb, &b_fatjetCA15PuppiHbb);
   fChain->SetBranchAddress("fatjetCA15PuppitopMVA", &fatjetCA15PuppitopMVA, &b_fatjetCA15PuppitopMVA);
   fChain->SetBranchAddress("lepP4", &lepP4, &b_lepP4);
   fChain->SetBranchAddress("lepPdgId", &lepPdgId, &b_lepPdgId);
   fChain->SetBranchAddress("lepIso", &lepIso, &b_lepIso);
   fChain->SetBranchAddress("lepSelBits", &lepSelBits, &b_lepSelBits);
   fChain->SetBranchAddress("lepPfPt", &lepPfPt, &b_lepPfPt);
   fChain->SetBranchAddress("lepChIso", &lepChIso, &b_lepChIso);
   fChain->SetBranchAddress("lepNhIso", &lepNhIso, &b_lepNhIso);
   fChain->SetBranchAddress("lepPhoIso", &lepPhoIso, &b_lepPhoIso);
   fChain->SetBranchAddress("lepPuIso", &lepPuIso, &b_lepPuIso);
   fChain->SetBranchAddress("metP4", &metP4, &b_metP4);
   fChain->SetBranchAddress("metSumEtRaw", &metSumEtRaw, &b_metSumEtRaw);
   fChain->SetBranchAddress("metPtJESUP", &metPtJESUP, &b_metPtJESUP);
   fChain->SetBranchAddress("metPtJESDOWN", &metPtJESDOWN, &b_metPtJESDOWN);
   fChain->SetBranchAddress("metP4_GEN", &metP4_GEN, &b_metP4_GEN);
   fChain->SetBranchAddress("metPuppi", &metPuppi, &b_metPuppi);
   fChain->SetBranchAddress("metPuppiSyst", &metPuppiSyst, &b_metPuppiSyst);
   fChain->SetBranchAddress("metSumEtRawPuppi", &metSumEtRawPuppi, &b_metSumEtRawPuppi);
   fChain->SetBranchAddress("metNoMu", &metNoMu, &b_metNoMu);
   fChain->SetBranchAddress("metNoHF", &metNoHF, &b_metNoHF);
   fChain->SetBranchAddress("metSumEtRawNoHF", &metSumEtRawNoHF, &b_metSumEtRawNoHF);
   fChain->SetBranchAddress("pfMet_e3p0", &pfMet_e3p0, &b_pfMet_e3p0);
   fChain->SetBranchAddress("trackMet", &trackMet, &b_trackMet);
   fChain->SetBranchAddress("caloMet_Pt", &caloMet_Pt, &b_caloMet_Pt);
   fChain->SetBranchAddress("caloMet_Phi", &caloMet_Phi, &b_caloMet_Phi);
   fChain->SetBranchAddress("caloMet_SumEt", &caloMet_SumEt, &b_caloMet_SumEt);
   fChain->SetBranchAddress("rawMet_Pt", &rawMet_Pt, &b_rawMet_Pt);
   fChain->SetBranchAddress("rawMet_Phi", &rawMet_Phi, &b_rawMet_Phi);
   fChain->SetBranchAddress("genP4", &genP4, &b_genP4);
   fChain->SetBranchAddress("genjetP4", &genjetP4, &b_genjetP4);
   fChain->SetBranchAddress("genPdgId", &genPdgId, &b_genPdgId);
   fChain->SetBranchAddress("genFlags", &genFlags, &b_genFlags);
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
   fChain->SetBranchAddress("r2f1", &r2f1, &b_r2f1);
   fChain->SetBranchAddress("r5f1", &r5f1, &b_r5f1);
   fChain->SetBranchAddress("r1f2", &r1f2, &b_r1f2);
   fChain->SetBranchAddress("r2f2", &r2f2, &b_r2f2);
   fChain->SetBranchAddress("r1f5", &r1f5, &b_r1f5);
   fChain->SetBranchAddress("r5f5", &r5f5, &b_r5f5);
   fChain->SetBranchAddress("pdfRwgt", &pdfRwgt, &b_pdfRwgt);
   fChain->SetBranchAddress("genIso", &genIso, &b_genIso);
   fChain->SetBranchAddress("genIsoFrixione", &genIsoFrixione, &b_genIsoFrixione);
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
   fChain->SetBranchAddress("photonRawPt", &photonRawPt, &b_photonRawPt);
   fChain->SetBranchAddress("photonR9", &photonR9, &b_photonR9);
   fChain->SetBranchAddress("tauP4", &tauP4, &b_tauP4);
   fChain->SetBranchAddress("tauSelBits", &tauSelBits, &b_tauSelBits);
   fChain->SetBranchAddress("tauQ", &tauQ, &b_tauQ);
   fChain->SetBranchAddress("tauM", &tauM, &b_tauM);
   fChain->SetBranchAddress("tauIso", &tauIso, &b_tauIso);
   fChain->SetBranchAddress("tauChargedIsoPtSum", &tauChargedIsoPtSum, &b_tauChargedIsoPtSum);
   fChain->SetBranchAddress("tauNeutralIsoPtSum", &tauNeutralIsoPtSum, &b_tauNeutralIsoPtSum);
   fChain->SetBranchAddress("tauIsoDeltaBetaCorr", &tauIsoDeltaBetaCorr, &b_tauIsoDeltaBetaCorr);
   fChain->SetBranchAddress("tauIsoPileupWeightedRaw", &tauIsoPileupWeightedRaw, &b_tauIsoPileupWeightedRaw);
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("triggerPrescale", &triggerPrescale, &b_triggerPrescale);
   fChain->SetBranchAddress("triggerLeps", &triggerLeps, &b_triggerLeps);
   fChain->SetBranchAddress("triggerJets", &triggerJets, &b_triggerJets);
   fChain->SetBranchAddress("triggerTaus", &triggerTaus, &b_triggerTaus);
   fChain->SetBranchAddress("triggerPhotons", &triggerPhotons, &b_triggerPhotons);
   fChain->SetBranchAddress("triggerNoneTaus", &triggerNoneTaus, &b_triggerNoneTaus);
   fChain->SetBranchAddress("npv", &npv, &b_npv);
   Notify();
}

Bool_t NeroTree76::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void NeroTree76::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t NeroTree76::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
