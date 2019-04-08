#ifndef operators_h
#define operators_h

#include "PandaTree/Objects/interface/EventMonophoton.h"
#include "PandaTree/Objects/interface/EventTP.h"

#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TRandom3.h"

#include "TDirectory.h"

#include "logging.h"

#include "fastjet/JetDefinition.hh"

#include <bitset>
#include <map>
#include <vector>
#include <utility>
#include <iostream>
#include <functional>

enum LeptonFlavor {
  lElectron,
  lMuon,
  nLeptonFlavors
};

enum Collection {
  cPhotons,
  cElectrons,
  cMuons,
  cTaus,
  nCollections
};

enum MetSource {
  kInMet,
  kOutMet
};

enum TPEventType {
  kTPEG,
  kTPEEG,
  kTPMG,
  kTPMMG,
  kTP2E,
  kTP2M,
  kTPEM,
  kTPME,
  nOutTypes
};

const UInt_t NMAX_PARTICLES = 128;

//--------------------------------------------------------------------
// Base classes
//--------------------------------------------------------------------

class Operator {
 public:
  Operator(char const* name) : name_(name) {}
  virtual ~Operator() {}

  char const* name() const { return name_.Data(); }
  virtual TString expr() const { return name_; }

  virtual bool exec(panda::EventMonophoton const&, panda::EventBase&) = 0;

  virtual void addInputBranch(panda::utils::BranchList&) {}
  virtual void addBranches(TTree& skimTree) {}
  virtual void initialize(panda::EventMonophoton&) {}

  void setPrintLevel(unsigned l) { printLevel_ = l; }
  void setOutputStream(std::ostream& st) { stream_ = &st; }

 protected:
  TString name_;
  unsigned printLevel_{0};
  std::ostream* stream_{&std::cout};
};

class CutMixin {
 public:
  CutMixin(char const* name) : cutName_(name), result_(false), ignoreDecision_(false) {}

  TString cutExpr(TString const& name) const;

  void setIgnoreDecision(bool b) { ignoreDecision_ = b; }

  virtual void registerCut(TTree& cutsTree) { cutsTree.Branch(cutName_, &result_, cutName_ + "/O"); }

 protected:
  TString cutName_;
  bool result_;
  bool ignoreDecision_;
};

#endif
