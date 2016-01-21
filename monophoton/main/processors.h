#include "TreeEntries_simpletree.h"

#include "TString.h"

class EventProcessor {
 public:
  EventProcessor(double _weightNorm = 1., char const* _name = "EventProcessor") : weightNorm_(_weightNorm), name_(_name) {}
  ~EventProcessor() {}

  virtual bool passTrigger(simpletree::Event const&);
  virtual bool beginEvent(simpletree::Event const&);
  virtual bool vetoElectrons(simpletree::Event const&, simpletree::Event&);
  virtual bool vetoMuons(simpletree::Event const&, simpletree::Event&);
  virtual bool vetoTaus(simpletree::Event const&);
  virtual bool selectPhotons(simpletree::Event const&, simpletree::Event&, simpletree::PhotonCollection&);
  virtual bool cleanJets(simpletree::Event const&, simpletree::Event&);
  virtual void calculateMet(simpletree::Event const&, simpletree::Event&);
  virtual void calculateWeight(simpletree::Event const&, simpletree::Event&);
  virtual bool prepareOutput(simpletree::Event const&, simpletree::Event&) { bool ready(outReady_); outReady_ = false; return ready; }

  void setMinPhotonPt(double _m) { minPhotonPt_ = _m; }

  TString const& getName() const { return name_; }

 protected:
  void sortPhotons_(simpletree::Event const&);

  double weightNorm_{1.};
  TString name_{};
  double minPhotonPt_{175.};
  bool outReady_{false};
  std::vector<unsigned> photonPtOrder_{};
};

class GenProcessor : public virtual EventProcessor {
  // As standard processor, but trigger is a passthrough and with npv reweighting

 public:
  GenProcessor() {}
  GenProcessor(double _weightNorm, char const* _name = "GenProcessor") : EventProcessor(_weightNorm, _name) {}
  ~GenProcessor() {}

  void setReweight(TH1* _rwt) { reweight_ = _rwt; }
  void setIdScaleFactor(TH1* _scl) { idscale_ = _scl; }

  bool passTrigger(simpletree::Event const&) override;
  void calculateWeight(simpletree::Event const&, simpletree::Event&) override;

  TH1* reweight_{0};
  TH1* idscale_{0};
};

class GenZnnProxyProcessor : public GenProcessor {
  // GenProcessor with lepton-emulated MET

 public:
  GenZnnProxyProcessor(double _weightNorm, char const* _name = "GenZnnProxyProcessor") : EventProcessor(_weightNorm * 20.00 / (3.363 + 3.366), _name), GenProcessor() {}
  ~GenZnnProxyProcessor() {}

  bool beginEvent(simpletree::Event const&) override;
  bool vetoElectrons(simpletree::Event const&, simpletree::Event&) override;
  bool vetoMuons(simpletree::Event const&, simpletree::Event&) override;
  void calculateMet(simpletree::Event const&, simpletree::Event&) override;

 private:
  unsigned leptonId_{0};
  unsigned proxyLeptons_[2]{0, 0};
};

class GenWlnuProcessor : public GenProcessor {
  // GenProcessor filtering out W->enu events

 public:
  GenWlnuProcessor(double _weightNorm, char const* _name = "GenWlnuProcessor") : EventProcessor(_weightNorm, _name), GenProcessor() {}
  ~GenWlnuProcessor() {}

  bool beginEvent(simpletree::Event const&) override;
};

class GenWenuProcessor : public GenProcessor {
  // GenProcessor limiting to W->enu events

 public:
  GenWenuProcessor() {}
  GenWenuProcessor(double _weightNorm, char const* _name = "GenWenuProcessor") : EventProcessor(_weightNorm, _name), GenProcessor() {}
  ~GenWenuProcessor() {}

  bool beginEvent(simpletree::Event const&) override;
};

class GenGJetProcessor : public GenProcessor {
  // GenProcessor with a linear k-factor as a function of reconstructed photon pt

 public:
  GenGJetProcessor(double _weightNorm, char const* _name = "GenGJetProcessor") : EventProcessor(_weightNorm, _name), GenProcessor() {}
  ~GenGJetProcessor() {}
  
  void calculateWeight(simpletree::Event const&, simpletree::Event&) override;
};

class WenuProxyProcessor : public virtual EventProcessor {
  // Standard processor with e-to-photon proxy
  // Require 0 medium photon passing pixel veto and exactly 1 photon failing the veto and matching a high-pT electron
  // No normalization is performed

 public:
  WenuProxyProcessor() {}
  WenuProxyProcessor(double _weightNorm, char const* _name = "WenuProxyProcessor") : EventProcessor(_weightNorm, _name) {}
  ~WenuProxyProcessor() {}

  bool vetoElectrons(simpletree::Event const&, simpletree::Event&) override;
  bool selectPhotons(simpletree::Event const&, simpletree::Event&, simpletree::PhotonCollection&) override;

 protected:
  std::vector<std::pair<bool, simpletree::LorentzVectorM>> hardElectrons_;
};

class ZeeProxyProcessor : public virtual EventProcessor {
  // Standard processor with e-to-photon proxy + one electron
  // Model monoelectron selection

 public:
  ZeeProxyProcessor(double _weightNorm, char const* _name = "ZeeProxyProcessor") : EventProcessor(_weightNorm, _name) {}
  ~ZeeProxyProcessor() {}

  bool passTrigger(simpletree::Event const&) override;
  bool vetoElectrons(simpletree::Event const&, simpletree::Event&) override;
  bool selectPhotons(simpletree::Event const&, simpletree::Event&, simpletree::PhotonCollection&) override;
  bool prepareOutput(simpletree::Event const&, simpletree::Event&) override;

 protected:
  std::vector<std::pair<unsigned, unsigned>> egPairs_;
};

class LeptonProcessor : public virtual EventProcessor {
  // Require exactly nEl electrons and nMu muons

 public:
  LeptonProcessor(unsigned _nEl, unsigned _nMu, double _weightNorm = 1., char const* _name = "LeptonProcessor") : EventProcessor(_weightNorm, _name), nEl_(_nEl), nMu_(_nMu) {}
  ~LeptonProcessor() {}

  bool passTrigger(simpletree::Event const&) override;
  bool vetoElectrons(simpletree::Event const&, simpletree::Event&) override;
  bool vetoMuons(simpletree::Event const&, simpletree::Event&) override;
  bool vetoTaus(simpletree::Event const&) override { return true; }

 protected:
  unsigned nEl_{0};
  unsigned nMu_{0};
  bool requireTrigger_{true};
};

class GenWenuProxyProcessor : public WenuProxyProcessor, public GenWenuProcessor {
 public:
  GenWenuProxyProcessor(double _weightNorm, char const* _name = "GenWenuProxyProcessor") : EventProcessor(_weightNorm, _name), WenuProxyProcessor(), GenWenuProcessor() {}
  ~GenWenuProxyProcessor() {}
};

class GenLeptonProcessor : public LeptonProcessor, public GenProcessor {
 public:
  GenLeptonProcessor(unsigned _nEl, unsigned _nMu, double _weightNorm, char const* _name = "GenLeptonProcessor") : EventProcessor(_weightNorm, _name), LeptonProcessor(_nEl, _nMu, _weightNorm, _name), GenProcessor() { requireTrigger_ = false; }
  ~GenLeptonProcessor() {}

  bool passTrigger(simpletree::Event const&) override { return true; }
};

class HadronProxyProcessor : public virtual EventProcessor {
  // Require exactly 1 hadron-proxy photon object

 public:
  HadronProxyProcessor(double _weightNorm, char const* _name = "HadronProxyProcessor") : EventProcessor(_weightNorm, _name) {}
  ~HadronProxyProcessor() {}

  void setReweight(TH1* _rwgt) { reweight_ = _rwgt; }

  bool selectPhotons(simpletree::Event const&, simpletree::Event&, simpletree::PhotonCollection&) override;
  void calculateWeight(simpletree::Event const&, simpletree::Event&) override;

 protected:
  TH1* reweight_{0};
};

class GenHadronProcessor : public GenProcessor {
  // As GenProcessor but allows no high-pT gen photon

 public:
  GenHadronProcessor() {}
  GenHadronProcessor(double _weightNorm, char const* _name = "GenHadronProcessor") : EventProcessor(_weightNorm, _name), GenProcessor() {}
  ~GenHadronProcessor() {}

  bool beginEvent(simpletree::Event const&) override;
};
