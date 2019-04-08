#include "Operators.h"

class TPOperator : public Operator {
 public:
  TPOperator(TPEventType t, char const* name) : Operator(name), eventType_(t) {}

  bool exec(panda::EventMonophoton const& inEvent, panda::EventBase& outEvent) final {
    return tpexec(inEvent, static_cast<panda::EventTP&>(outEvent));
  }

  panda::ParticleCollection* getLooseTags(panda::EventTP&) const;
  panda::ParticleCollection* getTags(panda::EventTP&) const;
  panda::ParticleCollection* getProbes(panda::EventTP&) const;

 protected:
  virtual bool tpexec(panda::EventMonophoton const&, panda::EventTP&) = 0;

  TPEventType eventType_;
};

class TPCut : public TPOperator, public CutMixin {
  // Cut with EventTP
 public:
  TPCut(TPEventType t, char const* name) : TPOperator(t, name), CutMixin(name) {}

  TString expr() const override { return cutExpr(name_); }

 protected:
  bool tpexec(panda::EventMonophoton const&, panda::EventTP&) final;
  virtual bool pass(panda::EventMonophoton const&, panda::EventTP&) = 0;
};

class TPModifier : public TPOperator {
  // Modifier with EventTP
 public:
  TPModifier(TPEventType t, char const* name) : TPOperator(t, name) {}

 protected:
  bool tpexec(panda::EventMonophoton const&, panda::EventTP&) final;
  virtual void apply(panda::EventMonophoton const&, panda::EventTP&) = 0;
};

//--------------------------------------------------------------------
// Cuts
//--------------------------------------------------------------------

class TPLeptonPhoton : public TPCut {
 public:
  TPLeptonPhoton(TPEventType t, char const* name = "TPLeptonPhoton") : TPCut(t, name) {}

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void setMinProbePt(double d) { minProbePt_ = d; }
  void setMinTagPt(double d) { minTagPt_ = d; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventTP&) override;

  double minProbePt_{175.};
  double minTagPt_{15.};
  double chargedPFDR_{0.1};
  double chargedPFRelPt_{0.6};

  bool chargedPFVeto_[NMAX_PARTICLES];
  bool hasCollinearL_[NMAX_PARTICLES];
  float ptdiff_[NMAX_PARTICLES];
};

class TPDilepton : public TPCut {
 public:
  TPDilepton(TPEventType t, char const* name = "TPDilepton") : TPCut(t, name) {}

  void addBranches(TTree& skimTree) override;

  void setMinProbePt(double d) { minProbePt_ = d; }
  void setMinTagPt(double d) { minTagPt_ = d; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventTP&) override;

  double minProbePt_{15.};
  double minTagPt_{30.};

  int probeGenId_[NMAX_PARTICLES];
};

class TPOFLepton : public TPCut {
 public:
  TPOFLepton(TPEventType t, char const* name = "TPOFLepton") : TPCut(t, name) {}

  void addBranches(TTree& skimTree) override;

  void setMinProbePt(double d) { minProbePt_ = d; }
  void setMinTagPt(double d) { minTagPt_ = d; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventTP&) override;

  double minProbePt_{15.};
  double minTagPt_{30.};

  int probeGenId_[NMAX_PARTICLES];
};

class TPLeptonVeto : public TPCut {
 public:
  TPLeptonVeto(TPEventType t, char const* name = "TPLeptonVeto") : TPCut(t, name) {}
  
  void addBranches(TTree& skimTree) override;

  void setVetoElectrons(bool b) { vetoElectrons_ = b; }
  void setVetoMuons(bool b) { vetoMuons_ = b; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventTP&) override;

  bool vetoElectrons_{true};
  bool vetoMuons_{true};
  unsigned nElectrons_;
  unsigned nMuons_;
};

//--------------------------------------------------------------------
// Modifiers
//--------------------------------------------------------------------

class TPJetCleaning : public TPModifier {
  // JetCleaning for TP
  // For photons, only clean overlap with the leading
 public:
  TPJetCleaning(TPEventType t, char const* name = "TPJetCleaning") : TPModifier(t, name) {}
  ~TPJetCleaning() {}

  void setMinPt(double min) { minPt_ = min; }
  
 protected:
  void apply(panda::EventMonophoton const&, panda::EventTP&) override;

  double minPt_{30.};
};

class TPTriggerMatch : public TPModifier {
 public:
  enum Candidate {
    kProbe,
    kTag
  };

 TPTriggerMatch(TPEventType t, Candidate c, char const* name) : TPModifier(t, name), candidate_(c) {}
  ~TPTriggerMatch() {}

  void initialize(panda::EventMonophoton&) override;
  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;

  void addTriggerFilter(char const* filterName) { filterNames_.emplace_back(filterName); }

 protected:
  void apply(panda::EventMonophoton const& event, panda::EventTP& outEvent) override;

  Candidate candidate_;
  std::vector<TString> filterNames_{};
  bool matchResults_[NMAX_PARTICLES];
};
