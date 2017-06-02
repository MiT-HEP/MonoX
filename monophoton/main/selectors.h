#ifndef selectors_h
#define selectors_h

#include "TTree.h"
#include "TFile.h"
#include "TString.h"
#include "TF1.h"

#include "operators.h"

#include <vector>
#include <chrono>
#include <iostream>

typedef std::chrono::high_resolution_clock Clock;

class Operator;

class EventSelectorBase {
public:
  EventSelectorBase(char const* name) : name_(name) {}
  virtual ~EventSelectorBase();

  void addOperator(Operator*, unsigned idx = -1);
  unsigned size() const { return operators_.size(); }
  Operator* getOperator(unsigned iO) const { return operators_.at(iO); }
  Operator* findOperator(char const* name) const;
  void removeOperator(char const* name);

  void initialize(char const* outputPath, panda::EventMonophoton& inEvent, panda::utils::BranchList& blist, bool isMC);
  void finalize();
  virtual void selectEvent(panda::EventMonophoton&) = 0;

  TString const& name() const { return name_; }
  virtual char const* className() const = 0;

  void setCanPhotonSkim(bool b) { canPhotonSkim_ = b; }
  bool getCanPhotonSkim() const { return canPhotonSkim_; }

  void setOwnOperators(bool b) { ownOperators_ = b; }
  void setUseTimers(bool b) { useTimers_ = b; }
  void setPrintLevel(unsigned l, std::ostream* st = 0) { printLevel_ = l; if (st) stream_ = st; }

protected:
  virtual void setupSkim_(panda::EventMonophoton& inEvent, bool isMC) {}
  virtual void addOutput_(TFile*& outputFile) {}

  TString name_;
  TTree* skimOut_{0};
  TTree* cutsOut_{0};

  std::vector<Operator*> operators_;
  bool ownOperators_{true};

  double inWeight_{1.};

  bool useTimers_{false};
  std::vector<Clock::duration> timers_;

  bool canPhotonSkim_{true};

  unsigned printLevel_{0};
  std::ostream* stream_{&std::cout};
};

class EventSelector : public EventSelectorBase {
public:
  EventSelector(char const* name) : EventSelectorBase(name) {}
  ~EventSelector() {}

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "EventSelector"; }

  void setPartialBlinding(unsigned prescale, unsigned minRun = 0) { blindPrescale_ = prescale; blindMinRun_ = minRun; }

 protected:
  void setupSkim_(panda::EventMonophoton& event, bool isMC) override;
  void prepareFill_(panda::EventMonophoton&);

  panda::EventMonophoton outEvent_;

  unsigned blindPrescale_{1};
  unsigned blindMinRun_{0};
};

class ZeeEventSelector : public EventSelector {
  // Special event selector for Zee events where one input event can yield multiple output events
 public:
  ZeeEventSelector(char const* name);
  ~ZeeEventSelector();

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "ZeeEventSelector"; }

  class EEPairSelection : public PhotonSelection {
  public:
    EEPairSelection(char const* name = "EEPairSelection");
    std::vector<std::pair<unsigned, unsigned>> const& getEEPairs() const { return eePairs_; }

  protected:
    bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;
    
    std::vector<std::pair<unsigned, unsigned>> eePairs_;
  };

 protected:
  std::vector<Operator*>::iterator eePairSel_;
};

class PartonSelector : public EventSelector {
  // Special event selector that considers events with specified lepton flavors in LHE
 public:
  PartonSelector(char const* name) : EventSelector(name) {}

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "PartonSelector"; }

  void setRejectedPdgId(unsigned id) { rejectedId_ = id; }
  void setAcceptedPdgId(unsigned id) { acceptedId_ = id; }

  unsigned getRejectedPdgId() const { return rejectedId_; }
  unsigned getAcceptedPdgId() const { return acceptedId_; }

 private:
  unsigned rejectedId_{0};
  unsigned acceptedId_{0};
};

class NormalizingSelector : public EventSelector {
  // Special event selector that normalizes the output to a given total sumW at the end
 public:
  NormalizingSelector(char const* name) : EventSelector(name) {}
  ~NormalizingSelector() {}

  void setNormalization(double norm, char const* normCut) { norm_ = norm; normCut_ = normCut; }

 protected:
  void addOutput_(TFile*& outputFile) override;

  double norm_{1.};
  TString normCut_{""};
};

class SmearingSelector : public EventSelector {
  // Generates nSample events per input event with smeared MET according to a model.
  // Technically there are statistics issues here, but we'll ignore it for now.
 public:
  SmearingSelector(char const* name) : EventSelector(name) {}
  ~SmearingSelector() {}

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "SmearingSelector"; }

  void setNSamples(unsigned n) { nSamples_ = n; }
  void setFunction(TF1* func) { func_ = func; }

 protected:
  unsigned nSamples_{1};
  TF1* func_{0};
};

class TagAndProbeSelector : public EventSelectorBase {
public:
  TagAndProbeSelector(char const* name) : EventSelectorBase(name) {}
  ~TagAndProbeSelector() {}

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "TagAndProbeSelector"; }

  void setSampleId(unsigned id) { sampleId_ = id; }

 protected:
  void setupSkim_(panda::EventMonophoton& inEvent, bool isMC) override;

  panda::EventTPPhoton outEvent_;
  unsigned sampleId_; // outEvent_.sample gets reset at the beginning of each event
};

#endif
