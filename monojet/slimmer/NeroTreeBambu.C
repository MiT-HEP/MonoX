#define NeroTreeBambu_cxx
#include "NeroTreeBambu.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void NeroTreeBambu::Loop()
{
//   In a ROOT session, you can do:
//      root> .L NeroTreeBambu.C
//      root> NeroTreeBambu t
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

NeroTreeBambu::NeroTreeBambu(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../../../../../eos/cms/store/user/zdemirag/V0004/ttbarsync/nero_0000.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../../../../eos/cms/store/user/zdemirag/V0004/ttbarsync/nero_0000.root");
      }
      TDirectory * dir = (TDirectory*)f->Get("../../../../../eos/cms/store/user/zdemirag/V0004/ttbarsync/nero_0000.root:/nero");
      dir->GetObject("events",tree);

   }
   Init(tree);
}

NeroTreeBambu::~NeroTreeBambu()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t NeroTreeBambu::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t NeroTreeBambu::LoadTree(Long64_t entry)
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

void NeroTreeBambu::Init(TTree *tree)
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
   fatjetak8P4 = 0;
   fatjetak8RawPt = 0;
   fatjetak8Flavour = 0;
   fatjetak8Tau1 = 0;
   fatjetak8Tau2 = 0;
   fatjetak8Tau3 = 0;
   fatjetak8TrimmedMass = 0;
   fatjetak8PrunedMass = 0;
   fatjetak8FilteredMass = 0;
   fatjetak8SoftdropMass = 0;
   ak8_subjet = 0;
   ak8jet_hasSubjet = 0;
   ak8subjet_btag = 0;
   fatjetak8Hbb = 0;
   fatjetak8topMVA = 0;
   fatjetca15P4 = 0;
   fatjetca15RawPt = 0;
   fatjetca15Flavour = 0;
   fatjetca15Tau1 = 0;
   fatjetca15Tau2 = 0;
   fatjetca15Tau3 = 0;
   fatjetca15TrimmedMass = 0;
   fatjetca15PrunedMass = 0;
   fatjetca15FilteredMass = 0;
   fatjetca15SoftdropMass = 0;
   ca15_subjet = 0;
   ca15jet_hasSubjet = 0;
   ca15subjet_btag = 0;
   fatjetca15Hbb = 0;
   fatjetca15topMVA = 0;
   fatjetak8puppiP4 = 0;
   fatjetak8puppiRawPt = 0;
   fatjetak8puppiFlavour = 0;
   fatjetak8puppiTau1 = 0;
   fatjetak8puppiTau2 = 0;
   fatjetak8puppiTau3 = 0;
   fatjetak8puppiTrimmedMass = 0;
   fatjetak8puppiPrunedMass = 0;
   fatjetak8puppiFilteredMass = 0;
   fatjetak8puppiSoftdropMass = 0;
   ak8puppi_subjet = 0;
   ak8puppijet_hasSubjet = 0;
   ak8puppisubjet_btag = 0;
   fatjetak8puppiHbb = 0;
   fatjetak8puppitopMVA = 0;
   fatjetca15puppiP4 = 0;
   fatjetca15puppiRawPt = 0;
   fatjetca15puppiFlavour = 0;
   fatjetca15puppiTau1 = 0;
   fatjetca15puppiTau2 = 0;
   fatjetca15puppiTau3 = 0;
   fatjetca15puppiTrimmedMass = 0;
   fatjetca15puppiPrunedMass = 0;
   fatjetca15puppiFilteredMass = 0;
   fatjetca15puppiSoftdropMass = 0;
   ca15puppi_subjet = 0;
   ca15puppijet_hasSubjet = 0;
   ca15puppisubjet_btag = 0;
   fatjetca15puppiHbb = 0;
   fatjetca15puppitopMVA = 0;
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
   fChain->SetBranchAddress("fatjetak8P4", &fatjetak8P4, &b_fatjetak8P4);
   fChain->SetBranchAddress("fatjetak8RawPt", &fatjetak8RawPt, &b_fatjetak8RawPt);
   fChain->SetBranchAddress("fatjetak8Flavour", &fatjetak8Flavour, &b_fatjetak8Flavour);
   fChain->SetBranchAddress("fatjetak8Tau1", &fatjetak8Tau1, &b_fatjetak8Tau1);
   fChain->SetBranchAddress("fatjetak8Tau2", &fatjetak8Tau2, &b_fatjetak8Tau2);
   fChain->SetBranchAddress("fatjetak8Tau3", &fatjetak8Tau3, &b_fatjetak8Tau3);
   fChain->SetBranchAddress("fatjetak8TrimmedMass", &fatjetak8TrimmedMass, &b_fatjetak8TrimmedMass);
   fChain->SetBranchAddress("fatjetak8PrunedMass", &fatjetak8PrunedMass, &b_fatjetak8PrunedMass);
   fChain->SetBranchAddress("fatjetak8FilteredMass", &fatjetak8FilteredMass, &b_fatjetak8FilteredMass);
   fChain->SetBranchAddress("fatjetak8SoftdropMass", &fatjetak8SoftdropMass, &b_fatjetak8SoftdropMass);
   fChain->SetBranchAddress("ak8_subjet", &ak8_subjet, &b_ak8_subjet);
   fChain->SetBranchAddress("ak8jet_hasSubjet", &ak8jet_hasSubjet, &b_ak8jet_hasSubjet);
   fChain->SetBranchAddress("ak8subjet_btag", &ak8subjet_btag, &b_ak8subjet_btag);
   fChain->SetBranchAddress("fatjetak8Hbb", &fatjetak8Hbb, &b_fatjetak8Hbb);
   fChain->SetBranchAddress("fatjetak8topMVA", &fatjetak8topMVA, &b_fatjetak8topMVA);
   fChain->SetBranchAddress("fatjetca15P4", &fatjetca15P4, &b_fatjetca15P4);
   fChain->SetBranchAddress("fatjetca15RawPt", &fatjetca15RawPt, &b_fatjetca15RawPt);
   fChain->SetBranchAddress("fatjetca15Flavour", &fatjetca15Flavour, &b_fatjetca15Flavour);
   fChain->SetBranchAddress("fatjetca15Tau1", &fatjetca15Tau1, &b_fatjetca15Tau1);
   fChain->SetBranchAddress("fatjetca15Tau2", &fatjetca15Tau2, &b_fatjetca15Tau2);
   fChain->SetBranchAddress("fatjetca15Tau3", &fatjetca15Tau3, &b_fatjetca15Tau3);
   fChain->SetBranchAddress("fatjetca15TrimmedMass", &fatjetca15TrimmedMass, &b_fatjetca15TrimmedMass);
   fChain->SetBranchAddress("fatjetca15PrunedMass", &fatjetca15PrunedMass, &b_fatjetca15PrunedMass);
   fChain->SetBranchAddress("fatjetca15FilteredMass", &fatjetca15FilteredMass, &b_fatjetca15FilteredMass);
   fChain->SetBranchAddress("fatjetca15SoftdropMass", &fatjetca15SoftdropMass, &b_fatjetca15SoftdropMass);
   fChain->SetBranchAddress("ca15_subjet", &ca15_subjet, &b_ca15_subjet);
   fChain->SetBranchAddress("ca15jet_hasSubjet", &ca15jet_hasSubjet, &b_ca15jet_hasSubjet);
   fChain->SetBranchAddress("ca15subjet_btag", &ca15subjet_btag, &b_ca15subjet_btag);
   fChain->SetBranchAddress("fatjetca15Hbb", &fatjetca15Hbb, &b_fatjetca15Hbb);
   fChain->SetBranchAddress("fatjetca15topMVA", &fatjetca15topMVA, &b_fatjetca15topMVA);
   fChain->SetBranchAddress("fatjetak8puppiP4", &fatjetak8puppiP4, &b_fatjetak8puppiP4);
   fChain->SetBranchAddress("fatjetak8puppiRawPt", &fatjetak8puppiRawPt, &b_fatjetak8puppiRawPt);
   fChain->SetBranchAddress("fatjetak8puppiFlavour", &fatjetak8puppiFlavour, &b_fatjetak8puppiFlavour);
   fChain->SetBranchAddress("fatjetak8puppiTau1", &fatjetak8puppiTau1, &b_fatjetak8puppiTau1);
   fChain->SetBranchAddress("fatjetak8puppiTau2", &fatjetak8puppiTau2, &b_fatjetak8puppiTau2);
   fChain->SetBranchAddress("fatjetak8puppiTau3", &fatjetak8puppiTau3, &b_fatjetak8puppiTau3);
   fChain->SetBranchAddress("fatjetak8puppiTrimmedMass", &fatjetak8puppiTrimmedMass, &b_fatjetak8puppiTrimmedMass);
   fChain->SetBranchAddress("fatjetak8puppiPrunedMass", &fatjetak8puppiPrunedMass, &b_fatjetak8puppiPrunedMass);
   fChain->SetBranchAddress("fatjetak8puppiFilteredMass", &fatjetak8puppiFilteredMass, &b_fatjetak8puppiFilteredMass);
   fChain->SetBranchAddress("fatjetak8puppiSoftdropMass", &fatjetak8puppiSoftdropMass, &b_fatjetak8puppiSoftdropMass);
   fChain->SetBranchAddress("ak8puppi_subjet", &ak8puppi_subjet, &b_ak8puppi_subjet);
   fChain->SetBranchAddress("ak8puppijet_hasSubjet", &ak8puppijet_hasSubjet, &b_ak8puppijet_hasSubjet);
   fChain->SetBranchAddress("ak8puppisubjet_btag", &ak8puppisubjet_btag, &b_ak8puppisubjet_btag);
   fChain->SetBranchAddress("fatjetak8puppiHbb", &fatjetak8puppiHbb, &b_fatjetak8puppiHbb);
   fChain->SetBranchAddress("fatjetak8puppitopMVA", &fatjetak8puppitopMVA, &b_fatjetak8puppitopMVA);
   fChain->SetBranchAddress("fatjetca15puppiP4", &fatjetca15puppiP4, &b_fatjetca15puppiP4);
   fChain->SetBranchAddress("fatjetca15puppiRawPt", &fatjetca15puppiRawPt, &b_fatjetca15puppiRawPt);
   fChain->SetBranchAddress("fatjetca15puppiFlavour", &fatjetca15puppiFlavour, &b_fatjetca15puppiFlavour);
   fChain->SetBranchAddress("fatjetca15puppiTau1", &fatjetca15puppiTau1, &b_fatjetca15puppiTau1);
   fChain->SetBranchAddress("fatjetca15puppiTau2", &fatjetca15puppiTau2, &b_fatjetca15puppiTau2);
   fChain->SetBranchAddress("fatjetca15puppiTau3", &fatjetca15puppiTau3, &b_fatjetca15puppiTau3);
   fChain->SetBranchAddress("fatjetca15puppiTrimmedMass", &fatjetca15puppiTrimmedMass, &b_fatjetca15puppiTrimmedMass);
   fChain->SetBranchAddress("fatjetca15puppiPrunedMass", &fatjetca15puppiPrunedMass, &b_fatjetca15puppiPrunedMass);
   fChain->SetBranchAddress("fatjetca15puppiFilteredMass", &fatjetca15puppiFilteredMass, &b_fatjetca15puppiFilteredMass);
   fChain->SetBranchAddress("fatjetca15puppiSoftdropMass", &fatjetca15puppiSoftdropMass, &b_fatjetca15puppiSoftdropMass);
   fChain->SetBranchAddress("ca15puppi_subjet", &ca15puppi_subjet, &b_ca15puppi_subjet);
   fChain->SetBranchAddress("ca15puppijet_hasSubjet", &ca15puppijet_hasSubjet, &b_ca15puppijet_hasSubjet);
   fChain->SetBranchAddress("ca15puppisubjet_btag", &ca15puppisubjet_btag, &b_ca15puppisubjet_btag);
   fChain->SetBranchAddress("fatjetca15puppiHbb", &fatjetca15puppiHbb, &b_fatjetca15puppiHbb);
   fChain->SetBranchAddress("fatjetca15puppitopMVA", &fatjetca15puppitopMVA, &b_fatjetca15puppitopMVA);
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
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("triggerPrescale", &triggerPrescale, &b_triggerPrescale);
   fChain->SetBranchAddress("triggerLeps", &triggerLeps, &b_triggerLeps);
   fChain->SetBranchAddress("triggerJets", &triggerJets, &b_triggerJets);
   fChain->SetBranchAddress("triggerTaus", &triggerTaus, &b_triggerTaus);
   fChain->SetBranchAddress("triggerPhotons", &triggerPhotons, &b_triggerPhotons);
   fChain->SetBranchAddress("npv", &npv, &b_npv);
   Notify();
}

Bool_t NeroTreeBambu::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void NeroTreeBambu::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t NeroTreeBambu::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
