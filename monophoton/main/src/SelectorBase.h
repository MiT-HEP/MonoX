#ifndef SelectorBase_h
#define SelectorBase_h

#include "PandaTree/Objects/interface/EventBase.h"

#include "Operator.h"

#include "TTree.h"
#include "TFile.h"
#include "TString.h"

#include <vector>
#include <iostream>
#include <chrono>
#include <mutex>

typedef std::chrono::high_resolution_clock Clock;

class EventSelectorBase {
public:
  EventSelectorBase(char const* name) : name_(name) {}
  virtual ~EventSelectorBase();

  virtual void addOperator(Operator*, unsigned idx = -1) = 0;
  unsigned size() const { return operators_.size(); }
  Operator* getOperator(unsigned iO) const { return operators_.at(iO); }
  Operator* findOperator(char const* name) const;
  unsigned index(char const* name) const;
  void removeOperator(char const* name);

  void initialize(char const* outputPath, panda::EventBase& inEvent, panda::utils::BranchList& blist, bool isMC);
  void finalize();
  virtual void selectEvent(panda::EventBase&) = 0;

  TString const& name() const { return name_; }
  virtual char const* className() const = 0;

  void setPreskim(char const* s) { preskim_ = s; }
  char const* getPreskim() const { return preskim_.Data(); }

  void setOwnOperators(bool b) { ownOperators_ = b; }
  void setUseTimers(bool b) { useTimers_ = b; }
  void setPrintLevel(unsigned l, std::ostream* st = 0) { printLevel_ = l; if (st) stream_ = st; }

  static std::mutex mutex;

protected:
  virtual void setupSkim_(panda::EventBase& inEvent, bool isMC) {}
  virtual void addOutput_(TFile*& outputFile) {}

  TString name_;
  TTree* skimOut_{0};
  TTree* cutsOut_{0};

  std::vector<Operator*> operators_;
  bool ownOperators_{true};

  double inWeight_{1.};

  bool useTimers_{false};
  std::vector<Clock::duration> timers_;

  TString preskim_{""};

  unsigned printLevel_{0};
  std::ostream* stream_{&std::cout};
};

#endif
