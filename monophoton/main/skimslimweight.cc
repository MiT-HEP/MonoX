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

// Hard-coded parameters
bool const ABORTONFAIL(false);
unsigned const PHOTONWP(1);

enum Cut {
  kTrigger,
  kEventFilter,
  kMuonVeto,
  kElectronVeto,
  kTauVeto,
  kPhotonSelection,
  kJetCleaning,
  kMetSelection,
  kHighMet,
  kMetIso,
  nCuts
};

// allow the possibility to apply the cut and record the result but keep the event processing on
unsigned const IGNORECUT((1 << kTauVeto) | (1 << kHighMet) | (1 << kMetIso));

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

bool
allBitsUp(unsigned bits, unsigned pos)
{
  // return true if bits have all 1's up to one bit before pos
  // example: bits = 0011, pos = 2 -> true, pos = 3 -> false
  unsigned mask((1 << pos) - 1);
  mask &= ~IGNORECUT;
  return (bits & mask) == mask;
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
  unsigned short iCut(0);
  std::vector<unsigned> cutBits(nP, 0);
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

    cutTrees[iP] = new TTree("cutflow", "cutflow");
    cutTrees[iP]->Branch("run", &event.run, "run/i");
    cutTrees[iP]->Branch("lumi", &event.lumi, "lumi/i");
    cutTrees[iP]->Branch("event", &event.event, "event/i");
    if (ABORTONFAIL)
      cutTrees[iP]->Branch("cut", &iCut, "cut/s");
    else
      cutTrees[iP]->Branch("cutBits", &(cutBits[iP]), "cutBits/i");
  }

  auto updateCutFlow([&iCut, &cutBits, &cutTrees](bool passCut, unsigned iP) {
      if (passCut)
        cutBits[iP] |= (1 << iCut);
      else if (ABORTONFAIL && allBitsUp(cutBits[iP], iCut))
        cutTrees[iP]->Fill();
    });

  auto passAny([&cutBits, &iCut, nP, &updateCutFlow](std::function<bool(unsigned)> const& fct)->bool {
      bool pass(false);
      for (unsigned iP(0); iP != nP; ++iP) {
        // in "abort on fail" mode, cutBits must have all 1's up to the last bit
        if (ABORTONFAIL && !allBitsUp(cutBits[iP], iCut))
          continue;
        
        bool passCut(fct(iP));
        updateCutFlow(passCut, iP);
        if (passCut)
          pass = true;
      }
      return pass;
    });

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (translator)
      translator->translate();

    for (auto& ev : outEvents)
      ev.init();

    iCut = 0;
    cutBits.assign(cutBits.size(), 0);

    assert(iCut == kTrigger);

    if (!passAny([this, &event](unsigned iP)->bool {

          return this->processors_[iP].second->passTrigger(event);

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    assert(iCut == kEventFilter);

    if (!passAny([this, &event](unsigned iP)->bool {

          return this->processors_[iP].second->beginEvent(event);

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    assert(iCut == kMuonVeto);

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->vetoMuons(event, outEvents[iP]);

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    assert(iCut == kElectronVeto);

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->vetoElectrons(event, outEvents[iP]);

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    assert(iCut == kTauVeto);

    if (!passAny([this, &event, &tauVeto](unsigned iP)->bool {

          *tauVeto[iP] = this->processors_[iP].second->vetoTaus(event);
          return *tauVeto[iP];

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    assert(iCut == kPhotonSelection);

    if (!passAny([this, &event, &outEvents](unsigned iP)->bool {

          return this->processors_[iP].second->selectPhotons(event, outEvents[iP]);

        }) && ABORTONFAIL)
      continue;

    ++iCut;

    for (unsigned iP(0); iP != nP; ++iP) {
      if (ABORTONFAIL && !allBitsUp(cutBits[iP], iCut))
        continue;

      outEvents[iP].run = event.run;
      outEvents[iP].lumi = event.lumi;
      outEvents[iP].event = event.event;
      outEvents[iP].npv = event.npv;
      outEvents[iP].partons.copy(event.partons);

      // multiple output "events" can be created from a single input event in some control regions
      while (processors_[iP].second->prepareOutput(event, outEvents[iP])) {
        assert(iCut == kJetCleaning);

        bool cleanJets(processors_[iP].second->cleanJets(event, outEvents[iP]));
        updateCutFlow(cleanJets, iP);

        if (!cleanJets && ABORTONFAIL)
          continue;

        ++iCut;

        processors_[iP].second->calculateMet(event, outEvents[iP]);

        assert(iCut == kMetSelection);

        bool selectMet(processors_[iP].second->selectMet(event, outEvents[iP]));
        updateCutFlow(selectMet, iP);

        if (!selectMet && ABORTONFAIL)
          continue;

        ++iCut;

        assert(iCut == kHighMet);

        bool highMet(outEvents[iP].t1Met.met > 140.);
        updateCutFlow(highMet, iP);

        ++iCut;

        assert(iCut == kMetIso);

        // temporary
        unsigned iJ(0);
        unsigned nJMax(outEvents[iP].jets.size());
	float dPhi = 5.;
        if (nJMax > 4)
          nJMax = 4;

        for (; iJ != nJMax; ++iJ) {
	  dPhi = std::abs(TVector2::Phi_mpi_pi(outEvents[iP].jets[iJ].phi - outEvents[iP].t1Met.phi));
          if (dPhi < 0.5)
            break;
        }
        *metIso[iP] = iJ == nJMax;
        updateCutFlow(*metIso[iP], iP);

        ++iCut;

	*dPhiJetMetMin[iP] = dPhi;
        // temporary

        assert(iCut == nCuts);

        if (allBitsUp(cutBits[iP], iCut)) {
          processors_[iP].second->calculateWeight(event, outEvents[iP]);

          skimTrees[iP]->Fill();
        }

        if (!ABORTONFAIL || allBitsUp(cutBits[iP], iCut))
          cutTrees[iP]->Fill();
        
        // cutflow counter is incremented per updateCutFlow call
        // reset the cutflow counter for the next round of prepareOutput
        iCut -= 4;
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

  photonEnergyShift_.Set(0., 0.);

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
      if (_outEvent.photons[iP].dR2(electron) < 0.25)
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
    if (!muon.loose || muon.pt < 10.)
      continue;

    unsigned iP(0);
    for (; iP != _outEvent.photons.size(); ++iP) {
      if (_outEvent.photons[iP].dR2(muon) < 0.25)
        break;
    }
    if (iP != _outEvent.photons.size()) // there was a matching candidate photon
      continue;

    break;
  }

  // no muon matched the veto condition
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
      if (electron.loose && tau.dR2(electron) < 0.16)
        break;
    }
    if (iE != _event.electrons.size())
      continue;

    unsigned iM(0);
    for (; iM != _event.muons.size(); ++iM) {
      auto& muon(_event.muons[iM]);
      if (muon.loose && tau.dR2(muon) < 0.16)
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
    
    double pt(photon.pt * (1. + photonEnergyVarFactor_));

    // need to add sipip cut when available
    if (photonSelection(photon) && photonEVeto(photon) && pt > minPhotonPt_ &&
        photon.sieie > 0.001 && photon.mipEnergy < 4.9 && std::abs(photon.time) < 3. && photon.s4 < 0.95) {
      // unsigned iM(0);
      // for (; iM != _event.muons.size(); ++iM) {
      //   if (_event.muons[iM].dR2(photon) < 0.01)
      //     break;
      // }
      // if (iM == _event.muons.size())
      //   _outEvent.photons.push_back(photon);
      
      _outEvent.photons.push_back(photon);

      if (photonEnergyVarFactor_ != 0.) {
        _outEvent.photons.back().pt = pt;
        TVector2 oldPt;
        oldPt.SetMagPhi(photon.pt, photon.phi);
        TVector2 newPt;
        newPt.SetMagPhi(pt, photon.phi);
        photonEnergyShift_ += (newPt - oldPt);
      }
      //}
    }
  }

  return _outEvent.photons.size() != 0;
}

bool
EventProcessor::cleanJets(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  for (auto& jet : _event.jets) {
    switch (jetEnergyVarFactor_) {
    case 0:
      if (jet.pt < 30.)
        continue;
      break;
    case 1:
      if (jet.ptCorrUp < 30.)
        continue;
      break;
    case -1:
      if (jet.ptCorrDown < 30.)
        continue;
      break;
    default:
      continue;
    }

    unsigned iPh(0);
    for (; iPh != _outEvent.photons.size(); ++iPh) {
      if (jet.dR2(_outEvent.photons[iPh]) < 0.16)
        break;
    }
    if (iPh != _outEvent.photons.size())
      continue;

    unsigned iMu(0);
    for (; iMu != _outEvent.muons.size(); ++iMu) {
      if (jet.dR2(_outEvent.muons[iMu]) < 0.16)
        break;
    }
    if (iMu != _outEvent.muons.size())
      continue;

    unsigned iEl(0);
    for (; iEl != _outEvent.electrons.size(); ++iEl) {
      if (jet.dR2(_outEvent.electrons[iEl]) < 0.16)
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

  switch (jetEnergyVarFactor_) {
  case 0:
    break;
  case 1:
    _outEvent.t1Met.met = _event.t1Met.metCorrUp;
    _outEvent.t1Met.phi = _event.t1Met.phiCorrUp;
    break;
  case -1:
    _outEvent.t1Met.met = _event.t1Met.metCorrDown;
    _outEvent.t1Met.phi = _event.t1Met.phiCorrDown;
    break;
  default:
    break;
  }

  if (photonEnergyVarFactor_ != 0.) {
    auto&& metV(_outEvent.t1Met.v());
    metV -= photonEnergyShift_;
    _outEvent.t1Met.met = metV.Mod();
    _outEvent.t1Met.phi = TVector2::Phi_mpi_pi(metV.Phi());
  }
}

bool
EventProcessor::selectMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  if (_outEvent.photons.size() != 0 &&
      !(std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi)) > 2.))
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

  if (idscale_ && _outEvent.photons.size() != 0) {
    int iX(idscale_->FindFixBin(_outEvent.photons[0].pt));
    if (iX == 0)
      iX = 1;
    if (iX > idscale_->GetNbinsX())
      iX = idscale_->GetNbinsX();

    _outEvent.weight *= idscale_->GetBinContent(iX);
  }

  if (kfactors_.size() != 0) {
    for (auto& parton : _event.partons) {
      if (parton.pid != 22 || parton.status != 1)
        continue;

      // what if parton is out of eta acceptance?
      unsigned iBin(0);
      while (iBin != kfactors_.size() && parton.pt >= kfactors_[iBin].first)
        ++iBin;

      if (iBin > 0)
        iBin -= 1;

      _outEvent.weight *= kfactors_[iBin].second;

      break;
    }
  }

  if (useAltWeights_) {
    for (unsigned iS(0); iS != 6; ++iS)
      scaleReweight_[iS] = _event.reweight[iS].scale;
    for (unsigned iS(0); iS != 100; ++iS)
      pdfReweight_[iS] = _event.reweight[iS + 6].scale;
  }
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
        if (finalStates[iG].dR2(electron) < 0.01)
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
        if (finalStates[iG].dR2(muon) < 0.01)
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
  EventProcessor::calculateMet(_event, _outEvent);

  auto&& metV(_outEvent.t1Met.v());
  double sumEt(_outEvent.t1Met.sumEt);

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

  if (_outEvent.photons.size() != 0)
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
      hardElectrons_.emplace_back(electrons[iE].loose, &electrons[iE]);
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
        if (ele.second->dR2(photon) < 0.01)
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

        if (electron.dR2(photon) < 0.01)
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


void
LeptonProcessor::addBranches(TTree& _outTree)
{
  _outTree.Branch("t1Met.recoil", &recoilPt_, "recoil/F");
  _outTree.Branch("t1Met.recoilPhi", &recoilPhi_, "recoilPhi/F");
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

void
LeptonProcessor::calculateMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  EventProcessor::calculateMet(_event, _outEvent);

  auto&& metV(_event.t1Met.v());

  for (auto& electron : _outEvent.electrons)
    metV += TVector2(electron.pt * std::cos(electron.phi), electron.pt * std::sin(electron.phi));

  for (auto& muon : _outEvent.muons)
    metV += TVector2(muon.pt * std::cos(muon.phi), muon.pt * std::sin(muon.phi));

  recoilPt_ = metV.Mod();
  recoilPhi_ = TVector2::Phi_mpi_pi(metV.Phi());
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

    // Wisconsin denominator def
    // if (photon.passHOverE(PHOTONWP) && photonEVeto(photon) && photon.sieie > 0.001 && photon.mipEnergy < 4.9 && std::abs(photon.time) < 3. &&
    //     photon.nhIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::nhIsoCuts[0][0]) &&
    //     photon.phIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::phIsoCuts[0][0]) &&
    //     photon.chIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::chIsoCuts[0][0])) {
    //   unsigned nPass(0);
    //   if (photon.passCHIso(0))
    //     ++nPass;
    //   if (photon.passNHIso(0))
    //     ++nPass;
    //   if (photon.passPhIso(0))
    //     ++nPass;

    //   if (nPass == 3)
    //     break;
      
    //   _outEvent.photons.push_back(photon);
    // }
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

bool
EMPlusJetProcessor::selectMet(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  return true;
}


void
HadronProxyProcessor::calculateWeight(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  EventProcessor::calculateWeight(_event, _outEvent);

  if (reweight_) {
    int iX(reweight_->FindFixBin(_event.photons[0].pt));
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
  if (_outEvent.photons.size() == 0)
    return false;

  double dPhi(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi));
  if (std::abs(dPhi) > 2.)
    return false;

  double mt2(2 * _outEvent.t1Met.met * _outEvent.photons[0].pt * (1 - std::cos(dPhi)));

  return mt2 > 40. * 40. && mt2 < 150. * 150.;
}

void
GenWtaunuProcessor::addBranches(TTree& _outTree)
{
    _outTree.Branch("photons.id", nCut_, "id[photons.size]/I");
  
    GenProcessor::addBranches(_outTree);
}

bool
GenWtaunuProcessor::beginEvent(simpletree::Event const& _event)
{
  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    if (std::abs(_event.partons[iP].pid) == 15)
      break;
  }
  
  if (iP == _event.partons.size())
    return false;

  return EventProcessor::beginEvent(_event);
}

bool
GenWtaunuProcessor::selectPhotons(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  bool matched = false;
  int iP = -1;
  for (auto& photon : _event.photons) {
    iP++;
    nCut_[iP] = 0;
    matched = false;
 
    for (auto& parton : _event.partons) {
     if (std::abs(parton.pid) == 15)
       if (parton.dR2(photon) < 0.5) {
	 matched = true;
	 break;
       }
    } 

    if (!matched)
      continue;
    nCut_[iP]++;

    _outEvent.photons.push_back(photon);

    if (!photon.isEB)
      continue;
    nCut_[iP]++;
  
    if (!(photon.pt > minPhotonPt_))
      continue;
    nCut_[iP]++;
  
    if (!(photon.hOverE < simpletree::Photon::hOverECuts[0][PHOTONWP]))
      continue;
    nCut_[iP]++;
    
    if (!(photon.nhIso < simpletree::Photon::nhIsoCuts[0][PHOTONWP]))
      continue;
    nCut_[iP]++;
    
    if (!(photon.chIso < simpletree::Photon::chIsoCuts[0][PHOTONWP]))
      continue;
    nCut_[iP]++;
    
    if (!(photon.phIso < simpletree::Photon::phIsoCuts[0][PHOTONWP]))
      continue;
    nCut_[iP]++;
    
    if (!(photon.sieie < simpletree::Photon::sieieCuts[0][PHOTONWP]))
      continue;
    nCut_[iP]++;
    
    if (!photonEVeto(photon)) 
      continue;
    nCut_[iP]++;
    
    if (!(photon.sieie > 0.001)) 
      continue;
    nCut_[iP]++;
    
    if (!(photon.s4 < 0.95))
      continue;
    nCut_[iP]++;
    
    if (!(photon.mipEnergy < 4.9))
      continue;
    nCut_[iP]++;
    
    if (!(std::abs(photon.time) < 3.))
      continue;
    nCut_[iP]++;
  }
  
  return _outEvent.photons.size() != 0;
}
