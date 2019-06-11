#ifndef BaseOperator_h
#define BaseOperator_h

#include "Operator.h"

#include "TF1.h"

class BaseOperator : public Operator 
{
 public:
  BaseOperator(char const* name) : Operator(name) {}
};

class Cut : public BaseOperator, public CutMixin {
 public:
  Cut(char const* name) : BaseOperator(name), CutMixin(name) {}

  TString expr() const override { return cutExpr(name_); }

  bool exec(panda::EventBase const& inEvent, panda::EventBase& outEvent) final;

 protected:
  virtual bool pass(panda::EventBase const&, panda::EventBase&) = 0;
};

class Modifier : public BaseOperator {
 public:
  Modifier(char const* name) : BaseOperator(name) {}

  bool exec(panda::EventBase const& inEvent, panda::EventBase& outEvent) final;

 protected:
  virtual void apply(panda::EventBase const&, panda::EventBase&) = 0;
};

//--------------------------------------------------------------------
// Cuts
//--------------------------------------------------------------------

class HLTFilter : public Cut {
 public:
  HLTFilter(char const* name = "PATHNAME");
  ~HLTFilter();

  void initialize(panda::EventBase& _event) override;
  void addBranches(TTree& skimTree) override;

 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  TString pathNames_{""};
  std::vector<UInt_t> tokens_;
  bool pass_{false};
};

class EventVeto : public Cut {
 public:
  EventVeto(char const* name = "EventVeto") : Cut(name) {}

  void addSource(char const* path);
  void addEvent(unsigned run, unsigned lumi, unsigned event);

  protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  typedef std::set<unsigned> EventContainer;
  typedef std::map<unsigned, EventContainer> LumiContainer;
  typedef std::map<unsigned, LumiContainer> RunContainer;

  RunContainer list_{};
};

// TODO HERE - SHOULD MOVE ALL GEN OPERATORS TO MONOPHOTON?

class GenPhotonVeto : public Cut {
  /* Veto event if it contains a prompt gen photon */
 public:
  GenPhotonVeto(char const* name = "GenPhotonVeto") : Cut(name) {}

  void setMinPt(double m) { minPt_ = m; }
  void setMinPartonDR(double m) { minPartonDR2_ = m * m; }

 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  double minPt_{130.}; // minimum pt of the gen photon to be vetoed
  double minPartonDR2_{0.5 * 0.5}; // minimum dR wrt any parton of the gen photon to be vetoed
};

class PartonFlavor : public Cut {
  /* Select events with specified parton ids */
 public:
  PartonFlavor(char const* name = "PartonFlavor") : Cut(name) {}

  void setRejectedPdgId(unsigned id) { rejectedId_ = id; }
  void setRequiredPdgId(unsigned id) { requiredId_ = id; }

  unsigned getRejectedPdgId() const { return rejectedId_; }
  unsigned getRequiredPdgId() const { return requiredId_; }

 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  unsigned rejectedId_{0};
  unsigned requiredId_{0};
};

class GenPhotonPtTruncator : public Cut {
 public:
  GenPhotonPtTruncator(char const* name = "GenPhotonPtTruncator") : Cut(name) {}

  void setPtMin(double min) { min_ = min; }
  void setPtMax(double max) { max_ = max; }
 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  double min_{0.};
  double max_{500.};
};

class GenHtTruncator : public Cut {
 public:
  GenHtTruncator(char const* name = "GenHtTruncator") : Cut(name) {}

  void addBranches(TTree& skimTree) override;

  void setHtMin(double min) { min_ = min; }
  void setHtMax(double max) { max_ = max; }
 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  float ht_{-1.};
  double min_{0.};
  double max_{100.};
};

class GenBosonPtTruncator : public Cut {
 public:
  GenBosonPtTruncator(char const* name = "GenBosonPtTruncator") : Cut(name) {}

  void addBranches(TTree& skimTree) override;

  void setPtMin(double min) { min_ = min; }
  void setPtMax(double max) { max_ = max; }
 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;

  float pt_{-1.};
  double min_{0.};
  double max_{50.};
};

class GenParticleSelection : public Cut {
 public:
  GenParticleSelection(char const* name = "GenParticleSelection") : Cut(name) {}
  
  void setPdgId(int pdgId) { pdgId_ = pdgId; }
  void setMinPt(double minPt) { minPt_ = minPt; }
  void setMaxPt(double maxPt) { maxPt_ = maxPt; }
  void setMinEta(double minEta) { minEta_ = minEta; }
  void setMaxEta(double maxEta) { maxEta_ = maxEta; }

 protected:
  bool pass(panda::EventBase const&, panda::EventBase&) override;
  
  int pdgId_{22};
  double minPt_{140.};
  double maxPt_{6500.};
  double minEta_{0.};
  double maxEta_{5.};
};

//--------------------------------------------------------------------
// Modifiers
//--------------------------------------------------------------------

class PartonKinematics : public Modifier {
  /* Save parton level photon and met kinematics. */
 public:
  PartonKinematics(char const* name = "PartonKinematics") : Modifier(name) {}
  
  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventBase const&, panda::EventBase&) override;
  
  float phoPt_{-1.};
  float phoEta_{-1.};
  float phoPhi_{-1.};
  
  float metPt_{-1.};
  float metPhi_{-1.};
};

class ConstantWeight : public Modifier {
 public:
  ConstantWeight(double weight, char const* name = "ConstantWeight") : Modifier(name), weight_(weight) {}
  void addBranches(TTree& skimTree) override;

  void setUncertaintyUp(double delta) { weightUp_ = 1. + delta; }
  void setUncertaintyDown(double delta) { weightDown_ = 1. - delta; }

 protected:
  void apply(panda::EventBase const&, panda::EventBase& outEvent) override { outEvent.weight *= weight_; }
  
  double weight_;
  double weightUp_{-1.};
  double weightDown_{-1.};
};

class NNPDFVariation : public Modifier {
 public:
  NNPDFVariation(char const* name = "NNPDFVariation") : Modifier(name) {}

  void setRescale(double scale) { rescale_ = scale; }
  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventBase const&, panda::EventBase&) override;

  double rescale_{1.};
  double weightUp_;
  double weightDown_;
};

class GJetsDR : public Modifier {
 public:
  GJetsDR(char const* name = "GJetsDR") : Modifier(name) {}

  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventBase const&, panda::EventBase&) override;

  float minDR_;
};

class PUWeight : public Modifier {
 public:
  PUWeight(TH1* factors, char const* name = "PUWeight") : Modifier(name), factors_(factors) {}

  void addBranches(TTree& _skimTree) override;

 protected:
  void apply(panda::EventBase const&, panda::EventBase&) override;

  TH1* factors_;
  double weight_;
};

#endif
