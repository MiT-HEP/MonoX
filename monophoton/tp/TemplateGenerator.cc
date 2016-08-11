#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"

#include "RooUniformBinning.h"

#include "TreeEntries_simpletree.h"

#include <fstream>
#include <stdexcept>
#include <string>
#include <iostream>
#include <cstring>
#include <bitset>

enum SkimType {
  kEG,
  kMG,
  kMMG,
  nSkimTypes
};

TString skimTypes[nSkimTypes] = {
  "[tag:e, probe:g]",
  "[tag:m, probe:g]",
  "[tag:mm, probe:g]"
};

enum Variable {
  kMass,
  kSCRawMass,
  kDRGen,
  nVariables
};

class TemplateGenerator {
public:
  TemplateGenerator();
  ~TemplateGenerator();

  void addInput(SkimType _type, char const* _fileName) { input_[_type]->Add(_fileName); }
  void setTemplateBinning(RooUniformBinning const*, Variable = kMass);
  TH1D* makeEmptyTemplate(char const* name, Variable = kMass);
  TH1D* makeTemplate(SkimType, char const* name, char const* expr, Variable = kMass);
  TTree* makeUnbinnedTemplate(SkimType, char const* name, char const* expr, Variable = kMass);

  TFile* getTmpFile() const;

private:
  TChain* input_[nSkimTypes];
  int nBins_[nVariables]{60, 60, 40};
  double xmin_[nVariables]{60., 60., 0.};
  double xmax_[nVariables]{120., 120., 2.5};
};

TemplateGenerator::TemplateGenerator()
{
  for (auto*& tree : input_)
    tree = new TChain("skimmedEvents");
}

TemplateGenerator::~TemplateGenerator()
{
  for (auto* tree : input_)
    delete tree;
}

void
TemplateGenerator::setTemplateBinning(RooUniformBinning const* _binning, Variable _var/* = kMass*/)
{
  nBins_[_var] = _binning->numBins();
  xmin_[_var] = _binning->lowBound();
  xmax_[_var] = _binning->highBound();
}

TH1D*
TemplateGenerator::makeEmptyTemplate(char const* _name, Variable _var/*kMass*/)
{
  auto* temp = new TH1D(_name, "", nBins_[_var], xmin_[_var], xmax_[_var]);
  temp->Sumw2();
  return temp;
}

TH1D*
TemplateGenerator::makeTemplate(SkimType _type, char const* _name, char const* _expr, Variable _var/* = kMass*/)
{
  auto& tree(*input_[_type]);

  tree.Draw(">>elist", _expr, "entrylistarray");
  auto* elist(static_cast<TEntryListArray*>(gDirectory->Get("elist")));

  std::cout << "Tree " << skimTypes[_type] << ": making binned template from " << (elist ? elist->GetN() : 0) << " entries passing " << _expr << std::endl;

  if (!elist)
    return 0;

  unsigned const NMAX(256);

  unsigned size(0);
  double weight(0.);
  unsigned short npv(0);
  float mass[NMAX];
  float probeScRawPt[NMAX];
  float probeEta[NMAX];
  float probePhi[NMAX];
  float tagPt[NMAX];
  float tagEta[NMAX];
  float tagPhi[NMAX];

  tree.SetBranchAddress("tp.size", &size);
  tree.SetBranchAddress("weight", &weight);
  tree.SetBranchAddress("npv", &npv);
  switch (_var) {
  case kMass:
    tree.SetBranchAddress("tp.mass", mass);
    break;
  case kSCRawMass:
    tree.SetBranchAddress("probes.scRawPt", probeScRawPt);
    tree.SetBranchAddress("probes.eta", probeEta);
    tree.SetBranchAddress("probes.phi", probePhi);
    tree.SetBranchAddress("tags.pt", tagPt);
    tree.SetBranchAddress("tags.eta", tagEta);
    tree.SetBranchAddress("tags.phi", tagPhi);
    break;
  default:
    return 0;
  };

  auto* tmp = makeEmptyTemplate(_name, _var);

  tree.SetEntryList(elist);

  long iListEntry(0);
  long iTreeEntry(0);
  while ((iTreeEntry = tree.GetEntryNumber(iListEntry++)) >= 0) {
    long localEntry(tree.LoadTree(iTreeEntry));
    tree.GetEntry(iTreeEntry);

    auto* pList(elist->GetSubListForEntry(localEntry, tree.GetTree()));

    if (!pList) {
      std::cerr << "Sublist not found for entry " << iListEntry << " " << iTreeEntry << " (" << tree.GetTreeNumber() << ", " << localEntry << ")" << std::endl;
      throw std::runtime_error("entrylist");
    }

    for (int iE(0); iE != pList->GetN(); ++iE) {
      unsigned iP(pList->GetEntry(iE));

      if (_var == kSCRawMass) {
        //        std::cout << probeScRawPt[iP] << " " << probeEta[iP] << " " << probePhi[iP] << " " << tagPt[iP] << " " << tagEta[iP] << " " << tagPhi[iP] << std::endl;
        double pX(probeScRawPt[iP] * std::cos(probePhi[iP]));
        double pY(probeScRawPt[iP] * std::sin(probePhi[iP]));
        double pZ(probeScRawPt[iP] * std::sinh(probeEta[iP]));
        double pE(probeScRawPt[iP] * std::cosh(probeEta[iP]));
        double tX(tagPt[iP] * std::cos(tagPhi[iP]));
        double tY(tagPt[iP] * std::sin(tagPhi[iP]));
        double tZ(tagPt[iP] * std::sinh(tagEta[iP]));
        double tE(tagPt[iP] * std::cosh(tagEta[iP]));
        //        std::cout << std::sqrt((pE + tE) * (pE + tE) - (pX + tX) * (pX + tX) - (pY + tY) * (pY + tY) - (pZ + tZ) * (pZ + tZ)) << std::endl;
        mass[iP] = std::sqrt((pE + tE) * (pE + tE) - (pX + tX) * (pX + tX) - (pY + tY) * (pY + tY) - (pZ + tZ) * (pZ + tZ));
      }

      tmp->Fill(mass[iP], weight);
    }
  }

  for (int iX(1); iX != nBins_[_var] + 1; ++iX) {
    if (tmp->GetBinContent(iX) < 0.)
      tmp->SetBinContent(iX, 0.);
    if (tmp->GetBinContent(iX) - tmp->GetBinError(iX) < 0.)
      tmp->SetBinError(iX, 0.);
  }

  tree.SetEntryList(0);
  delete elist;

  return tmp;
}

TTree*
TemplateGenerator::makeUnbinnedTemplate(SkimType _type, char const* _name, char const* _expr, Variable _var/* = kMass*/)
{
  auto& tree(*input_[_type]);

  tree.Draw(">>elist", _expr, "entrylistarray");
  auto* elist(static_cast<TEntryListArray*>(gDirectory->Get("elist")));

  std::cout << "Tree " << skimTypes[_type] << ": making unbinned template from " << (elist ? elist->GetN() : 0) << " entries passing " << _expr << std::endl;

  if (!elist)
    return 0;

  auto* gd = gDirectory;

  auto* tmpFile(static_cast<TFile*>(gROOT->GetListOfFiles()->FindObject("/tmp/templategen.root")));
  if (!tmpFile)
    tmpFile = TFile::Open("/tmp/templategen.root", "recreate");
  else
    tmpFile->cd();

  unsigned const NMAX(256);

  TTree* tempTree(new TTree(_name, ""));

  unsigned size(0);
  double weight(0.);
  unsigned short npv(0);
  float mass[NMAX];
  float probeScRawPt[NMAX];
  float probeEta[NMAX];
  float probePhi[NMAX];
  float tagPt[NMAX];
  float tagEta[NMAX];
  float tagPhi[NMAX];

  double var(0.);

  tempTree->Branch("weight", &weight, "weight/D");

  tree.SetBranchAddress("tp.size", &size);
  tree.SetBranchAddress("weight", &weight);
  tree.SetBranchAddress("npv", &npv);
  switch (_var) {
  case kMass:
    tree.SetBranchAddress("tp.mass", mass);
    tempTree->Branch("mass", &var, "mass/D");
    break;
  case kSCRawMass:
    tree.SetBranchAddress("probes.scRawPt", probeScRawPt);
    tree.SetBranchAddress("probes.eta", probeEta);
    tree.SetBranchAddress("probes.phi", probePhi);
    tree.SetBranchAddress("tags.pt", tagPt);
    tree.SetBranchAddress("tags.eta", tagEta);
    tree.SetBranchAddress("tags.phi", tagPhi);
    tempTree->Branch("mass", &var, "mass/D");
    break;
  default:
    return 0;
  };

  tree.SetEntryList(elist);

  long iListEntry(0);
  long iTreeEntry(0);
  while ((iTreeEntry = tree.GetEntryNumber(iListEntry++)) >= 0) {
    long localEntry(tree.LoadTree(iTreeEntry));
    tree.GetEntry(iTreeEntry);

    auto* pList(elist->GetSubListForEntry(localEntry, tree.GetTree()));

    if (!pList) {
      std::cerr << "Sublist not found for entry " << iListEntry << " " << iTreeEntry << " (" << tree.GetTreeNumber() << ", " << localEntry << ")" << std::endl;
      throw std::runtime_error("entrylist");
    }

    for (int iE(0); iE != pList->GetN(); ++iE) {
      unsigned iP(pList->GetEntry(iE));

      if (_var == kSCRawMass) {
        double pX(probeScRawPt[iP] * std::cos(probePhi[iP]));
        double pY(probeScRawPt[iP] * std::sin(probePhi[iP]));
        double pZ(probeScRawPt[iP] * std::sinh(probeEta[iP]));
        double pE(probeScRawPt[iP] * std::cosh(probeEta[iP]));
        double tX(tagPt[iP] * std::cos(tagPhi[iP]));
        double tY(tagPt[iP] * std::sin(tagPhi[iP]));
        double tZ(tagPt[iP] * std::sinh(tagEta[iP]));
        double tE(tagPt[iP] * std::cosh(tagEta[iP]));
        var = std::sqrt((pE + tE) * (pE + tE) - (pX + tX) * (pX + tX) - (pY + tY) * (pY + tY) - (pZ + tZ) * (pZ + tZ));
      }
      else if (_var == kMass)
        var = mass[iP];

      tempTree->Fill();
    }
  }

  tree.SetEntryList(0);
  delete elist;
 
  gd->cd();
  
  return tempTree;
}

TFile*
TemplateGenerator::getTmpFile() const
{
  auto* tmpFile(static_cast<TFile*>(gROOT->GetListOfFiles()->FindObject("/tmp/templategen.root")));
  return tmpFile;
}
