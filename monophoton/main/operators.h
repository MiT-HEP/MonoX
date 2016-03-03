#ifndef operators_h
#define operators_h

#include "TreeEntries_simpletree.h"

#include "TH1.h"
#include "TH2.h"

#include <bitset>

//--------------------------------------------------------------------
// Base classes
//--------------------------------------------------------------------

class Operator {
 public:
  Operator(char const* name) : name_(name) {}
  virtual ~Operator() {}
  char const* name() const { return name_.Data(); }

  virtual bool operator()(simpletree::Event const&, simpletree::Event&) = 0;

  virtual void addBranches(TTree& skimTree) {}

 protected:
  TString name_;
};

class Cut : public Operator {
 public:
  Cut(char const* name) : Operator(name), result_(false), ignoreDecision_(false) {}
  virtual ~Cut() {}

  bool operator()(simpletree::Event const&, simpletree::Event&) override;

  void registerCut(TTree& cutsTree) { cutsTree.Branch(name_, &result_, name_ + "/O"); }
  void setIgnoreDecision(bool b) { ignoreDecision_ = b; }

 protected:
  virtual bool pass(simpletree::Event const&, simpletree::Event&) = 0;

 private:
  bool result_;
  bool ignoreDecision_;
};

class Modifier : public Operator {
 public:
  Modifier(char const* name) : Operator(name) {}
  virtual ~Modifier() {}

  bool operator()(simpletree::Event const&, simpletree::Event&) override;

 protected:
  virtual void apply(simpletree::Event const&, simpletree::Event&) = 0;
};

//--------------------------------------------------------------------
// Cuts
//--------------------------------------------------------------------

class HLTPhoton165HE10 : public Cut {
 public:
  HLTPhoton165HE10(char const* name = "HLTPhoton165HE10") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const& _event, simpletree::Event&) override { return _event.hlt[simpletree::kPhoton165HE10].pass; }
};

class HLTEle27eta2p1WPLooseGsf : public Cut {
 public:
  HLTEle27eta2p1WPLooseGsf(char const* name = "HLTEle27eta2p1WPLooseGsf") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const& _event, simpletree::Event&) override { return _event.hlt[simpletree::kEle27Loose].pass; }
};

class HLTIsoMu27 : public Cut {
 public:
  HLTIsoMu27(char const* name = "HLTIsoMu27") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const& _event, simpletree::Event&) override { return _event.hlt[simpletree::kMu27].pass; }
};

class MetFilters : public Cut {
 public:
  MetFilters(char const* name = "MetFilters") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const& _event, simpletree::Event&) override { return _event.metFilters.pass(); }
};

class PhotonSelection : public Cut {
 public:
  enum Selection {
    HOverE,
    Sieie,
    CHIso,
    NHIso,
    PhIso,
    EVeto,
    MIP49,
    Time,
    SieieNonzero,
    NoisyRegion,
    Sieie12,
    Sieie15,
    CHIso11,
    NHIso11,
    PhIso3,
    NHIsoTight,
    PhIsoTight,
    CHWorstIso,
    CHWorstIso11,
    nSelections
  };

  PhotonSelection(char const* name = "PhotonSelection") : Cut(name) {}

  void addBranches(TTree& skimTree) override;

  void addSelection(bool, unsigned, unsigned = nSelections, unsigned = nSelections);
  void addVeto(bool, unsigned, unsigned = nSelections, unsigned = nSelections);
  void setMinPt(double minPt) { minPt_ = minPt; }
  void setWP(unsigned wp) { wp_ = wp; }

  double ptVariation(simpletree::Photon const&, bool up);

 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;
  int selectPhoton(simpletree::Photon const&);

  double minPt_{175.};
  unsigned wp_{1}; // 1 -> medium
  float ptVarUp_[simpletree::Particle::array_data::NMAX];
  float ptVarDown_[simpletree::Particle::array_data::NMAX];
  // Will select photons based on the AND of the elements.
  // Within each element, multiple bits are considered as OR.
  typedef std::bitset<nSelections> BitMask;
  typedef std::pair<bool, BitMask> SelectionMask; // pass/fail & bitmask
  std::vector<SelectionMask> selections_;
  std::vector<SelectionMask> vetoes_;
};

class ElectronVeto : public Cut {
 public:
  ElectronVeto(char const* name = "ElectronVeto") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;
};

class MuonVeto : public Cut {
 public:
  MuonVeto(char const* name = "MuonVeto") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;
};

class TauVeto : public Cut {
 public:
  TauVeto(char const* name = "TauVeto") : Cut(name) {}
 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;
};

class PhotonMetDPhi : public Cut {
 public:
  PhotonMetDPhi(char const* name = "PhotonMetDPhi") : Cut(name) {}
  void addBranches(TTree& skimTree) override;
 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;

  float dPhi_{0.};
};

class JetMetDPhi : public Cut {
 public:
  JetMetDPhi(char const* name = "JetMetDPhi") : Cut(name) {}
  void addBranches(TTree& skimTree) override;

  void setPassIfIsolated(bool p) { passIfIsolated_ = p; }

 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;

  float dPhi_{0.};
  float dPhiCorrUp_{0.};
  float dPhiCorrDown_{0.};
  bool passIfIsolated_{true};
};

class LeptonSelection : public Cut {
 public:
  LeptonSelection(char const* name = "LeptonSelection") : Cut(name) {}

  void setN(unsigned nEl, unsigned nMu) { nEl_ = nEl; nMu_ = nMu; }
 protected:
  bool pass(simpletree::Event const&, simpletree::Event&) override;

  unsigned nEl_{0};
  unsigned nMu_{0};
};

//--------------------------------------------------------------------
// Modifiers
//--------------------------------------------------------------------

class JetCleaning : public Modifier {
 public:
  enum Collection {
    kPhotons,
    kElectrons,
    kMuons,
    kTaus,
    nCollections
  };

  JetCleaning(char const* name = "JetCleaning") : Modifier(name) { cleanAgainst_.set(); }

  void setCleanAgainst(Collection col, bool c) { cleanAgainst_.set(col, c); }
  
 protected:
  void apply(simpletree::Event const&, simpletree::Event&) override;

  std::bitset<nCollections> cleanAgainst_{};
};

class CopyMet : public Modifier {
 public:
  CopyMet(char const* name = "CopyMet") : Modifier(name) {}
 protected:
  void apply(simpletree::Event const& event, simpletree::Event& outEvent) override { outEvent.t1Met = event.t1Met; }
};

class LeptonRecoil : public Modifier {
  enum Collection {
    kElectrons,
    kMuons,
    nCollections
  };

 public:
  LeptonRecoil(char const* name = "LeptonRecoil") : Modifier(name), collection_(nCollections) {}
  void addBranches(TTree& skimTree) override;

 protected:
  void apply(simpletree::Event const&, simpletree::Event&) override;

  Collection collection_;
  float recoil_;
  float recoilPhi_;
};

class UniformWeight : public Modifier {
 public:
  UniformWeight(double weight, char const* name = "UniformWeight") : Modifier(name), weight_(weight) {}
  void addBranches(TTree& skimTree) override;

  void setUncertainty(double delta) { weightUncert_ = delta; }

 protected:
  void apply(simpletree::Event const&, simpletree::Event& _outEvent) override { _outEvent.weight *= weight_; }
  
  double weight_;
  double weightUncert_;
};

class PtWeight : public Modifier {
 public:
  PtWeight(TH1* factors, char const* name = "PtWeight") : Modifier(name), factors_(factors) {}
  void addBranches(TTree& skimTree) override;

  void setUncertaintyUp(TH1* delta) { uncertUp_ = delta; }
  void setUncertaintyDown(TH1* delta) { uncertDown_ = delta; }

 protected:
  void apply(simpletree::Event const&, simpletree::Event& _outEvent) override;

  TH1* factors_{0};
  TH1* uncertUp_{0};
  TH1* uncertDown_{0};
  double weightUncertUp_;
  double weightUncertDown_;
};

class IDSFWeight : public Modifier {
 public:
  enum Object {
    kPhoton,
    kElectron,
    kMuon,
    nObjects
  };

  IDSFWeight(Object obj, TH2* factors, char const* name = "IDSFWeight") : Modifier(name), object_(obj), factors_(factors) {}

 protected:
  void apply(simpletree::Event const&, simpletree::Event& _outEvent) override;

  Object object_;
  TH2* factors_;
};

class NPVWeight : public Modifier {
 public:
  NPVWeight(TH1* factors, char const* name = "NPVWeight") : Modifier(name), factors_(factors) {}
 protected:
  void apply(simpletree::Event const&, simpletree::Event& _outEvent) override;

  TH1* factors_;
};

class KFactorCorrection : public Modifier {
 public:
  KFactorCorrection(char const* name = "KFactorCorrection") : Modifier(name) {}

  void addPtBin(double ptmin, double kfactor) { kfactors_.emplace_back(ptmin, kfactor); }
  void setCorrection(TH1*);
 protected:
  void apply(simpletree::Event const&, simpletree::Event& _outEvent) override;

  std::vector<std::pair<double, double>> kfactors_;
};

#endif
