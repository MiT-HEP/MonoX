#ifndef Operator_h
#define Operator_h

#include "PandaTree/Objects/interface/EventMonophoton.h"

#include "logging.h"

#include <iostream>

enum Collection {
  cPhotons,
  cElectrons,
  cMuons,
  cTaus,
  nCollections
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

  TString cutExpr(TString const& name) const {
    if (ignoreDecision_)
      return TString::Format("(%s)", name.Data());
    else
      return TString::Format("[%s]", name.Data());
  }

  void setIgnoreDecision(bool b) { ignoreDecision_ = b; }

  virtual void registerCut(TTree& cutsTree) { cutsTree.Branch(cutName_, &result_, cutName_ + "/O"); }

 protected:
  TString cutName_;
  bool result_;
  bool ignoreDecision_;
};

#endif
