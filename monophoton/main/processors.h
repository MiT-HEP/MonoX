#include "TreeEntries_simpletree.h"

#include "TString.h"

#include <fstream>
#include <string>
#include <cstdlib>
#include <map>
#include <set>

class EventList {
 public:
  void addSource(char const*);
  bool inList(simpletree::Event const&) const;

 private:
  typedef std::set<unsigned> EventContainer;
  typedef std::map<unsigned, EventContainer> LumiContainer;
  typedef std::map<unsigned, LumiContainer> RunContainer;
  RunContainer list_{};
  RunContainer::const_iterator rEnd_{};
};

void
EventList::addSource(char const* _path)
{
  std::ifstream input(_path);
  std::string line;

  while (true) {
    std::getline(input, line);
    if (!input.good())
      break;

    unsigned run(std::atoi(line.substr(0, line.find(":")).c_str()));
    unsigned lumi(std::atoi(line.substr(line.find(":") + 1, line.rfind(":")).c_str()));
    unsigned event(std::atoi(line.substr(line.rfind(":") + 1).c_str()));

    list_[run][lumi].insert(event);
  }

  rEnd_ = list_.end();
}

bool
EventList::inList(simpletree::Event const& _event) const
{
  auto rItr(list_.find(_event.run));
  if (rItr == rEnd_)
    return false;

  auto lItr(rItr->second.find(_event.lumi));
  if (lItr == rItr->second.end())
    return false;

  auto eItr(lItr->second.find(_event.event));
  return eItr != lItr->second.end();
}

class EventProcessor {
 public:
  EventProcessor(double _weightNorm = 1., char const* _name = "EventProcessor") : weightNorm_(_weightNorm), name_(_name) {}
  ~EventProcessor() {}

  virtual bool passTrigger(simpletree::Event const&);
  virtual bool beginEvent(simpletree::Event const&);
  virtual bool vetoElectrons(simpletree::Event const&, simpletree::Event&);
  virtual bool vetoMuons(simpletree::Event const&, simpletree::Event&);
  virtual bool vetoTaus(simpletree::Event const&);
  virtual bool selectPhotons(simpletree::Event const&, simpletree::Event&);
  virtual bool cleanJets(simpletree::Event const&, simpletree::Event&);
  virtual void calculateMet(simpletree::Event const&, simpletree::Event&);
  virtual bool selectMet(simpletree::Event const&, simpletree::Event&);
  virtual void calculateWeight(simpletree::Event const&, simpletree::Event&);
  virtual bool prepareOutput(simpletree::Event const&, simpletree::Event&) { bool ready(outReady_); outReady_ = false; return ready; }

  void setMinPhotonPt(double _m) { minPhotonPt_ = _m; }
  void setEventList(EventList const* _l) { eventList_ = _l; }

  TString const& getName() const { return name_; }

 protected:
  void sortPhotons_(simpletree::Event const&);

  double weightNorm_{1.};
  TString name_{};
  double minPhotonPt_{175.};
  bool outReady_{false};
  std::vector<unsigned> photonPtOrder_{};
  EventList const* eventList_{0};
};

class ListedEventProcessor : public EventProcessor {
  // For beam halo control region; inverted event list filter

 public:
  ListedEventProcessor() {}
  ListedEventProcessor(double _weightNorm = 1., char const* _name = "ListedEventProcessor") : EventProcessor(_weightNorm, _name) {}
  ~ListedEventProcessor() {}

  bool beginEvent(simpletree::Event const&) override;
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
  bool selectPhotons(simpletree::Event const&, simpletree::Event&) override;

  void setWeightErr(double _weightErr) { weightErr_ = _weightErr; }

 protected:
  std::vector<std::pair<bool, simpletree::LorentzVectorM>> hardElectrons_;
  double weightErr_;
};

class ZeeProxyProcessor : public virtual EventProcessor {
  // Standard processor with e-to-photon proxy + one electron
  // Model monoelectron selection

 public:
  ZeeProxyProcessor(double _weightNorm, char const* _name = "ZeeProxyProcessor") : EventProcessor(_weightNorm, _name) {}
  ~ZeeProxyProcessor() {}

  bool passTrigger(simpletree::Event const&) override;
  bool vetoElectrons(simpletree::Event const&, simpletree::Event&) override;
  bool selectPhotons(simpletree::Event const&, simpletree::Event&) override;
  bool prepareOutput(simpletree::Event const&, simpletree::Event&) override;

  void setWeightErr(double _weightErr) { weightErr_ = _weightErr; }

 protected:
  std::vector<std::pair<unsigned, unsigned>> egPairs_;
  double weightErr_;
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

class EMObjectProcessor : public virtual EventProcessor {
  // Require exactly 1 hadron-proxy photon object
 public:
  EMObjectProcessor() {}
  EMObjectProcessor(double _weightNorm, char const* _name = "EMObjectProcessor") : EventProcessor(_weightNorm, _name) {}
  ~EMObjectProcessor() {}

  bool selectPhotons(simpletree::Event const&, simpletree::Event&) override;
};

class EMPlusJetProcessor : public EMObjectProcessor {
  // Require >= 1 jet and 1 hadron-proxy photon object
 public:
  EMPlusJetProcessor(char const* _name = "EMPlusJetProcessor") : EventProcessor(1., _name), EMObjectProcessor() {}
  ~EMPlusJetProcessor() {}

  bool cleanJets(simpletree::Event const&, simpletree::Event&) override;
};
  
class HadronProxyProcessor : public EMObjectProcessor {
  // Require exactly 1 hadron-proxy photon object
 public:
  HadronProxyProcessor() {}
  HadronProxyProcessor(double _weightNorm, char const* _name = "HadronProxyProcessor") : EventProcessor(_weightNorm, _name), EMObjectProcessor() {}
  ~HadronProxyProcessor() {}

  void setReweight(TH1* _rwgt) { reweight_ = _rwgt; }

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

class LowMtProcessor : public virtual EventProcessor {
  // Inverting dPhi(met, photon) cut and requiring Mt(photon) < 90 GeV

 public:
  LowMtProcessor(double _weightNorm = 1., char const* _name = "LowMtProcessor") : EventProcessor(_weightNorm, _name) {}
  ~LowMtProcessor() {}
  
  bool selectMet(simpletree::Event const&, simpletree::Event&) override;
};

class WenuProxyLowMtProcessor : public LowMtProcessor, public WenuProxyProcessor {
 public:
  WenuProxyLowMtProcessor(double _weightNorm, char const* _name = "WenuProxyLowMtProcessor") : EventProcessor(_weightNorm, _name), WenuProxyProcessor() {}
  ~WenuProxyLowMtProcessor() {}
};

class HadronProxyLowMtProcessor : public LowMtProcessor, public HadronProxyProcessor {
 public:
  HadronProxyLowMtProcessor(double _weightNorm, char const* _name = "HadronProxyLowMtProcessor") : EventProcessor(_weightNorm, _name), HadronProxyProcessor() {}
  ~HadronProxyLowMtProcessor() {}
};

class GenLowMtProcessor : public LowMtProcessor, public GenProcessor {
 public:
  GenLowMtProcessor(double _weightNorm, char const* _name = "GenLowMtProcessor") : EventProcessor(_weightNorm, _name), GenProcessor() {}
  ~GenLowMtProcessor() {}
};
