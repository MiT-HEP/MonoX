#ifndef SelectorBase_h
#define SelectorBase_h

#include "PandaTree/Objects/interface/EventBase.h"
#include "PandaTree/Objects/interface/Event.h"

#include "Operator.h"

#include "TTree.h"
#include "TFile.h"
#include "TString.h"

#include <vector>
#include <array>
#include <iostream>
#include <chrono>
#include <mutex>

typedef std::chrono::high_resolution_clock Clock;

class EventSelectorBase {
public:
  enum InputEventType {
    kEventBase,
    kEvent,
    kEventMonophoton,
    kEventTP,
    kEventSV,
    nInputEventTypes
  };
  
  EventSelectorBase(char const* name, InputEventType inputType, panda::EventBase* outEvent);
  virtual ~EventSelectorBase();

  virtual void addOperator(Operator*, unsigned idx = -1) = 0;
  unsigned size() const { return operators_.size(); }
  Operator* getOperator(unsigned iO) const { return operators_.at(iO); }
  Operator* findOperator(char const* name) const;
  unsigned index(char const* name) const;
  void removeOperator(char const* name);

  void initialize(char const* outputPath, std::array<panda::EventBase*, nInputEventTypes>& inEvents, panda::utils::BranchList& blist, bool isMC);
  void finalize();

  virtual void selectEvent();

  TString const& name() const { return name_; }
  virtual char const* className() const { return "EventSelectorBase"; }

  void setPreskim(char const* s) { preskim_ = s; }
  char const* getPreskim() const { return preskim_.Data(); }

  void setOwnOperators(bool b) { ownOperators_ = b; }
  void setUseTimers(bool b) { useTimers_ = b; }
  void setPartialBlinding(unsigned prescale, unsigned minRun = 0) { blindPrescale_ = prescale; blindMinRun_ = minRun; }
  void setPrintLevel(unsigned l, std::ostream* st = 0) { printLevel_ = l; if (st) stream_ = st; }

  InputEventType inputType() const { return inputType_; }

  static void prepareEvent(unsigned inputType, panda::Event const&, panda::EventBase&, bool isData);

  static std::mutex mutex;

protected:
  typedef std::vector<Operator*> OperatorVector;

  virtual void castInEvent_() {}
  virtual panda::utils::BranchList directCopyBranches_(bool isMC);
  virtual panda::utils::BranchList processedBranches_(bool isMC) const;
  virtual void setupSkim_(bool isMC) {}
  virtual void addOutput_(TFile*& outputFile) {}
  void needPrepareFill_(panda::CollectionBase& coll) { directCopyCollections_.push_back(&coll); }
  bool runOperators_() { auto itr(operators_.begin()); return runOperators_(itr, operators_.end()); }
  bool runOperators_(OperatorVector::iterator&, OperatorVector::iterator const&);
  void prepareFill_();
  void fillEvent_(bool pass);

  TString name_;
  TTree* skimOut_{0};
  TTree* cutsOut_{0};

  InputEventType const inputType_;
  panda::EventBase* inEventBase_{nullptr};
  panda::EventBase* outEventBase_{nullptr};

  OperatorVector operators_;
  bool ownOperators_{true};

  std::vector<panda::CollectionBase*> directCopyCollections_{};

  double inWeight_{1.};

  std::vector<unsigned> passes_;

  bool useTimers_{false};
  std::vector<Clock::duration> timers_;

  TString preskim_{""};

  unsigned blindPrescale_{1};
  unsigned blindMinRun_{0};

  unsigned printLevel_{0};
  std::ostream* stream_{&std::cout};
};

#endif
