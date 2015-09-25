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
  kElectron,
  nTemplateTypes
};

enum TemplateVar {
  kSigmaIetaIeta,
  kPhotonIsolation,
  nTemplateVars
};

enum FakeVar {
  kChIso,
  kNhIso,
  kPhIso,
  kHOverE,
  kSieie,
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
  TemplateGenerator(TemplateType, TemplateVar, char const* fileName, bool write = false);
  ~TemplateGenerator() {}

  void fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id, Double_t _xsec);
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

TemplateGenerator::TemplateGenerator(TemplateType _type, TemplateVar _var, char const* _fileName, bool _write/* = false*/) :
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
  if (_write)
    file = TFile::Open(_fileName, "recreate");
  else
    file = TFile::Open(_fileName);

  if (!file || file->IsZombie())
    throw std::runtime_error(std::string("File ") + _fileName + " could not be opened.");

  if (_write) {
    file->cd();
    skimTree_ = new TTree("skimmedEvents", "template skim");
  }
  else
    skimTree_ = static_cast<TTree*>(file->Get("skimmedEvents"));
}

void
TemplateGenerator::fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id, Double_t _xsec)
{
  if (skimTree_->GetListOfBranches()->GetEntries() != 0)
    throw std::runtime_error("Skim already exists.");

  simpletree::Event event;
  event.setAddress(*_input);
  event.book(*skimTree_, {"run", "lumi", "event", "weight", "rho", "npv", "ntau", "jets", "electrons" , "muons", "t1Met"});

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
  
  
  Double_t eventWeight;
  if (_xsec < 0) eventWeight = 1;
  else {
    TH1D* hWeight = new TH1D("hWeight","Sum of Weights", 1, 0.0, 1.0);
    _input->Draw("0.5>>hWeight","weight","goff");
    Double_t nEvents =  hWeight->GetBinContent(1);
    Double_t lumi = 8.1;
    eventWeight = _xsec * lumi / nEvents; 
  }

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    event.weight *= eventWeight;

    selectedPhotons.clear();
    unsigned iSel(0);

    auto& photons(event.photons);
    auto& electrons(event.electrons);
    
    UInt_t kObject = 0; // 0 = photon
    UInt_t nObjects = photons.size();
    
    if (tType_ == kElectron) {
      kObject = 1; // 1 = electron
      nObjects = electrons.size();
    }

    Float_t* hOverE[2] = {
      event.photons.data.hOverE,
      event.electrons.data.hOverE
    };

    Float_t* sieie[2] = {
      event.photons.data.sieie,
      event.electrons.data.sieie
    };
    
    Float_t* chIso[2] = {
      event.photons.data.chIso,
      event.electrons.data.chIsoPh
    };

    Float_t* nhIso[2] = {
      event.photons.data.nhIso,
      event.electrons.data.nhIsoPh
    };

    Float_t* phIso[2] = {
      event.photons.data.phIso,
      event.electrons.data.phIsoPh
    };


    for (unsigned iP(0); iP != nObjects; ++iP) {
      // apply photon selection for the background
    
      Bool_t PassCut[nFakeVars];
      Bool_t PassSel = true;
      for (unsigned iC(0); iC < nFakeVars; iC++) {
	PassCut[iC] = false;
      }

      // barrel photons
      UInt_t kLocation;
      if (TMath::Abs(photons[iP].eta) < 1.5) kLocation = kBarrel;
      else kLocation = kEndcap;
		
      // baseline photon selection
      if (hOverE[kObject][iP] < cut_hOverE[kLocation][_id]) PassCut[kHOverE] = true;
      if (chIso[kObject][iP] < cut_chIso[kLocation][_id]) PassCut[kChIso] = true;
      if (nhIso[kObject][iP] < (cut_nhIso[0][kLocation][_id]+TMath::Exp(cut_nhIso[1][kLocation][_id]*photons[iP].pt + cut_nhIso[2][kLocation][_id]))) PassCut[kNhIso] = true;
      if (tVar_ == kPhotonIsolation) PassCut[kPhIso] = true;
      else {
	if (phIso[kObject][iP] < (cut_phIso[0][kLocation][_id] + cut_phIso[1][kLocation][_id]*photons[iP].pt)) PassCut[kPhIso] = true;
      }
      if (tVar_ == kSigmaIetaIeta) PassCut[kSieie] = true;
      else {
	if (sieie[kObject][iP] < cut_sieie[kLocation][_id]) PassCut[kSieie] = true;
      }
      if (tType_ != kElectron) {
	if (photons[iP].csafeVeto) continue;
      }
      
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
	    if (_fakevar == kChIso) {
	      if (chIso[kObject][iP] > cut_chIso[kLocation][kTight]) PassSel = true;
	    }
	    else if (_fakevar == kNhIso) {
	      if (nhIso[kObject][iP] > (cut_nhIso[0][kLocation][kTight]+TMath::Exp(cut_nhIso[1][kLocation][kTight]*photons[iP].pt + cut_nhIso[2][kLocation][kTight]))) PassSel = true;
	    }
	    else if (_fakevar == kPhIso) {
	      if (phIso[kObject][iP] > (cut_phIso[0][kLocation][kTight] + cut_phIso[1][kLocation][kTight]*photons[iP].pt)) PassSel = true;
	    }
	    else if (_fakevar == kHOverE) {
	      if (hOverE[kObject][iP] > cut_hOverE[kLocation][kTight]) PassSel = true;
	    }
	    else if (_fakevar == kSieie) {
	      if (sieie[kObject][iP] > cut_sieie[kLocation][kTight]) PassSel = true;
	    }
	  }
	  else { 
	    if (!PassCut[iC]) PassSel = false;
	  }
	}
      }
      
      if (!PassSel) continue;
    
      selectedPhotons.resize(iSel + 1);
      simpletree::Photon& selected(selectedPhotons[iSel]);
      
      if (tType_ == kElectron) {
	selected.pt = electrons[iP].pt;
	selected.eta = electrons[iP].eta;
	selected.phi = electrons[iP].phi;    
	selected.chIso = electrons[iP].chIsoPh; 
	selected.nhIso = electrons[iP].nhIsoPh;
	selected.phIso = electrons[iP].phIsoPh;
	selected.sieie = electrons[iP].sieie;
	selected.hOverE = electrons[iP].hOverE;
	selected.matchedGen = electrons[iP].matchedGen;
	selected.hadDecay = electrons[iP].hadDecay;
	selected.pixelVeto = true;
	selected.csafeVeto = true;
	/*
	selected.loose = -1;
	selected.medium = -1;
	selected.tight = -1;
	selected.matchHLT120 = -1;
	selected.matchHLT165HE10 = electrons[iP].matchHLT165HE10;
	selected.matchHLT175 = electrons[iP].matchHLT175;
	*/
      }
      else {
	selected.pt = photons[iP].pt;
	selected.eta = photons[iP].eta;
	selected.phi = photons[iP].phi;    
	selected.chIso = photons[iP].chIso; 
	selected.nhIso = photons[iP].nhIso;
	selected.phIso = photons[iP].phIso;
	selected.sieie = photons[iP].sieie;
	selected.hOverE = photons[iP].hOverE;
	selected.matchedGen = photons[iP].matchedGen;
	selected.hadDecay = photons[iP].hadDecay;
	selected.pixelVeto = photons[iP].pixelVeto;
	selected.csafeVeto = photons[iP].csafeVeto;
	selected.loose = photons[iP].loose;
	selected.medium = photons[iP].medium;
	selected.tight = photons[iP].tight;
	selected.matchHLT120 = photons[iP].matchHLT120;
	selected.matchHLT165HE10 = photons[iP].matchHLT165HE10;
	selected.matchHLT175 = photons[iP].matchHLT175;
      } 
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
  else if (tVar_ == kPhotonIsolation)
    var = "phIso";

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
