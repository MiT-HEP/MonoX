#ifndef selectors_h
#define selectors_h

#include "operators.h"

#include "TTree.h"
#include "TString.h"

#include <vector>

class EventSelector {
public:
  EventSelector(char const* name) : name_(name) {}
  virtual ~EventSelector() {}

  void addOperator(Operator* _op, unsigned idx = -1) { if (idx >= operators_.size()) operators_.push_back(_op); else operators_.insert(operators_.begin() + idx, _op); }
  virtual void initialize(char const* outputPath, simpletree::Event& event);
  virtual void finalize();
  virtual bool selectEvent(simpletree::Event const&);

  TString const& name() const { return name_; }
  unsigned size() const { return operators_.size(); }
  Operator* getOperator(unsigned iO) const { return operators_.at(iO); }
  Operator* findOperator(char const* name) const;

 protected:
  TString name_;
  std::vector<Operator*> operators_;
  TTree* skimOut_{0};
  TTree* cutsOut_{0};
  simpletree::Event outEvent_;
};

class ZeeEventSelector : public EventSelector {
  // Special event selector for Zee events where one input event can yield multiple output events
 public:
  ZeeEventSelector(char const* name);
  ~ZeeEventSelector();

  bool selectEvent(simpletree::Event const&) override;

  class EEPairSelection : public PhotonSelection {
  public:
    EEPairSelection(char const* name = "EEPairSelection");
    std::vector<std::pair<unsigned, unsigned>> const& getEEPairs() const { return eePairs_; }

  protected:
    bool pass(simpletree::Event const&, simpletree::Event&) override;
    
    std::vector<std::pair<unsigned, unsigned>> eePairs_;
  };

 protected:
  std::vector<Operator*>::iterator eePairSel_;
};

class WlnuSelector : public EventSelector {
  // Special event selector that considers only non-electron decays of W
 public:
  WlnuSelector(char const* name) : EventSelector(name) {}

  bool selectEvent(simpletree::Event const&) override;
};

class NormalizingSelector : public EventSelector {
  // Special event selector that normalizes the output to a given total sumW at the end
 public:
  NormalizingSelector(char const* name) : EventSelector(name) {}
  ~NormalizingSelector() {}

  void finalize() override;

  void setNormalization(double norm, char const* normCut) { norm_ = norm; normCut_ = normCut; }

 protected:
  double norm_{1.};
  TString normCut_{""};
};

#endif
