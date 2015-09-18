#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TMath.h"

#include "TreeEntries_simpletree.h"

#include <fstream>
#include <stdexcept>
#include <string>
#include <iostream>
#include <cstring>

enum TemplateType {
  kPhoton,
  kBackground,
  nTemplateTypes
};

enum TemplateVar {
  kSigmaIetaIeta,
  nTemplateVars
};

enum FakeVar {
  kChIso,
  kNhIso,
  kPhIso,
  kHOverE,
  // kSieie,
  nFakeVars
};

enum PhotonId {
  kLoose,
  kMedium,
  kTight,
  nPhotonIds
};

enum PhotonLocation {
  kBarrel,
  kEndcap,
  nPhotonLocations
};

class TemplateGenerator {
public:
  TemplateGenerator(TemplateType, TemplateVar, char const* fileName, bool recreate = false);
  ~TemplateGenerator() {}

  void fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id);
  void writeSkim();
  void setTemplateBinning(int nBins, double xmin, double xmax);
  TH1D* makeTemplate(char const* name, char const* expr);

private:
  TemplateType tType_;
  TemplateVar tVar_;

  int nBins_;
  double xmin_;
  double xmax_;

  TTree* skimTree_{0};
};

TemplateGenerator::TemplateGenerator(TemplateType _type, TemplateVar _var, char const* _fileName, bool _recreate/* = false*/) :
  tType_(_type),
  tVar_(_var),
  nBins_(40),
  xmin_(0.),
  xmax_(0.02)
{
  bool exists(false);
  std::ifstream fs(_fileName, std::ifstream::in | std::ifstream::binary);
  if (fs.is_open())
    exists = true;
  fs.close();

  TFile* file = 0;
  if (_recreate || !exists)
    file = TFile::Open(_fileName, "recreate");
  else
    file = TFile::Open(_fileName);

  if (!file || file->IsZombie())
    throw std::runtime_error(std::string("File ") + _fileName + " could not be opened.");

  if (_recreate || !exists) {
    file->cd();
    skimTree_ = new TTree("skimmedEvents", "template skim");
  }
  else
    skimTree_ = static_cast<TTree*>(file->Get("skimmedEvents"));
}

void
TemplateGenerator::fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id)
{
  if (skimTree_->GetListOfBranches()->GetEntries() != 0)
    throw std::runtime_error("Skim already exists.");

  simpletree::Event event;
  event.setAddress(*_input);
  event.book(*skimTree_, {&event.run, &event.lumi, &event.event, &event.weight, &event.rho, &event.npv,&event.ntau,&event.jets,&event.electrons,&event.muons,&event.t1Met});

  simpletree::PhotonCollection selectedPhotons("selPhotons");
  selectedPhotons.book(*skimTree_);

  Float_t cut_hOverE[2][3] = {
    {0.05,0.05,0.05},
    {0.05,0.05,0.05}
  };
  Float_t cut_sieie[2][3] = {
    {0.0103,0.0100,0.100},
    {0.0277,0.0267,0.0267}
  };
  Float_t cut_chIso[2][3] = {
    {2.44,1.31,0.91},
    {1.84,1.25,0.65}
  };
  Float_t cut_nhIso[3][2][3] = {
    { {2.57,0.60,0.33},
      {4.00,1.65,0.93} },
    { {0.0044,0.0044,0.0044},
      {0.0040,0.0040,0.0040} },
    { {0.5809,0.5809,0.5809},
      {0.9402,0.9402,0.9402} }
  };
  Float_t cut_phIso[2][2][3] = {
    { {1.92,1.33,0.61},
      {2.15,1.02,0.54} },
    { {0.0043,0.0043,0.0043},
      {0.0041,0.0041,0.0041} }
  };

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    selectedPhotons.clear();
    unsigned iSel(0);

    Bool_t PassCut[nFakeVars];
    Bool_t PassSel;
      
    auto& photons(event.photons);
    for (unsigned iP(0); iP != photons.size; ++iP) {
      // apply photon selection for the background
      
      PassSel = true;
      for (unsigned iC(0); iC < nFakeVars; iC++) {
	PassCut[iC] = false;
      }

      // barrel photons
      if (TMath::Abs(photons[iP].eta) < 1.5) {
	/*
	  if (!(_loc == kBarrel)) {
	  PassSel = false;
	  continue;
	}
	*/
	
	// baseline photon selection
	if (photons[iP].hOverE < cut_hOverE[kBarrel][_id]) PassCut[kHOverE] = true;
	if (photons[iP].chIso < cut_chIso[kBarrel][_id]) PassCut[kChIso] = true;
	if (photons[iP].nhIso < (cut_nhIso[0][kBarrel][_id]+TMath::Exp(cut_nhIso[1][kBarrel][_id]*photons[iP].pt + cut_nhIso[2][kBarrel][_id]))) PassCut[kNhIso] = true;
	if (photons[iP].phIso < (cut_phIso[0][kBarrel][_id] + cut_phIso[1][kBarrel][_id]*photons[iP].pt)) PassCut[kPhIso] = true;
	if (photons[iP].csafeVeto) continue;

	// real vs fake selection
	if (tType_ == kPhoton) {
	  for (unsigned iC(0); iC < nFakeVars; iC++) {
	    if (!PassCut[iC]) PassSel = false;
	  }
	}
	else if (tType_ == kBackground) {
	  for (unsigned iC(0); iC < nFakeVars; iC++) {
	    if (iC == _fakevar) {
	      if (PassCut[iC]) PassSel = false;
	      // picking out chIso as fakevar
	      if (photons[iP].chIso > cut_chIso[kBarrel][kTight]) PassSel = true;
	    }
	    else { 
	      if (!PassCut[iC]) PassSel = false;
	    }
	  }
	}
      }

      // endcap photons (loose selection)
      else {
	/*
	if (!(_loc == kEndcap)) {
	  PassSel = false;
	  continue;
	}
	*/
	
	// baseline photon selection
	if (photons[iP].hOverE < cut_hOverE[kEndcap][_id]) PassCut[kHOverE] = true;
	if (photons[iP].chIso < cut_chIso[kEndcap][_id]) PassCut[kChIso] = true;
	if (photons[iP].nhIso < (cut_nhIso[0][kEndcap][_id]+TMath::Exp(cut_nhIso[1][kEndcap][_id]*photons[iP].pt + cut_nhIso[2][kEndcap][_id]))) PassCut[kNhIso] = true;
	if (photons[iP].phIso < (cut_phIso[0][kEndcap][_id] + cut_phIso[1][kEndcap][_id]*photons[iP].pt)) PassCut[kPhIso] = true;
	if (photons[iP].csafeVeto) continue;

	// real vs fake selection
	if (tType_ == kPhoton) {
	  for (unsigned iC(0); iC < nFakeVars; iC++) {
	    if (!PassCut[iC]) PassSel = false;
	  }
	}
	else if (tType_ == kBackground) {
	  for (unsigned iC(0); iC < nFakeVars; iC++) {
	    if (iC == _fakevar) {
	      if (PassCut[iC]) PassSel = false;
	      // picking out chIso as fakevar
	      if (photons[iP].chIso > cut_chIso[kEndcap][kTight]) PassSel = true;
	    }
	    else { 
	      if (!PassCut[iC]) PassSel = false;
	    }
	  }
	}
      }
      
      if (!PassSel) continue;

      selectedPhotons.resize(iSel + 1);
      selectedPhotons[iSel] = photons[iP];
      ++iSel;
    }
 
    if (iSel != 0)
      skimTree_->Fill();
  }
}

void
TemplateGenerator::writeSkim()
{
  auto* file = skimTree_->GetCurrentFile();
  file->cd();
  skimTree_->Write();
}

void
TemplateGenerator::setTemplateBinning(int _nBins, double _xmin, double _xmax)
{
  nBins_ = _nBins;
  xmin_ = _xmin;
  xmax_ = _xmax;
}

TH1D*
TemplateGenerator::makeTemplate(char const* _name, char const* _expr)
{
  auto* gd = gDirectory;
  skimTree_->GetCurrentFile()->cd();
  auto* tmp = new TH1D(_name, "", nBins_, xmin_, xmax_);
  tmp->Sumw2();

  TString var;
  if (tVar_ == kSigmaIetaIeta)
    var = "sieie";

  TString weight("weight");
  if (std::strlen(_expr) != 0) {
    weight += " * (";
    weight += _expr;
    weight += ")";
  }

  skimTree_->Draw("selPhotons." + var + ">>" + TString(_name), weight, "goff");

  gd->cd();

  return tmp;
}
