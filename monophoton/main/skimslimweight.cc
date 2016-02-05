#include "TTree.h"
#include "TFile.h"
#include "TH1.h"
#include "TLorentzVector.h"
#include "TROOT.h"

#include "processors.h"

#include "NeroToSimple.h"

#include <vector>
#include <utility>
#include <map>
#include <functional>

double
deltaR2(simpletree::Particle const& _p1, simpletree::Particle const& _p2)
{
  double dEta(_p1.eta - _p2.eta);
  double dPhi(TVector2::Phi_mpi_pi(_p1.phi - _p2.phi));
  return dEta * dEta + dPhi * dPhi;
}

unsigned const PHOTONWP(1);

bool
photonSelection(simpletree::Photon const& _ph)
{
  switch (PHOTONWP) {
  case 0:
    return _ph.loose;
  case 1:
    return _ph.medium;
  case 2:
    return _ph.tight;
  };
}

bool
photonEVeto(simpletree::Photon const& _ph)
{
  return _ph.pixelVeto;
}

class SkimSlimWeight {
public:
  SkimSlimWeight() {}
  ~SkimSlimWeight() {}

  void reset() { processors_.clear(); }
  void addProcessor(char const* _name, EventProcessor* _p) { processors_.emplace_back(_name, _p); }
  void run(TTree* input, char const* outputDir, char const* sampleName, long nEntries = -1, bool neroInput = false);

private:
  std::vector<std::pair<TString, EventProcessor*>> processors_{};
};

void
SkimSlimWeight::run(TTree* _input, char const* _outputDir, char const* _sampleName, long _nEntries/* = -1*/, bool _neroInput/* = false*/)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  unsigned nP(processors_.size());

  simpletree::Event event;

  NeroToSimple* translator(0);
  if (_neroInput) {
    translator = new NeroToSimple(*_input, event);
    _input->LoadTree(0);
    auto* file(_input->GetCurrentFile());
    auto* triggerNames(file->Get("triggerNames"));
    if (triggerNames)
      translator->setTriggerNames(triggerNames->GetTitle());
  }
  else
    event.setAddress(*_input);

  std::vector<TTree*> skimTrees(nP, 0);
  std::vector<TTree*> cutTrees(nP, 0);
  std::vector<simpletree::Event> outEvents(nP);
  std::vector<unsigned short> cut(nP, 0);
  std::vector<bool*> tauVeto(nP, 0); // cannot use std::vetor<bool> because that is not quite an array of bools
  std::vector<bool*> metIso(nP, 0);
  std::vector<float*> dPhiJetMetMin(nP, 0);
  
  for (unsigned iP(0); iP != nP; ++iP) {
    auto* outputFile(new TFile(outputDir + "/" + sampleName + "_" + processors_[iP].first + ".root", "recreate"));
    skimTrees[iP] = new TTree("events", "events");
    outEvents[iP].book(*skimTrees[iP], {"run", "lumi", "event", "npv", "weight", "partons", "jets", "photons", "electrons", "muons", "t1Met"});
    tauVeto[iP] = new bool;
    metIso[iP] = new bool;
    dPhiJetMetMin[iP] = new float;
    skimTrees[iP]->Branch("tauVeto", tauVeto[iP], "tauVeto/O");
    skimTrees[iP]->Branch("t1Met.iso", metIso[iP], "iso/O");
    skimTrees[iP]->Branch("dPhiJetMetMin", dPhiJetMetMin[iP], "dPhiJetMetMin/F");
    processors_[iP].second->addBranches(*skimTrees[iP]);

    cutTrees[iP] = new TTree(processors_[iP].second->getName() + "CutFlow", "cutflow");
    cutTrees[iP]->Branch("run", &event.run, "run/i");
    cutTrees[iP]->Branch("lumi", &event.lumi, "lumi/i");
    cutTrees[iP]->Branch("event", &event.event, "event/i");
    cutTrees[iP]->Branch("cut", &(cut[iP]), "cut/s");
  }

  unsigned long passInit(0);
  for (unsigned iP(0); iP != nP; ++iP)
    passInit |= (1 << iP);
  unsigned long pass(passInit);

  auto updateCutFlow([&pass, &cut, &cutTrees](bool passCut, unsigned iP) {
      if (passCut)
        ++cut[iP];
      else {
        pass &= ~(1 << iP);
        cutTrees[iP]->Fill();
      }
    });

  auto passAny([&pass, nP, &updateCutFlow](std::function<bool(unsigned)> const& fct)->bool {
      for (unsigned iP(0); iP != nP; ++iP) {
        if ((pass & (1 << iP)) == 0)
          continue;
        
        bool passCut(fct(iP));
        updateCutFlow(passCut, iP);
      }
      return pass != 0;
    });

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (translator)
      translator->translate();

    for (auto& ev : outEvents)
      ev.init();

    pass = passInit;
    cut.assign(cut.size(), 0);

    if (!passAny([this, &event](unsigned iP)->bool {

          return this->processors_[iP].second->passTrigger(event);

        }))
      continue;

    if (!passAny([this, &event](unsigned iP)->bool {

          return this->processors_[iP].second->beginEvent(event);

        }))
      continue;

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->vetoMuons(event, outEvents[iP]);

        }))
      continue;

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->vetoElectrons(event, outEvents[iP]);

        }))
      continue;

    if (!passAny([this, &event, &tauVeto](unsigned iP)->bool {

          //          return this->processors_[iP].second->vetoTaus(event);
          *tauVeto[iP] = this->processors_[iP].second->vetoTaus(event);
          return true;

        }))
      continue;

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->selectPhotons(event, outEvents[iP]);

        }))
      continue;

    for (unsigned iP(0); iP != nP; ++iP) {
      if ((pass & (1 << iP)) == 0)
        continue;

      outEvents[iP].run = event.run;
      outEvents[iP].lumi = event.lumi;
      outEvents[iP].event = event.event;
      outEvents[iP].npv = event.npv;
      outEvents[iP].partons.copy(event.partons);

      // multiple output "events" can be created from a single input event in some control regions
      while (processors_[iP].second->prepareOutput(event, outEvents[iP])) {
        processors_[iP].second->calculateMet(event, outEvents[iP]);

        bool cleanJets(processors_[iP].second->cleanJets(event, outEvents[iP]));
        updateCutFlow(cleanJets, iP);

        if (!cleanJets)
          continue;

        bool selectMet(processors_[iP].second->selectMet(event, outEvents[iP]));
        updateCutFlow(selectMet, iP);

        if (!selectMet)
          continue;

        // temporary
        unsigned iJ(0);
        unsigned nJMax(outEvents[iP].jets.size());
	float dPhi = 5.;
        if (nJMax > 4)
          nJMax = 4;

        for (; iJ != nJMax; ++iJ) {
	  dPhi = std::abs(TVector2::Phi_mpi_pi(outEvents[iP].jets[iJ].phi - outEvents[iP].t1Met.phi));
          if ( dPhi < 0.5)
            break;
        }
        *metIso[iP] = iJ == nJMax;
	*dPhiJetMetMin[iP] = dPhi;
        // temporary

        processors_[iP].second->calculateWeight(event, outEvents[iP]);

        skimTrees[iP]->Fill();
        cutTrees[iP]->Fill();
        
        // cutflow counter is incremented per applyCut call
        // reset the cutflow counter for the next round of prepareOutput
        cut[iP] -= 2;
      }
    }
  }

  for (unsigned iP(0); iP != nP; ++iP) {
    auto* file = skimTrees[iP]->GetCurrentFile();
    file->cd();
    skimTrees[iP]->Write();
    cutTrees[iP]->Write();
    delete skimTrees[iP];
    delete cutTrees[iP];
    delete file;
    delete tauVeto[iP];
    delete metIso[iP];
    delete dPhiJetMetMin[iP];
  }

  delete translator;
}

bool
EventProcessor::passTrigger(simpletree::Event const& _event)
{
  return _event.hlt[simpletree::kPhoton165HE10].pass;
}

bool
EventProcessor::beginEvent(simpletree::Event const& _event)
{
  if (eventList_ && eventList_->inList(_event))
    return false;

  if (!_event.metFilters.pass())
    return false;

  outReady_ = true;
  return true;
}

bool
EventProcessor::vetoElectrons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon

  unsigned iE(0);
  for (; iE != _event.electrons.size(); ++iE) {
    auto& electron(_event.electrons[iE]);
    if (!electron.loose || electron.pt < 10.)
      continue;

    unsigned iP(0);
    for (; iP != _outEvent.photons.size(); ++iP) {
      if (deltaR2(_outEvent.photons[iP], electron) < 0.0225)
        break;
    }
    if (iP != _outEvent.photons.size()) // there was a matching candidate photon
      continue;

    break;
  }

  // no electron matched the veto condition
  return iE == _event.electrons.size();
}

bool
EventProcessor::vetoMuons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned iM(0);
  for (; iM != _event.muons.size(); ++iM) {
    auto& muon(_event.muons[iM]);
    if (muon.loose && muon.pt > 10.)
      break;
  }

  return iM == _event.muons.size();
}

bool
EventProcessor::vetoTaus(simpletree::Event const& _event)
{
  unsigned iTau(0);
  for (; iTau != _event.taus.size(); ++iTau) {
    auto& tau(_event.taus[iTau]);

    unsigned iE(0);
    for (; iE != _event.electrons.size(); ++iE) {
      auto& electron(_event.electrons[iE]);
      if (electron.loose && deltaR2(tau, electron) < 0.16)
        break;
    }
    if (iE != _event.electrons.size())
      continue;

    unsigned iM(0);
    for (; iM != _event.muons.size(); ++iM) {
      auto& muon(_event.muons[iM]);
      if (muon.loose && deltaR2(tau, muon) < 0.16)
        break;
    }
    if (iM != _event.muons.size())
      continue;

    if (tau.decayMode && tau.combIso < 5.)
      break;
  }

  return iTau == _event.taus.size();
}

bool
EventProcessor::selectPhotons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  for (auto& photon : _event.photons) {
    if (!photon.isEB)
      continue;

    // need to add sipip cut when available
    if (photonSelection(photon) && photonEVeto(photon) && photon.pt > minPhotonPt_ &&
        photon.sieie > 0.001 && photon.mipEnergy < 4.9 && std::abs(photon.time) < 3. && photon.s4 < 0.95) {

      // unsigned iM(0);
      // for (; iM != _event.muons.size(); ++iM) {
      //   if (deltaR2(_event.muons[iM], photon) < 0.01)
      //     break;
      // }
      // if (iM == _event.muons.size())
      //   _outEvent.photons.push_back(photon);
      
      _outEvent.photons.push_back(photon);
      //}
    }
  }

  return _outEvent.photons.size() != 0;
}

bool
EventProcessor::cleanJets(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  for (auto& jet : _event.jets) {
    unsigned iPh(0);
    for (; iPh != _outEvent.photons.size(); ++iPh) {
      if (deltaR2(jet, _outEvent.photons[iPh]) < 0.16)
        break;
    }
    if (iPh != _outEvent.photons.size())
      continue;

    unsigned iMu(0);
    for (; iMu != _outEvent.muons.size(); ++iMu) {
      if (deltaR2(jet, _outEvent.muons[iMu]) < 0.16)
        break;
    }
    if (iMu != _outEvent.muons.size())
      continue;

    unsigned iEl(0);
    for (; iEl != _outEvent.electrons.size(); ++iEl) {
      if (deltaR2(jet, _outEvent.electrons[iEl]) < 0.16)
        break;
    }
    if (iEl != _outEvent.electrons.size())
      continue;

    _outEvent.jets.push_back(jet);
  }

  return true;
}

void
EventProcessor::calculateMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  _outEvent.t1Met = _event.t1Met;
}

bool
EventProcessor::selectMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (!(std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi)) > 2.))
    return false;

  return true;
}

void
EventProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  _outEvent.weight = _event.weight * weightNorm_;
}


bool
ListedEventProcessor::beginEvent(simpletree::Event const& _event)
{
  if (!eventList_ || !eventList_->inList(_event))
    return false;

  outReady_ = true;
  return true;
}


void
GenProcessor::addBranches(TTree& _outTree)
{
  if (!useAltWeights_)
    return;

  _outTree.Branch("scale1020", scaleReweight_, "scale1020/F");
  _outTree.Branch("scale1005", scaleReweight_ + 1, "scale1005/F");
  _outTree.Branch("scale2010", scaleReweight_ + 2, "scale2010/F");
  _outTree.Branch("scale2020", scaleReweight_ + 3, "scale2020/F");
  _outTree.Branch("scale0510", scaleReweight_ + 4, "scale0510/F");
  _outTree.Branch("scale0520", scaleReweight_ + 5, "scale0520/F");
  _outTree.Branch("pdf", pdfReweight_, "pdf[100]/F");
}

bool
GenProcessor::passTrigger(simpletree::Event const&)
{
  return true;
}

void
GenProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  EventProcessor::calculateWeight(_event, _outEvent);

  if (reweight_) {
    int iX(reweight_->FindFixBin(_event.npv));
    if (iX == 0)
      iX = 1;
    if (iX > reweight_->GetNbinsX())
      iX = reweight_->GetNbinsX();

    _outEvent.weight *= reweight_->GetBinContent(iX);
  }

  if (idscale_) {
    int iX(idscale_->FindFixBin(_outEvent.photons[0].pt));
    if (iX == 0)
      iX = 1;
    if (iX > idscale_->GetNbinsX())
      iX = idscale_->GetNbinsX();

    _outEvent.weight *= idscale_->GetBinContent(iX);
  }

  if (useAltWeights_) {
    for (unsigned iS(0); iS != 6; ++iS)
      scaleReweight_[iS] = _event.reweight[iS].scale;
    for (unsigned iS(0); iS != 100; ++iS)
      pdfReweight_[iS] = _event.reweight[iS + 6].scale;
  }
}


void
GenDifferentialProcessor::setPtBin(double _min, double _relWeight)
{
  weights_.emplace_back(_min, _relWeight);
}

void
GenDifferentialProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  GenProcessor::calculateWeight(_event, _outEvent);

  if (weights_.size() == 0)
    return;

  double pt(_outEvent.photons[0].pt);
  unsigned iBin(0);
  while (iBin != weights_.size() && pt >= weights_[iBin].first)
    ++iBin;

  if (iBin > 0)
    iBin -= 1;
  
  _outEvent.weight *= weights_[iBin].second;
}


bool
GenZnnProxyProcessor::beginEvent(simpletree::Event const& _event)
{
  proxyLeptons_[0] = proxyLeptons_[1] = -1;

  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    unsigned absId(std::abs(_event.partons[iP].pid));
    if (absId == 11 || absId == 13) {
      leptonId_ = absId;
      break;
    }
  }

  if (iP == _event.partons.size())
    return false;

  return EventProcessor::beginEvent(_event);
}

bool
GenZnnProxyProcessor::vetoElectrons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  auto& electrons(_event.electrons);

  if (leptonId_ == 11) {
    auto& finalStates(_event.partonFinalStates);

    for (unsigned iE(0); iE != electrons.size(); ++iE) {
      auto& electron(electrons[iE]);

      unsigned iG(0);
      for (; iG != finalStates.size(); ++iG) {
        if (deltaR2(finalStates[iG], electron) < 0.01)
          break;
      }
      if (iG != finalStates.size()) {
        if (proxyLeptons_[0] > electrons.size())
          proxyLeptons_[0] = iE;
        else {
          proxyLeptons_[1] = iE;
          break;
        }
      }
    }
  }

  unsigned iE(0);
  for (; iE != electrons.size(); ++iE) {
    if (iE == proxyLeptons_[0] || iE == proxyLeptons_[1])
      continue;

    if (electrons[iE].loose && electrons[iE].pt > 10.)
      break;
  }

  return iE == electrons.size();
}

bool
GenZnnProxyProcessor::vetoMuons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  auto& muons(_event.muons);

  if (leptonId_ == 13) {
    auto& finalStates(_event.partonFinalStates);

    for (unsigned iM(0); iM != muons.size(); ++iM) {
      auto& muon(muons[iM]);

      unsigned iG(0);
      for (; iG != finalStates.size(); ++iG) {
        if (deltaR2(finalStates[iG], muon) < 0.01)
          break;
      }
      if (iG != finalStates.size()) {
        if (proxyLeptons_[0] > muons.size())
          proxyLeptons_[0] = iM;
        else {
          proxyLeptons_[1] = iM;
          break;
        }
      }
    }
  }

  unsigned iM(0);
  for (; iM != muons.size(); ++iM) {
    if (iM == proxyLeptons_[0] || iM == proxyLeptons_[1])
      continue;

    if (muons[iM].loose && muons[iM].pt > 10.)
      break;
  }

  return iM == muons.size();
}

void
GenZnnProxyProcessor::calculateMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  auto&& metV(_event.t1Met.v());
  double sumEt(_event.t1Met.sumEt);

  simpletree::LeptonCollection const* leptons(0);
  if (leptonId_ == 11)
    leptons = &_event.electrons;
  else if (leptonId_ == 13)
    leptons = &_event.muons;

  if (leptons) {
    for (unsigned iProx : {0, 1}) {
      if (proxyLeptons_[iProx] < leptons->size()) {
        auto& lepton(leptons->at(proxyLeptons_[iProx]));
        metV += TVector2(lepton.pt * std::cos(lepton.phi), lepton.pt * std::sin(lepton.phi));
        sumEt -= lepton.pt;
      }
    }
  }

  _outEvent.t1Met.met = metV.Mod();
  _outEvent.t1Met.phi = TVector2::Phi_mpi_pi(metV.Phi());
  _outEvent.t1Met.sumEt = sumEt;
}


bool
GenWlnuProcessor::beginEvent(simpletree::Event const& _event)
{
  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    if (std::abs(_event.partons[iP].pid) == 11)
      break;
  }

  if (iP != _event.partons.size())
    return false;

  return EventProcessor::beginEvent(_event);
}


bool
GenWenuProcessor::beginEvent(simpletree::Event const& _event)
{
  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    if (std::abs(_event.partons[iP].pid) == 11)
      break;
  }
  
  if (iP == _event.partons.size())
    return false;

  return EventProcessor::beginEvent(_event);
}


void
GenGJetProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  GenProcessor::calculateWeight(_event, _outEvent);

  _outEvent.weight *= 1.71691 - 0.00122061 * _outEvent.photons[0].pt;
}


bool
WenuProxyProcessor::vetoElectrons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  auto& electrons(_event.electrons);

  hardElectrons_.clear();

  unsigned iE(0);
  for (; iE != electrons.size(); ++iE) {
    if (electrons[iE].pt > 150.)
      hardElectrons_.emplace_back(electrons[iE].loose, electrons[iE].p4());
    else if (electrons[iE].loose && electrons[iE].pt > 10.)
      break;
  }

  return iE == electrons.size();      
}

bool
WenuProxyProcessor::selectPhotons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned iP(0);
  for (; iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (!photon.isEB)
      continue;

    if (photonSelection(photon) && photon.pt > minPhotonPt_) {
      if (photonEVeto(photon))
        break;

      for (auto& ele : hardElectrons_) {
        double dEta(ele.second.Eta() - photon.eta);
        double dPhi(TVector2::Phi_mpi_pi(ele.second.Phi() - photon.phi));
        if (dEta * dEta + dPhi * dPhi < 0.01)
          ele.first = false;
      }

      _outEvent.photons.push_back(photon);
    }
  }

  if (_outEvent.photons.size() == 0 || iP != _event.photons.size())
    return false;

  unsigned iE(0);
  for (; iE != hardElectrons_.size(); ++iE) {
    if (hardElectrons_[iE].first)
      break;
  }
  if (iE != hardElectrons_.size())
    return false;

  return true;
}


bool
ZeeProxyProcessor::passTrigger(simpletree::Event const& _event)
{
  return _event.hlt[simpletree::kEle27Loose].pass;
}

bool
ZeeProxyProcessor::vetoElectrons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  // electron selection and veto done in selectPhotons
  return true;
}

bool
ZeeProxyProcessor::selectPhotons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  egPairs_.clear();

  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (!photon.isEB)
      continue;

    if (photonSelection(photon) && photon.pt > minPhotonPt_) {
      if (photonEVeto(photon))
        break;

      int unmatchedE(-1);
      unsigned iE(0);
      for (; iE != _event.electrons.size(); ++iE) {
        auto& electron(_event.electrons[iE]);
        if (!electron.loose || electron.pt < 10.)
          continue;

        double dEta(electron.eta - photon.eta);
        double dPhi(TVector2::Phi_mpi_pi(electron.phi - photon.phi));
        if (dEta * dEta + dPhi * dPhi < 0.01)
          continue;

        if (unmatchedE >= 0)
          break;

        unmatchedE = iE;
      }

      if (iE != _event.electrons.size()) // there were >= 2 unmatched loose electrons
        continue;

      if (unmatchedE < 0) // there was no unmatched loose electron
        continue;

      auto& electron(_event.electrons[unmatchedE]);
      if (electron.tight && electron.pt > 30. && electron.matchHLT27Loose)
        egPairs_.emplace_back(unmatchedE, iP);
    }
  }

  return egPairs_.size() != 0;
}

bool
ZeeProxyProcessor::prepareOutput(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (egPairs_.size() == 0)
    return false;
  
  _outEvent.electrons.clear();
  _outEvent.electrons.push_back(_event.electrons[egPairs_.back().first]);
  _outEvent.photons.clear();
  _outEvent.photons.push_back(_event.photons[egPairs_.back().second]);

  egPairs_.pop_back();

  return true;
}


bool
LeptonProcessor::passTrigger(simpletree::Event const& _event)
{
  if (!requireTrigger_)
    return true;

  if (nMu_ > 0)
    return _event.hlt[simpletree::kMu27].pass;
  else
    return _event.hlt[simpletree::kEle27Loose].pass;
}

bool
LeptonProcessor::vetoElectrons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (nEl_ > 0) {
    bool foundTight(false);

    for (auto& electron : _event.electrons) {
      if (electron.tight && electron.pt > 30. && (!requireTrigger_ || electron.matchHLT27Loose))
        foundTight = true;
      if (electron.loose && electron.pt > 10.)
        _outEvent.electrons.push_back(electron);
    }

    return (foundTight || nMu_ > 0) && _outEvent.electrons.size() == nEl_;
  }
  else {
    return EventProcessor::vetoElectrons(_event, _outEvent);
  }
}

bool
LeptonProcessor::vetoMuons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (nMu_ > 0) {
    bool foundTight(false);
    
    for (auto& muon : _event.muons) {
      if (muon.tight && muon.pt > 30. && (!requireTrigger_ || muon.matchHLT27))
        foundTight = true;
      if (muon.loose && muon.pt > 10.)
        _outEvent.muons.push_back(muon);
    }

    return foundTight && _outEvent.muons.size() == nMu_;
  }
  else {
    return EventProcessor::vetoMuons(_event, _outEvent);
  }
}


bool
EMObjectProcessor::selectPhotons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned iP(0);
  for (; iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (!photon.isEB)
      continue;

    if (photon.sieie > 0.015)
      continue;

    if (photon.passHOverE(PHOTONWP) && photon.passNHIso(PHOTONWP) && photon.passPhIso(PHOTONWP) && photonEVeto(photon) && photon.pt > minPhotonPt_) {
      if (photon.sieie < 0.012 && photon.passCHIso(PHOTONWP))
        break;

      _outEvent.photons.push_back(photon);
    }
  }

  return _outEvent.photons.size() == 1 && iP == _event.photons.size();
}


bool
EMPlusJetProcessor::cleanJets(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (!EventProcessor::cleanJets(_event, _outEvent))
    return false;

  for (auto& jet : _outEvent.jets) {
    if (jet.pt > 100. && std::abs(jet.eta) < 2.5)
      return true;
  }

  return false;
}


void
HadronProxyProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  EventProcessor::calculateWeight(_event, _outEvent);

  if (reweight_) {
    int iX(0);
    reweight_->FindFixBin(_event.photons[0].pt);
    if (iX == 0)
      iX = 1;
    else if (iX > reweight_->GetNbinsX())
      iX = reweight_->GetNbinsX();

    _outEvent.weight *= reweight_->GetBinContent(iX);
  }
}


bool
GenHadronProcessor::beginEvent(simpletree::Event const& _event)
{
  unsigned iP(0);
  for (; iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (photon.pt > minPhotonPt_ && std::abs(photon.matchedGen) == 22)
      break;
  }

  if (iP != _event.photons.size())
    return false;

  return EventProcessor::beginEvent(_event);
}


bool
LowMtProcessor::selectMet(simpletree::Event const&, simpletree::Event& _outEvent)
{
  double dPhi(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi));
  if (std::abs(dPhi) > 2.)
    return false;

  double mt2(2 * _outEvent.t1Met.met * _outEvent.photons[0].pt * (1 - std::cos(dPhi)));

  return mt2 > 40. * 40. && mt2 < 150. * 150.;
}
