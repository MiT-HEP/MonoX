//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Thu Jan 14 16:31:32 2016 by ROOT version 6.02/13
// from TTree events/events
// found on file: ../../../../../eos/cms/store/user/zdemirag/V0004/ttbarsync/nero_0000.root
//////////////////////////////////////////////////////////

#ifndef NeroTreeBambu_h
#define NeroTreeBambu_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include "TClonesArray.h"
#include "vector"
#include "vector"
#include "vector"
#include "TLorentzVector.h"

class NeroTreeBambu {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Int_t           isRealData;
   Int_t           runNum;
   Int_t           lumiNum;
   ULong64_t       eventNum;
   Float_t         rho;
   TClonesArray    *jetP4;
   vector<float>   *jetRawPt;
   vector<float>   *jetBdiscr;
   vector<float>   *jetBdiscrLegacy;
   vector<float>   *jetPuId;
   vector<float>   *jetUnc;
   vector<float>   *jetQGL;
   vector<int>     *jetFlavour;
   vector<int>     *jetMatchedPartonPdgId;
   vector<int>     *jetMotherPdgId;
   vector<int>     *jetGrMotherPdgId;
   vector<unsigned int> *jetSelBits;
   vector<float>   *jetQ;
   vector<float>   *jetQnoPU;
   TClonesArray    *jetpuppiP4;
   vector<float>   *jetpuppiRawPt;
   vector<float>   *jetpuppiBdiscr;
   vector<float>   *jetpuppiBdiscrLegacy;
   vector<float>   *jetpuppiPuId;
   vector<float>   *jetpuppiUnc;
   vector<float>   *jetpuppiQGL;
   vector<int>     *jetpuppiFlavour;
   vector<int>     *jetpuppiMatchedPartonPdgId;
   vector<int>     *jetpuppiMotherPdgId;
   vector<int>     *jetpuppiGrMotherPdgId;
   vector<unsigned int> *jetpuppiSelBits;
   vector<float>   *jetpuppiQ;
   vector<float>   *jetpuppiQnoPU;
   TClonesArray    *fatjetak8P4;
   vector<float>   *fatjetak8RawPt;
   vector<int>     *fatjetak8Flavour;
   vector<float>   *fatjetak8Tau1;
   vector<float>   *fatjetak8Tau2;
   vector<float>   *fatjetak8Tau3;
   vector<float>   *fatjetak8TrimmedMass;
   vector<float>   *fatjetak8PrunedMass;
   vector<float>   *fatjetak8FilteredMass;
   vector<float>   *fatjetak8SoftdropMass;
   TClonesArray    *ak8_subjet;
   vector<int>     *ak8jet_hasSubjet;
   vector<float>   *ak8subjet_btag;
   vector<float>   *fatjetak8Hbb;
   vector<float>   *fatjetak8topMVA;
   TClonesArray    *fatjetca15P4;
   vector<float>   *fatjetca15RawPt;
   vector<int>     *fatjetca15Flavour;
   vector<float>   *fatjetca15Tau1;
   vector<float>   *fatjetca15Tau2;
   vector<float>   *fatjetca15Tau3;
   vector<float>   *fatjetca15TrimmedMass;
   vector<float>   *fatjetca15PrunedMass;
   vector<float>   *fatjetca15FilteredMass;
   vector<float>   *fatjetca15SoftdropMass;
   TClonesArray    *ca15_subjet;
   vector<int>     *ca15jet_hasSubjet;
   vector<float>   *ca15subjet_btag;
   vector<float>   *fatjetca15Hbb;
   vector<float>   *fatjetca15topMVA;
   TClonesArray    *fatjetak8puppiP4;
   vector<float>   *fatjetak8puppiRawPt;
   vector<int>     *fatjetak8puppiFlavour;
   vector<float>   *fatjetak8puppiTau1;
   vector<float>   *fatjetak8puppiTau2;
   vector<float>   *fatjetak8puppiTau3;
   vector<float>   *fatjetak8puppiTrimmedMass;
   vector<float>   *fatjetak8puppiPrunedMass;
   vector<float>   *fatjetak8puppiFilteredMass;
   vector<float>   *fatjetak8puppiSoftdropMass;
   TClonesArray    *ak8puppi_subjet;
   vector<int>     *ak8puppijet_hasSubjet;
   vector<float>   *ak8puppisubjet_btag;
   vector<float>   *fatjetak8puppiHbb;
   vector<float>   *fatjetak8puppitopMVA;
   TClonesArray    *fatjetca15puppiP4;
   vector<float>   *fatjetca15puppiRawPt;
   vector<int>     *fatjetca15puppiFlavour;
   vector<float>   *fatjetca15puppiTau1;
   vector<float>   *fatjetca15puppiTau2;
   vector<float>   *fatjetca15puppiTau3;
   vector<float>   *fatjetca15puppiTrimmedMass;
   vector<float>   *fatjetca15puppiPrunedMass;
   vector<float>   *fatjetca15puppiFilteredMass;
   vector<float>   *fatjetca15puppiSoftdropMass;
   TClonesArray    *ca15puppi_subjet;
   vector<int>     *ca15puppijet_hasSubjet;
   vector<float>   *ca15puppisubjet_btag;
   vector<float>   *fatjetca15puppiHbb;
   vector<float>   *fatjetca15puppitopMVA;
   TClonesArray    *lepP4;
   vector<int>     *lepPdgId;
   vector<float>   *lepIso;
   vector<unsigned int> *lepSelBits;
   vector<float>   *lepPfPt;
   vector<float>   *lepChIso;
   vector<float>   *lepNhIso;
   vector<float>   *lepPhoIso;
   vector<float>   *lepPuIso;
   TClonesArray    *metP4;
   Float_t         metSumEtRaw;
   vector<float>   *metPtJESUP;
   vector<float>   *metPtJESDOWN;
   TClonesArray    *metP4_GEN;
   TLorentzVector  *metPuppi;
   TClonesArray    *metPuppiSyst;
   Float_t         metSumEtRawPuppi;
   TLorentzVector  *metNoMu;
   TLorentzVector  *metNoHF;
   Float_t         metSumEtRawNoHF;
   TLorentzVector  *pfMet_e3p0;
   TLorentzVector  *trackMet;
   Float_t         caloMet_Pt;
   Float_t         caloMet_Phi;
   Float_t         caloMet_SumEt;
   TClonesArray    *genP4;
   TClonesArray    *genjetP4;
   vector<int>     *genPdgId;
   vector<unsigned int> *genFlags;
   Int_t           puTrueInt;
   Float_t         mcWeight;
   Float_t         pdfQscale;
   Float_t         pdfAlphaQED;
   Float_t         pdfAlphaQCD;
   Float_t         pdfX1;
   Float_t         pdfX2;
   Int_t           pdfId1;
   Int_t           pdfId2;
   Float_t         pdfScalePdf;
   Float_t         r2f1;
   Float_t         r5f1;
   Float_t         r1f2;
   Float_t         r2f2;
   Float_t         r1f5;
   Float_t         r5f5;
   vector<float>   *pdfRwgt;
   vector<float>   *genIso;
   vector<float>   *genIsoFrixione;
   TClonesArray    *photonP4;
   vector<float>   *photonIso;
   vector<float>   *photonSieie;
   vector<unsigned int> *photonSelBits;
   vector<float>   *photonChIso;
   vector<float>   *photonChIsoRC;
   vector<float>   *photonNhIso;
   vector<float>   *photonNhIsoRC;
   vector<float>   *photonPhoIso;
   vector<float>   *photonPhoIsoRC;
   vector<float>   *photonPuIso;
   vector<float>   *photonPuIsoRC;
   vector<float>   *photonRawPt;
   vector<float>   *photonR9;
   TClonesArray    *tauP4;
   vector<unsigned int> *tauSelBits;
   vector<int>     *tauQ;
   vector<float>   *tauM;
   vector<float>   *tauIso;
   vector<float>   *tauChargedIsoPtSum;
   vector<float>   *tauNeutralIsoPtSum;
   vector<float>   *tauIsoDeltaBetaCorr;
   vector<int>     *triggerFired;
   vector<float>   *triggerPrescale;
   vector<int>     *triggerLeps;
   vector<int>     *triggerJets;
   vector<int>     *triggerTaus;
   vector<int>     *triggerPhotons;
   Int_t           npv;

   // List of branches
   TBranch        *b_isRealData;   //!
   TBranch        *b_runNum;   //!
   TBranch        *b_lumiNum;   //!
   TBranch        *b_eventNum;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_jetP4;   //!
   TBranch        *b_jetRawPt;   //!
   TBranch        *b_jetBdiscr;   //!
   TBranch        *b_jetBdiscrLegacy;   //!
   TBranch        *b_jetPuId;   //!
   TBranch        *b_jetUnc;   //!
   TBranch        *b_jetQGL;   //!
   TBranch        *b_jetFlavour;   //!
   TBranch        *b_jetMatchedPartonPdgId;   //!
   TBranch        *b_jetMotherPdgId;   //!
   TBranch        *b_jetGrMotherPdgId;   //!
   TBranch        *b_jetSelBits;   //!
   TBranch        *b_jetQ;   //!
   TBranch        *b_jetQnoPU;   //!
   TBranch        *b_jetpuppiP4;   //!
   TBranch        *b_jetpuppiRawPt;   //!
   TBranch        *b_jetpuppiBdiscr;   //!
   TBranch        *b_jetpuppiBdiscrLegacy;   //!
   TBranch        *b_jetpuppiPuId;   //!
   TBranch        *b_jetpuppiUnc;   //!
   TBranch        *b_jetpuppiQGL;   //!
   TBranch        *b_jetpuppiFlavour;   //!
   TBranch        *b_jetpuppiMatchedPartonPdgId;   //!
   TBranch        *b_jetpuppiMotherPdgId;   //!
   TBranch        *b_jetpuppiGrMotherPdgId;   //!
   TBranch        *b_jetpuppiSelBits;   //!
   TBranch        *b_jetpuppiQ;   //!
   TBranch        *b_jetpuppiQnoPU;   //!
   TBranch        *b_fatjetak8P4;   //!
   TBranch        *b_fatjetak8RawPt;   //!
   TBranch        *b_fatjetak8Flavour;   //!
   TBranch        *b_fatjetak8Tau1;   //!
   TBranch        *b_fatjetak8Tau2;   //!
   TBranch        *b_fatjetak8Tau3;   //!
   TBranch        *b_fatjetak8TrimmedMass;   //!
   TBranch        *b_fatjetak8PrunedMass;   //!
   TBranch        *b_fatjetak8FilteredMass;   //!
   TBranch        *b_fatjetak8SoftdropMass;   //!
   TBranch        *b_ak8_subjet;   //!
   TBranch        *b_ak8jet_hasSubjet;   //!
   TBranch        *b_ak8subjet_btag;   //!
   TBranch        *b_fatjetak8Hbb;   //!
   TBranch        *b_fatjetak8topMVA;   //!
   TBranch        *b_fatjetca15P4;   //!
   TBranch        *b_fatjetca15RawPt;   //!
   TBranch        *b_fatjetca15Flavour;   //!
   TBranch        *b_fatjetca15Tau1;   //!
   TBranch        *b_fatjetca15Tau2;   //!
   TBranch        *b_fatjetca15Tau3;   //!
   TBranch        *b_fatjetca15TrimmedMass;   //!
   TBranch        *b_fatjetca15PrunedMass;   //!
   TBranch        *b_fatjetca15FilteredMass;   //!
   TBranch        *b_fatjetca15SoftdropMass;   //!
   TBranch        *b_ca15_subjet;   //!
   TBranch        *b_ca15jet_hasSubjet;   //!
   TBranch        *b_ca15subjet_btag;   //!
   TBranch        *b_fatjetca15Hbb;   //!
   TBranch        *b_fatjetca15topMVA;   //!
   TBranch        *b_fatjetak8puppiP4;   //!
   TBranch        *b_fatjetak8puppiRawPt;   //!
   TBranch        *b_fatjetak8puppiFlavour;   //!
   TBranch        *b_fatjetak8puppiTau1;   //!
   TBranch        *b_fatjetak8puppiTau2;   //!
   TBranch        *b_fatjetak8puppiTau3;   //!
   TBranch        *b_fatjetak8puppiTrimmedMass;   //!
   TBranch        *b_fatjetak8puppiPrunedMass;   //!
   TBranch        *b_fatjetak8puppiFilteredMass;   //!
   TBranch        *b_fatjetak8puppiSoftdropMass;   //!
   TBranch        *b_ak8puppi_subjet;   //!
   TBranch        *b_ak8puppijet_hasSubjet;   //!
   TBranch        *b_ak8puppisubjet_btag;   //!
   TBranch        *b_fatjetak8puppiHbb;   //!
   TBranch        *b_fatjetak8puppitopMVA;   //!
   TBranch        *b_fatjetca15puppiP4;   //!
   TBranch        *b_fatjetca15puppiRawPt;   //!
   TBranch        *b_fatjetca15puppiFlavour;   //!
   TBranch        *b_fatjetca15puppiTau1;   //!
   TBranch        *b_fatjetca15puppiTau2;   //!
   TBranch        *b_fatjetca15puppiTau3;   //!
   TBranch        *b_fatjetca15puppiTrimmedMass;   //!
   TBranch        *b_fatjetca15puppiPrunedMass;   //!
   TBranch        *b_fatjetca15puppiFilteredMass;   //!
   TBranch        *b_fatjetca15puppiSoftdropMass;   //!
   TBranch        *b_ca15puppi_subjet;   //!
   TBranch        *b_ca15puppijet_hasSubjet;   //!
   TBranch        *b_ca15puppisubjet_btag;   //!
   TBranch        *b_fatjetca15puppiHbb;   //!
   TBranch        *b_fatjetca15puppitopMVA;   //!
   TBranch        *b_lepP4;   //!
   TBranch        *b_lepPdgId;   //!
   TBranch        *b_lepIso;   //!
   TBranch        *b_lepSelBits;   //!
   TBranch        *b_lepPfPt;   //!
   TBranch        *b_lepChIso;   //!
   TBranch        *b_lepNhIso;   //!
   TBranch        *b_lepPhoIso;   //!
   TBranch        *b_lepPuIso;   //!
   TBranch        *b_metP4;   //!
   TBranch        *b_metSumEtRaw;   //!
   TBranch        *b_metPtJESUP;   //!
   TBranch        *b_metPtJESDOWN;   //!
   TBranch        *b_metP4_GEN;   //!
   TBranch        *b_metPuppi;   //!
   TBranch        *b_metPuppiSyst;   //!
   TBranch        *b_metSumEtRawPuppi;   //!
   TBranch        *b_metNoMu;   //!
   TBranch        *b_metNoHF;   //!
   TBranch        *b_metSumEtRawNoHF;   //!
   TBranch        *b_pfMet_e3p0;   //!
   TBranch        *b_trackMet;   //!
   TBranch        *b_caloMet_Pt;   //!
   TBranch        *b_caloMet_Phi;   //!
   TBranch        *b_caloMet_SumEt;   //!
   TBranch        *b_genP4;   //!
   TBranch        *b_genjetP4;   //!
   TBranch        *b_genPdgId;   //!
   TBranch        *b_genFlags;   //!
   TBranch        *b_puTrueInt;   //!
   TBranch        *b_mcWeight;   //!
   TBranch        *b_pdfQscale;   //!
   TBranch        *b_pdfAlphaQED;   //!
   TBranch        *b_pdfAlphaQCD;   //!
   TBranch        *b_pdfX1;   //!
   TBranch        *b_pdfX2;   //!
   TBranch        *b_pdfId1;   //!
   TBranch        *b_pdfId2;   //!
   TBranch        *b_pdfScalePdf;   //!
   TBranch        *b_r2f1;   //!
   TBranch        *b_r5f1;   //!
   TBranch        *b_r1f2;   //!
   TBranch        *b_r2f2;   //!
   TBranch        *b_r1f5;   //!
   TBranch        *b_r5f5;   //!
   TBranch        *b_pdfRwgt;   //!
   TBranch        *b_genIso;   //!
   TBranch        *b_genIsoFrixione;   //!
   TBranch        *b_photonP4;   //!
   TBranch        *b_photonIso;   //!
   TBranch        *b_photonSieie;   //!
   TBranch        *b_photonSelBits;   //!
   TBranch        *b_photonChIso;   //!
   TBranch        *b_photonChIsoRC;   //!
   TBranch        *b_photonNhIso;   //!
   TBranch        *b_photonNhIsoRC;   //!
   TBranch        *b_photonPhoIso;   //!
   TBranch        *b_photonPhoIsoRC;   //!
   TBranch        *b_photonPuIso;   //!
   TBranch        *b_photonPuIsoRC;   //!
   TBranch        *b_photonRawPt;   //!
   TBranch        *b_photonR9;   //!
   TBranch        *b_tauP4;   //!
   TBranch        *b_tauSelBits;   //!
   TBranch        *b_tauQ;   //!
   TBranch        *b_tauM;   //!
   TBranch        *b_tauIso;   //!
   TBranch        *b_tauChargedIsoPtSum;   //!
   TBranch        *b_tauNeutralIsoPtSum;   //!
   TBranch        *b_tauIsoDeltaBetaCorr;   //!
   TBranch        *b_triggerFired;   //!
   TBranch        *b_triggerPrescale;   //!
   TBranch        *b_triggerLeps;   //!
   TBranch        *b_triggerJets;   //!
   TBranch        *b_triggerTaus;   //!
   TBranch        *b_triggerPhotons;   //!
   TBranch        *b_npv;   //!

   NeroTreeBambu(TTree *tree=0);
   virtual ~NeroTreeBambu();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif
