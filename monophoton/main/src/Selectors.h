#ifndef Selectors_h
#define Selectors_h

#include "SelectorBase.h"
#include "BaseOperators.h"

#include "TF1.h"

class EventSelector : public EventSelectorBase {
public:
  EventSelector(char const* name) : EventSelectorBase(name) {}
  ~EventSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;
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
  ZeeEventSelector(char const* name) : EventSelector(name) {}
  ~ZeeEventSelector() {}

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "ZeeEventSelector"; }

 protected:
  void setupSkim_(panda::EventMonophoton& event, bool isMC) override;

  std::vector<Operator*>::iterator leptonSelection_;
};

class PartonSelector : public EventSelector {
  // Special event selector that considers events with specified lepton flavors in LHE
  // Will internally use PartonFlavor operator. This selector exists purely for speed optimization.
 public:
  PartonSelector(char const* name);
  ~PartonSelector();

  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "PartonSelector"; }

  void setRejectedPdgId(unsigned id) { flavor_->setRejectedPdgId(id); }
  void setRequiredPdgId(unsigned id) { flavor_->setRequiredPdgId(id); }

  unsigned getRejectedPdgId() const { return flavor_->getRejectedPdgId(); }
  unsigned getRequiredPdgId() const { return flavor_->getRequiredPdgId(); }

 private:
  PartonFlavor* flavor_{0};
  unsigned rejectedId_{0};
  unsigned requiredId_{0};
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

#endif
