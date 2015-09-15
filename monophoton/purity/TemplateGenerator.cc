#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"

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

class TemplateGenerator {
public:
  TemplateGenerator(TemplateType, TemplateVar, char const* fileName, bool recreate = false);
  ~TemplateGenerator() {}

  void fillSkim(TTree*);
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
TemplateGenerator::fillSkim(TTree* _input)
{
  if (skimTree_->GetListOfBranches()->GetEntries() != 0)
    throw std::runtime_error("Skim already exists.");

  simpletree::Event event;
  event.setAddress(*_input);
  event.book(*skimTree_);

  simpletree::PhotonCollection selectedPhotons;
  selectedPhotons.book(*skimTree_, "selPhotons");

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    selectedPhotons.clear();
    unsigned iSel(0);

    if (tType_ == kBackground) {
      auto& photons(event.photons);
      for (unsigned iP(0); iP != photons.size; ++iP) {
        // apply photon selection for the background

        selectedPhotons.resize(iSel + 1);
        selectedPhotons[iSel] = photons[iP];
        ++iSel;
      }
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
