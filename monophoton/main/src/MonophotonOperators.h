#ifndef MonophotonOperator_h
#define MonophotonOperator_h

#include "Operator.h"

#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TRandom3.h"

#include "TDirectory.h"

#include "fastjet/JetDefinition.hh"

#include "PandaTree/Objects/interface/EventMonophoton.h"

#include <bitset>
#include <map>
#include <vector>
#include <utility>
#include <functional>

enum LeptonFlavor {
  lElectron,
  lMuon,
  nLeptonFlavors
};

enum MetSource {
  kInMet,
  kOutMet
};

class MonophotonOperator : public Operator {
 public:
  MonophotonOperator(char const* name) : Operator(name) {}

  void initialize(panda::EventBase& event) final {
    monophinitialize(static_cast<panda::EventMonophoton&>(event));
  }
  bool exec(panda::EventBase const& inEvent, panda::EventBase& outEvent) final {
    return monophexec(static_cast<panda::EventMonophoton const&>(inEvent), static_cast<panda::EventMonophoton&>(outEvent));
  }

 protected:
  virtual void monophinitialize(panda::EventMonophoton&) {}
  virtual bool monophexec(panda::EventMonophoton const&, panda::EventMonophoton&) = 0;
};

class MonophotonCut : public MonophotonOperator, public CutMixin {
 public:
  MonophotonCut(char const* name) : MonophotonOperator(name), CutMixin(name) {}

  TString expr() const override { return cutExpr(name_); }

 protected:
  bool monophexec(panda::EventMonophoton const&, panda::EventMonophoton&) final;
  virtual bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) = 0;
};

class MonophotonModifier : public MonophotonOperator {
 public:
  MonophotonModifier(char const* name) : MonophotonOperator(name) {}

 protected:
  bool monophexec(panda::EventMonophoton const&, panda::EventMonophoton&) final;
  virtual void apply(panda::EventMonophoton const&, panda::EventMonophoton&) = 0;
};

//--------------------------------------------------------------------
// Cuts
//--------------------------------------------------------------------

class PhotonSelection : public MonophotonCut {
 public:
  enum Selection {
    Pt,
    IsBarrel,
    HOverE,
    Sieie,
    NHIso,
    PhIso,
    CHIso,
    CHIsoMax,
    EVeto,
    CSafeVeto,
    ChargedPFVeto,
    MIP49,
    Time,
    SieieNonzero,
    SipipNonzero,
    NoisyRegion,
    E2E995,
    Sieie08,
    Sieie12,
    Sieie15,
    Sieie20,
    Sipip08,
    CHIso11,
    CHIsoMax11,
    NHIsoLoose,
    PhIsoLoose,
    NHIsoTight,
    PhIsoTight,
    Sieie05,
    Sipip05,
    R9Unity,
    nSelections
  };

  // Will select photons based on the AND of the elements.
  // Within each element, multiple bits are considered as OR.
  typedef std::bitset<nSelections> BitMask;
  typedef std::pair<bool, BitMask> SelectionMask; // pass/fail & bitmask

  static TString const selectionName[nSelections];
  static TString selToString(SelectionMask);

  PhotonSelection(char const* name = "PhotonSelection") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;
  void registerCut(TTree& cutsTree) override;

  // bool->true: add photon condition "pass one of the selections"
  // bool->false: add photon condition "fail one of the selections"
  // Photons are saved when they match all the conditions
  void addSelection(bool, unsigned, unsigned = nSelections, unsigned = nSelections);
  void resetSelection() { selections_.clear(); }
  void removeSelection(unsigned, unsigned = nSelections, unsigned = nSelections);
  // skip event if there is a photon passing the selection (bool->true) or failing (bool->false)
  void addVeto(bool, unsigned, unsigned = nSelections, unsigned = nSelections);
  void resetVeto() { vetoes_.clear(); }
  void removeVeto(unsigned, unsigned = nSelections, unsigned = nSelections);

  void addNoiseMask(unsigned subdet, int ix, int iy) { noiseMap_.emplace(subdet, ix, iy); }

  void setIncludeLowPt(bool i) { includeLowPt_ = i; }
  // void setUseOriginalPt(bool b) { useOriginalPt_ = b; }

  void setMinPt(double minPt) { minPt_ = minPt; }
  void setMaxPt(double maxPt) { maxPt_ = maxPt; }
  void setIDTune(panda::XPhoton::IDTune t) { idTune_ = t; }
  void setWP(unsigned wp) { wp_ = wp; }
  void setN(unsigned n) { nPhotons_ = n; }
  double ptVariation(panda::XPhoton const&, double shift);

 protected:
  void monophinitialize(panda::EventMonophoton&) override;
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;
  int selectPhoton(panda::XPhoton const&, unsigned idx);

  double minPt_{220.};
  double maxPt_{6500.};
  bool ebOnly_{true};
  panda::XPhoton::IDTune idTune_{panda::XPhoton::kFall17};
  unsigned wp_{0}; // 0 -> loose, 1 -> medium
  unsigned nPhotons_{1}; // required number of photons
  float ptVarUp_[NMAX_PARTICLES];
  float ptVarDown_[NMAX_PARTICLES];

  bool includeLowPt_{false};
  // specific to 03Feb2017 re-miniaod: scale output pt values to original / GS-fixed
  bool useOriginalPt_{false};

  std::vector<SelectionMask> selections_;
  std::vector<SelectionMask> vetoes_;
  bool cutRes_[nSelections][NMAX_PARTICLES];

  std::set<std::tuple<unsigned, int, int>> noiseMap_; // subdet(0:EB, 1:EE-, 2:EE+), ix, iy

  unsigned size_{0};
  bool nominalResult_{false};
  std::vector<panda::PFCand const*> chargedCands_;
  bool chargedPFVeto_[NMAX_PARTICLES];
};

class TauVeto : public MonophotonCut {
 public:
  TauVeto(char const* name = "TauVeto") : MonophotonCut(name) {}
  void addInputBranch(panda::utils::BranchList&) override;
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;
};

class EcalCrackVeto : public MonophotonCut {
 public:
  EcalCrackVeto(char const* name = "EcalCrackVeto") : MonophotonCut(name) {}
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void setMinPt(double minPt) { minPt_ = minPt; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;
  
  double minPt_{30.};
  Bool_t ecalCrackVeto_{true};
};

class LeptonMt : public MonophotonCut {
 public:
  LeptonMt(char const* name = "LeptonMt") : MonophotonCut(name) {}

  void setFlavor(LeptonFlavor flav) { flavor_ = flav; }
  void setMin(double min) { min_ = min; }
  void setMax(double max) { max_ = max; }

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void setOnlyLeading(bool b) { onlyLeading_ = b; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  LeptonFlavor flavor_;

  bool onlyLeading_{true};
  double min_{0.};
  double max_{14000.};
  float mt_[NMAX_PARTICLES];
};

class Mass : public MonophotonCut {
 public:
  Mass(char const* name = "Mass") : MonophotonCut(name) {}

  void setPrefix(char const* p) { prefix_ = p; }
  void setCollection1(Collection c) { col_[0] = c; }
  void setCollection2(Collection c) { col_[1] = c; }
  void setMin(double min) { min_ = min; }
  void setMax(double max) { max_ = max; }

  void addBranches(TTree& skimTree) override;

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  TString prefix_{"generic"};
  Collection col_[2]{nCollections, nCollections};

  float mass_{-1.};
  float pt_{-1.};
  float eta_{-99.};
  float phi_{-99.};
  double min_{0.};
  double max_{14000.};
};

class OppositeSign : public MonophotonCut {
 public:
  OppositeSign(char const* name = "OppositeSign") : MonophotonCut(name) {}

  void setPrefix(char const* p) { prefix_ = p; }
  void setCollection1(Collection c) { col_[0] = c; }
  void setCollection2(Collection c) { col_[1] = c; }

  void addBranches(TTree& skimTree) override;

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  TString prefix_{"generic"};
  Collection col_[2]{nCollections, nCollections};

  bool oppSign_{0};
};

class BjetVeto : public MonophotonCut {
 public:
  BjetVeto(char const* name = "BjetVeto") : MonophotonCut(name), bjets_("bjets") {}

  void addBranches(TTree& skimTree) override;
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  panda::JetCollection bjets_;
};

class MetVariations; // defined below
class JetCleaning; // defined below

class PhotonMetDPhi : public MonophotonCut {
 public:
  PhotonMetDPhi(char const* name = "PhotonMetDPhi") : MonophotonCut(name) {}
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;
  void registerCut(TTree& cutsTree) override { cutsTree.Branch(name_, &nominalResult_, name_ + "/O"); }

  void setCutValue(double v) { cutValue_ = v; }
  void setMetSource(MetSource s) { metSource_ = s; }
  void setMetVariations(MetVariations* v) { metVar_ = v; }
  void invert(bool i) { invert_ = i; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  MetSource metSource_{kOutMet};

  float dPhi_{0.};
  float dPhiJECUp_{0.};
  float dPhiJECDown_{0.};
  float dPhiGECUp_{0.};
  float dPhiGECDown_{0.};
  float dPhiUnclUp_{0.};
  float dPhiUnclDown_{0.};
  /* float dPhiJER_{0.}; */
  /* float dPhiJERUp_{0.}; */
  /* float dPhiJERDown_{0.}; */
  MetVariations* metVar_{0};

  double cutValue_{0.5};
  bool nominalResult_{false};
  bool invert_{false};
};

class LeptonRecoil;

class JetMetDPhi : public MonophotonCut {
 public:
  JetMetDPhi(char const* name = "JetMetDPhi") : MonophotonCut(name) {}
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;
  void registerCut(TTree& cutsTree) override { cutsTree.Branch(name_, &nominalResult_, name_ + "/O"); }

  void setMetSource(MetSource s) { metSource_ = s; }
  void setPassIfIsolated(bool p) { passIfIsolated_ = p; }
  void setMetVariations(MetVariations* v) { metVar_ = v; }
  /* void setJetCleaning(JetCleaning* jcl) { jetCleaning_ = jcl; } */

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  float dPhi_{0.};
  float dPhiJECUp_{0.};
  float dPhiJECDown_{0.};
  float dPhiGECUp_{0.};
  float dPhiGECDown_{0.};
  float dPhiUnclUp_{0.};
  float dPhiUnclDown_{0.};
  /* float dPhiJER_{0.}; */
  /* float dPhiJERUp_{0.}; */
  /* float dPhiJERDown_{0.}; */

  MetSource metSource_{kOutMet};
  bool passIfIsolated_{true};
  MetVariations* metVar_{0};
  /* JetCleaning* jetCleaning_{0}; */

  bool nominalResult_;
};

class LeptonSelection : public MonophotonCut {
 public:
  LeptonSelection(char const* name = "LeptonSelection");
  ~LeptonSelection();
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  enum OutMuonType {
    kMuJustLoose,
    kMuTrigger16Safe,
    kMuTrigger17Safe
  };

  enum OutElectronType {
    kElJustLoose,
    kElTrigger16Safe,
    kElTrigger17Safe
  };

  void setN(unsigned nEl, unsigned nMu) { nEl_ = nEl; nMu_ = nMu; }
  void setStrictMu(bool doStrict) { strictMu_ = doStrict; }
  void setStrictEl(bool doStrict) { strictEl_ = doStrict; }
  void setRequireMedium(bool require, unsigned btof = false) { requireMedium_ = require; mediumBtoF_ = btof; }
  void setRequireTight(bool require) { requireTight_ = require; }
  void setRequireHWWTight(bool require) { requireHWWTight_ = require; }
  void setOutMuonType(OutMuonType type) { outMuonType_ = type; }
  void setOutElectronType(OutElectronType type) { outElectronType_ = type; }
  panda::MuonCollection* getFailingMuons() { return failingMuons_; }
  panda::ElectronCollection* getFailingElectrons() {return failingElectrons_; }

 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  bool strictMu_{true};
  bool strictEl_{true};
  bool requireMedium_{true};
  bool mediumBtoF_{false};
  bool requireTight_{true};
  bool requireHWWTight_{false};
  OutMuonType outMuonType_{kMuJustLoose};
  OutElectronType outElectronType_{kElJustLoose};
  unsigned nEl_{0};
  unsigned nMu_{0};

  double minPtMu_{30.};
  double minPtEl_{30.};

  panda::MuonCollection* failingMuons_{0};
  panda::ElectronCollection* failingElectrons_{0};
};

class FakeElectron : public MonophotonCut {
  // Select electrons passing veto but failing loose with pt > 30
  // Overlaps with photons are skipped
 public:
  FakeElectron(char const* name = "FakeElectron") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;
};

class Met : public MonophotonCut {
 public:
  Met(char const* name = "Met") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  void setMetSource(MetSource s) { metSource_ = s; }
  void setThreshold(double min) { min_ = min; }
  void setCeiling(double max) { max_ = max; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton& outEvent) override;

  MetSource metSource_{kOutMet};
  double min_{170.};
  double max_{6500.};
};

class PhotonPtOverMet : public MonophotonCut {
 public:
  PhotonPtOverMet(char const* name = "PhotonPtOverMet") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  void setMetSource(MetSource s) { metSource_ = s; }
  void setThreshold(double min) { min_ = min; }
  void setCeiling(double max) { max_ = max; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton& outEvent) override;

  MetSource metSource_{kOutMet};
  double min_{0.};
  double max_{1.4};
};

class PhotonMt;

class MtRange : public MonophotonCut {
 public:
  MtRange(char const* name = "MtRange") : MonophotonCut(name) {}

  void setRange(double min, double max) { min_ = min; max_ = max; }
  void setCalculator(PhotonMt const* calc) { calc_ = calc; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  double min_{0.};
  double max_{6500.};
  PhotonMt const* calc_{0};
};

class HighPtJetSelection : public MonophotonCut {
 public:
  HighPtJetSelection(char const* name = "HighPtJetSelection") : MonophotonCut(name) {}

  void setJetPtCut(double min) { min_ = min; }
  void setNMin(unsigned n) { nMin_ = n; }
  void setNMax(unsigned n) { nMax_ = n; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  double min_{100.};
  unsigned nMin_{1};
  unsigned nMax_{100};
};

class DijetSelection : public MonophotonCut {
  // select events with two opposite-hemisphere jets with pT thresholds
 public:
  DijetSelection(char const* name = "DijetSelection") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  enum JetType {
    jReco,
    jGen,
    nJetTypes
  };

  void setMinPt1(double min) { minPt1_ = min; }
  void setMinPt2(double min) { minPt2_ = min; }
  void setMinDEta(double min) { minDEta_ = min; }
  void setMinMjj(double min) { minMjj_ = min; }
  void setSavePassing(bool b) { savePassing_ = b; }
  void setJetType(JetType j) { jetType_ = j; }
  void setLeadingOnly(bool b) { leadingOnly_ = b; }
  void setDEtajjReweight(TFile* _plotsFile);

  void addBranches(TTree& skimTree) override;

  unsigned getNDijet() const { return nDijet_; }
  unsigned getNDijetPassing() const { return nDijetPassing_; }
  double getDEtajj(unsigned i) const { return dEtajj_[i]; }
  double getDEtajjPassing(unsigned i) const { return dEtajjPassing_[i]; }
  
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  double minPt1_{50.};
  double minPt2_{50.};
  double minDEta_{3.};
  double minMjj_{800.};
  bool savePassing_{true};
  JetType jetType_{jReco};
  bool leadingOnly_{false}; // use leading two jets only

  unsigned nDijet_{0};
  float dEtajj_[NMAX_PARTICLES]{};
  float mjj_[NMAX_PARTICLES]{};
  unsigned ij1_[NMAX_PARTICLES]{};
  unsigned ij2_[NMAX_PARTICLES]{};
  unsigned nDijetPassing_{0};
  float dEtajjPassing_[NMAX_PARTICLES]{};
  float mjjPassing_[NMAX_PARTICLES]{};
  unsigned ij1Passing_[NMAX_PARTICLES]{};
  unsigned ij2Passing_[NMAX_PARTICLES]{};
  TH1D* reweightSource_{0};
  double detajjReweight_;
};

class MetFilters : public MonophotonCut {
 public:
  MetFilters(char const* name = "MetFilters") : MonophotonCut(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  void allowHalo() { halo_ = true; }
 protected:
  bool pass(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  bool halo_{false};
};

//--------------------------------------------------------------------
// Modifiers
//--------------------------------------------------------------------

// Does not work in 004!!
class TriggerMatch : public MonophotonModifier {
 public:
  TriggerMatch(char const* name, Collection col) : MonophotonModifier(name), collection_(col) {}
  ~TriggerMatch() {}

  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;

  void addTriggerFilter(char const* filterName) { filterNames_.emplace_back(filterName); }

 protected:
  void monophinitialize(panda::EventMonophoton&) override;
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  Collection collection_{nCollections};
  std::vector<TString> filterNames_{};
  bool matchResults_[NMAX_PARTICLES];
};

class PFMatch : public MonophotonModifier {
  /*Match a PF charged hadron to a photon (hardest within the dR cone).*/
  
 public:
  PFMatch(char const* name = "PFMatch") : MonophotonModifier(name) {}
  ~PFMatch() {}

  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;

  void setDR(double dr) { dr_ = dr; }

 protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  double dr_{0.1};
  unsigned short matchedPtype_[NMAX_PARTICLES]{};
  float matchedDR_[NMAX_PARTICLES]{};
  float matchedRelPt_[NMAX_PARTICLES]{};
};

class TriggerEfficiency : public MonophotonModifier {
 public:
  TriggerEfficiency(char const* name = "TriggerEfficiency") : MonophotonModifier(name) {}
  ~TriggerEfficiency() { delete formula_; }
  void addBranches(TTree& skimTree) override;
  
  void setMinPt(double minPt) { minPt_ = minPt; }
  void setFormula(char const* formula);
  void setUpFormula(char const* formula);
  void setDownFormula(char const* formula);

 protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  double minPt_{0.};
  TF1* formula_{0};
  TF1* upFormula_{0};
  TF1* downFormula_{0};
  double weight_;
  double reweightUp_;
  double reweightDown_;
};

class ExtraPhotons : public MonophotonModifier {
 public:
  ExtraPhotons(char const* name = "ExtraPhotons") : MonophotonModifier(name) {}

  void setMinPt(double minPt) { minPt_ = minPt; }

 protected:
  double minPt_{30.};
  
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;
};

class JetCleaning : public MonophotonModifier {
  // For photons, only clean overlap with the leading
 public:
  JetCleaning(char const* name = "JetCleaning");
  ~JetCleaning() { /*delete jer_; delete rndm_;*/ }
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void useTightWP(bool b) { useTightWP_ = b; }
  void setCleanAgainst(Collection col, bool c) { cleanAgainst_.set(col, c); }
  //  void setJetResolution(char const* sourcePath);
  void setMinPt(double min) { minPt_ = min; }
  void setPUIdWP(int i) { puidWP_ = i; }

  /* double ptScaled(unsigned iJ) const { return ptScaled_[iJ]; } */
  /* double ptScaledUp(unsigned iJ) const { return ptScaledUp_[iJ]; } */
  /* double ptScaledDown(unsigned iJ) const { return ptScaledDown_[iJ]; } */

  static double const puidCuts[4][4][4]; // WP x pt x eta
  static bool passPUID(int wp, panda::Jet const& jet);

 protected:
  void monophinitialize(panda::EventMonophoton&) override;
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;
  
  std::bitset<nCollections> cleanAgainst_{};

  // will copy jer branches
  /* float ptScaled_[NMAX_PARTICLES]; */
  /* float ptScaledUp_[NMAX_PARTICLES]; */
  /* float ptScaledDown_[NMAX_PARTICLES]; */

  //  JER* jer_{0};
  //  TRandom3* rndm_{0};
  double minPt_{30.};
  bool useTightWP_{false};
  int puidWP_{3}; // 0: loose, 1: medium, 2: tight, 3: some old WP
};

class PhotonJetDPhi : public MonophotonModifier {
 public:
  PhotonJetDPhi(char const* name = "PhotonJetDPhi") : MonophotonModifier(name) {}
  void addBranches(TTree& skimTree) override;

  void setMetVariations(MetVariations* v) { metVar_ = v; }
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  float dPhi_[NMAX_PARTICLES];
  float minDPhi_[NMAX_PARTICLES];
  float minDPhiJECUp_[NMAX_PARTICLES];
  float minDPhiJECDown_[NMAX_PARTICLES];
  MetVariations* metVar_{0};
};

class CopyMet : public MonophotonModifier {
 public:
  CopyMet(char const* name = "CopyMet") : MonophotonModifier(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  void setUseGSFix(bool b) { useGSFix_ = b; }
 protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  bool useGSFix_{true};
};

class CopySuperClusters : public MonophotonModifier {
 public:
  CopySuperClusters(char const* name = "CopySuperClusters") : MonophotonModifier(name) {}
  
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;
};

class AddTrailingPhotons : public MonophotonModifier {
  // Keep photons[0] and add all other loose photons to output
 public:
  AddTrailingPhotons(char const* name = "AddTrailingPhotons") : MonophotonModifier(name) {}

protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;
};

class PhotonMt : public MonophotonModifier {
 public:
  PhotonMt(char const* name = "PhotonMt") : MonophotonModifier(name) {}
  void addBranches(TTree& skimTree) override;
  
  double getMt(unsigned iP) const { return mt_[iP]; }
 protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  float mt_[NMAX_PARTICLES];
};

class AddGenJets : public MonophotonModifier {
 public:
  AddGenJets(char const* name = "AddGenJets") : MonophotonModifier(name) {}

  void addInputBranch(panda::utils::BranchList&) override;

  void setMinPt(double minPt) { minPt_ = minPt; }
  void setMaxEta(double maxEta) { maxEta_ = maxEta; }
 protected:
  void apply(panda::EventMonophoton const& event, panda::EventMonophoton& outEvent) override;

  double minPt_{30.};
  double maxEta_{5.};
};

class LeptonRecoil : public MonophotonModifier {
 public:
  LeptonRecoil(char const* name = "LeptonRecoil") : MonophotonModifier(name), flavor_(nLeptonFlavors) {}
  void addBranches(TTree& skimTree) override;

  void setFlavor(LeptonFlavor flav) { flavor_ = flav; }

  TVector2 realMet() const { TVector2 v; v.SetMagPhi(realMet_, realPhi_); return v; }
  TVector2 realMetCorr(int corr) const;
  TVector2 realMetUncl(int corr) const;

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  LeptonFlavor flavor_;
  MetVariations* metVar_{0};

  float realMet_;
  float realPhi_;
  float realMetCorrUp_;
  float realPhiCorrUp_;
  float realMetCorrDown_;
  float realPhiCorrDown_;
  float realMetUnclUp_;
  float realPhiUnclUp_;
  float realMetUnclDown_;
  float realPhiUnclDown_;
};

class PhotonFakeMet : public MonophotonModifier {
 public:
  PhotonFakeMet(char const* name = "PhotonFakeMet") : MonophotonModifier(name), rand_(12345) {}
  void addBranches(TTree& skimTree) override;

  void setFraction(float frac) { fraction_ = frac; }

  TVector2 realMet() const { TVector2 v; v.SetMagPhi(realMet_, realPhi_); return v; }
  TVector2 realMetCorr(int corr) const;
  TVector2 realMetUncl(int corr) const;

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  float fraction_{-1.};
  TRandom3 rand_;
  MetVariations* metVar_{0};

  float realPhoPt_[NMAX_PARTICLES];
  float realMet_;
  float realPhi_;
  float realMetCorrUp_;
  float realPhiCorrUp_;
  float realMetCorrDown_;
  float realPhiCorrDown_;
  float realMetUnclUp_;
  float realPhiUnclUp_;
  float realMetUnclDown_;
  float realPhiUnclDown_;
};

class MetVariations : public MonophotonModifier {
 public:
  MetVariations(char const* name = "MetVariations") : MonophotonModifier(name) {}
  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void setMetSource(MetSource s) { metSource_ = s; }
  void setPhotonSelection(PhotonSelection* sel) { photonSel_ = sel; }
  /* void setJetCleaning(JetCleaning* jcl) { jetCleaning_ = jcl; } */
  TVector2 gecUp() const { TVector2 v; v.SetMagPhi(metGECUp_, phiGECUp_); return v; }
  TVector2 gecDown() const { TVector2 v; v.SetMagPhi(metGECDown_, phiGECDown_); return v; }
  /* TVector2 jer() const { TVector2 v; v.SetMagPhi(metJER_, phiJER_); return v; } */
  /* TVector2 jerUp() const { TVector2 v; v.SetMagPhi(metJERUp_, phiJERUp_); return v; } */
  /* TVector2 jerDown() const { TVector2 v; v.SetMagPhi(metJERDown_, phiJERDown_); return v; } */

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;
  
  PhotonSelection* photonSel_{0};
  JetCleaning* jetCleaning_{0};
  float metGECUp_{0.};
  float phiGECUp_{0.};
  float metGECDown_{0.};
  float phiGECDown_{0.};
  /* float metJER_{0.}; */
  /* float phiJER_{0.}; */
  /* float metJERUp_{0.}; */
  /* float phiJERUp_{0.}; */
  /* float metJERDown_{0.}; */
  /* float phiJERDown_{0.}; */

  MetSource metSource_{kOutMet};
};

class PhotonPtWeight : public MonophotonModifier {
 public:
  enum PhotonType {
    kReco,
    kParton,
    kPostShower,
    nPhotonTypes
  };

  PhotonPtWeight(TObject* factors, char const* name = "PhotonPtWeight");
  ~PhotonPtWeight();

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void setPhotonType(unsigned t) { photonType_ = t; }
  void addVariation(char const* tag, TObject* corr);
  void useErrors(bool); // use errors of the nominal histogram weight for Up/Down variation

  double getWeight() const { return weight_; }
  double getVariation(TString const& var) const { return *varWeights_.at(var); }

  void computeWeight(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent);

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;

  double calcWeight_(TObject* source, double pt, int var = 0);

  TObject* nominal_;
  double weight_;
  bool usingErrors_{false};
  std::map<TString, TObject*> variations_;
  std::map<TString, double*> varWeights_;
  unsigned photonType_{kReco};
  int leptonCharge_{0};
};

class PhotonPtWeightSigned : public MonophotonModifier {
  // Rather non-generic operator to apply separate weights for W+ and W-
 public:

  PhotonPtWeightSigned(TObject* pfactors, TObject* nfactors, char const* name = "PhotonPtWeightSigned");
  ~PhotonPtWeightSigned() {}

  enum Sign {
    kPositive,
    kNegative,
    nSigns
  };

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

  void addVariation(char const* tag, TObject* pcorr, TObject* ncorr);
  void setPhotonType(unsigned t);
  void useErrors(bool); // use errors of the nominal histogram weight for Up/Down variation
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;
  
  std::unique_ptr<PhotonPtWeight> operators_[nSigns];
  double weight_;
  std::map<TString, std::unique_ptr<double>> varWeights_;
};

class IDSFWeight : public MonophotonModifier {
 public:
  enum Variable {
    kPt,
    kEta,
    kAbsEta,
    kNpv,
    nVariables
  };

  IDSFWeight(Collection obj, char const* name = "IDSFWeight") : MonophotonModifier(name), object_(obj) {}

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;
  void setVariable(Variable, Variable = nVariables);
  void setNParticles(unsigned _nP) { nParticles_ = _nP; }
  void addFactor(TH1* factor) { factors_.emplace_back(factor); }
  void addCustomCollection(panda::ParticleCollection* coll) { customCollection_ = coll; }
 protected:
  void applyParticle(unsigned iP, panda::EventMonophoton const& _event, panda::EventMonophoton& _outEvent);
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;

  panda::ParticleCollection* customCollection_{0};

  Collection object_;
  Variable variables_[2];
  unsigned nParticles_{1};
  std::vector<TH1*> factors_;
  double weight_{1.};
  double weightUp_{1.};
  double weightDown_{1.};
};

class VtxAdjustedJetProxyWeight : public PhotonPtWeight {
 public:
  VtxAdjustedJetProxyWeight(TH1* isoTFactor, TH2* isoVScore, TH1* noIsoTFactor, TH2* noIsoVScore, char const* name = "VtxAdjustedJetProxyWeight");
  
  void setRCProb(TH2* distribution, double chIsoCut);

  void addBranches(TTree& skimTree) override;
  void addInputBranch(panda::utils::BranchList&) override;

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;

  //  TH1* isoTFactor_; // N(fake jets) / N(jet proxies) - use nominal_ of PhotonPtWeight
  TH2* isoVScore_; // Score distribution of vertices with an isolated fake photon (score:pt)
  TH1* noIsoTFactor_; // N(noICH fake jets) / N(jet proxies)
  TH2* noIsoVScore_; // Score distribution of vertices with noICH fake photon (score:pt)
  TH1* rcProb_{0}; // Probability of a random 0.3 cone to have CH sumPT higher than the cut (:eta)

  //  float isoT_; - use weight_ of PhotonPtWeight
  float isoPVProb_;
  float noIsoT_;
  float noIsoPVProb_;
  float rc_;
};

class JetClustering : public MonophotonModifier {
 public:
  JetClustering(char const* name = "JetClustering") : MonophotonModifier(name), jets_("ak4Jets"), jetDef_(fastjet::antikt_algorithm, 0.4) {}
  
  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;

  void setJetsName(char const* n) { jets_.setName(n); }
  void setMinPt(double p) { minPt_ = p; }
  void setOverwrite(bool b) { overwrite_ = b; }
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  double minPt_{30.};
  bool overwrite_{false};
  panda::JetCollection jets_;
  fastjet::JetDefinition jetDef_;
};

class JetScore : public MonophotonModifier {
 public:
  JetScore(char const* name = "JetScore") : MonophotonModifier(name) {}

  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;

  float score_[NMAX_PARTICLES];
};

class LeptonVertex : public MonophotonModifier {
 public:
  // use the vertex of the leading lepton
  LeptonVertex(char const* name = "LeptonVertex") : MonophotonModifier(name) {}

  void addInputBranch(panda::utils::BranchList&) override;
  void addBranches(TTree& skimTree) override;

  void setSpecies(LeptonFlavor flavor) { flavor_ = flavor; }
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;

  LeptonFlavor flavor_;
  short ivtx_;
  short ivtxNoL_;
  float score_;
};

class WHadronizer : public MonophotonModifier {
 public:
  WHadronizer(char const* name = "WHadronizer") : MonophotonModifier(name) {}

  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton& _outEvent) override;
  void addInputBranch(panda::utils::BranchList&) override;

  double weight_;
};

class PhotonRecoil : public MonophotonModifier {
 public:
  PhotonRecoil(char const* name = "PhotonRecoil") : MonophotonModifier(name) {}

  void addBranches(TTree& skimTree) override;
 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  float realMet_;
  float realPhi_;
  float realMetCorrUp_;
  float realPhiCorrUp_;
  float realMetCorrDown_;
  float realPhiCorrDown_;
  float realMetUnclUp_;
  float realPhiUnclUp_;
  float realMetUnclDown_;
  float realPhiUnclDown_;
};

class DEtajjWeight : public MonophotonModifier {
 public:
  DEtajjWeight(TF1* formula, char const* name = "DEtajjWeight");
  ~DEtajjWeight() {}

  void addBranches(TTree& skimTree) override;
  void setDijetSelection(DijetSelection const* sel) { dijet_ = sel; }

 protected:
  void apply(panda::EventMonophoton const&, panda::EventMonophoton&) override;

  TF1* formula_;
  DijetSelection const* dijet_;
  double weight_;
};

#endif
