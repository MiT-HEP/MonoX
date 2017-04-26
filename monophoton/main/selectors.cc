#include "selectors.h"

#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

#include <cstring>

//--------------------------------------------------------------------
// EventSelectorBase
//--------------------------------------------------------------------

void
EventSelectorBase::addOperator(Operator* _op, unsigned _idx/* = -1*/)
{
  if (_idx >= operators_.size())
    operators_.push_back(_op);
  else
    operators_.insert(operators_.begin() + _idx, _op);
}

Operator*
EventSelectorBase::findOperator(char const* _name) const
{
  for (auto* op : operators_) {
    if (std::strcmp(op->name(), _name) == 0)
      return op;
  }

  return 0;
}

void
EventSelectorBase::initialize(char const* _outputPath, panda::EventMonophoton& _inEvent, bool _isMC)
{
  auto* outputFile(new TFile(_outputPath, "recreate"));

  skimOut_ = new TTree("events", "Events");
  cutsOut_ = new TTree("cutflow", "cutflow");

  skimOut_->Branch("weight_Input", &inWeight_, "weight_Input/D");

  cutsOut_->Branch("runNumber", &_inEvent.runNumber, "runNumber/i");
  cutsOut_->Branch("lumiNumber", &_inEvent.lumiNumber, "lumiNumber/i");
  cutsOut_->Branch("eventNumber", &_inEvent.eventNumber, "eventNumber/i");

  setupSkim_(_inEvent, _isMC);

  for (auto* op : operators_) {
    op->addBranches(*skimOut_);
    op->initialize(_inEvent);
    op->registerCut(*cutsOut_);
  }

  // printf("Added all the operators. \n");

  if (useTimers_)
    timers_.resize(operators_.size());
}

void
EventSelectorBase::finalize()
{
  if (!skimOut_)
    return;

  auto* outputFile(skimOut_->GetCurrentFile());
  outputFile->cd();
  skimOut_->Write();
  cutsOut_->Write();

  // save additional output if there are any
  addOutput_(outputFile);

  delete outputFile;
  skimOut_ = 0;
  cutsOut_ = 0;

  if (useTimers_) {
    std::cout << "Operator runtimes for " << name() << " (CPU seconds):" << std::endl;
    for (unsigned iO(0); iO != operators_.size(); ++iO) {
      std::cout.flags(std::ios_base::fixed);
      std::cout.width(5);
      std::cout << " " << (std::chrono::duration_cast<std::chrono::nanoseconds>(timers_[iO]).count() * 1.e-9) << " " << operators_[iO]->name() << std::endl;
    }
  }
}

//--------------------------------------------------------------------
// EventSelector
//--------------------------------------------------------------------

void
EventSelector::setupSkim_(panda::EventMonophoton& _inEvent, bool _isMC)
{
  // Branches to be directly copied from the input tree
  if (_isMC)
    _inEvent.book(*skimOut_, {"runNumber", "lumiNumber", "eventNumber", "npv", "partons", "genParticles"});
  else
    _inEvent.book(*skimOut_, {"runNumber", "lumiNumber", "eventNumber", "npv", "metFilters"});

  outEvent_.book(*skimOut_, {"weight", "jets", "photons", "electrons", "muons", "taus", "t1Met"});
}

void
EventSelector::selectEvent(panda::EventMonophoton& _event)
{
  if (blindPrescale_ > 1 && _event.runNumber >= blindMinRun_ && _event.eventNumber % blindPrescale_ != 0)
    return;

  outEvent_.init();
  inWeight_ = _event.weight;
  outEvent_.weight = _event.weight;

  Clock::time_point start;

  bool pass(true);
  for (unsigned iO(0); iO != operators_.size(); ++iO) {
    auto& op(*operators_[iO]);

    if (useTimers_)
      start = Clock::now();

    if (!op.exec(_event, outEvent_))
      pass = false;

    if (useTimers_)
      timers_[iO] += Clock::now() - start;
  }

  if (pass)
    skimOut_->Fill();

  cutsOut_->Fill();
}

//--------------------------------------------------------------------
// ZeeEventSelector
//--------------------------------------------------------------------

ZeeEventSelector::ZeeEventSelector(char const* name) :
  EventSelector(name)
{
  operators_.push_back(new HLTFilter("HLT_Ele27_WPTight_Gsf"));
  operators_.push_back(new MetFilters());
  operators_.push_back(new EEPairSelection());
  operators_.push_back(new MuonVeto());
  operators_.push_back(new TauVeto());
  operators_.push_back(new JetCleaning());
  operators_.push_back(new LeptonRecoil());

  eePairSel_ = operators_.begin();
  while (!dynamic_cast<EEPairSelection*>(*eePairSel_))
    ++eePairSel_;
}

ZeeEventSelector::~ZeeEventSelector()
{
  for (auto* op : operators_)
    delete op;
}

void
ZeeEventSelector::selectEvent(panda::EventMonophoton& _event)
{
  outEvent_.init();
  outEvent_.weight = _event.weight;

  bool passUpToEE(true);

  auto opItr(operators_.begin());
  while (true) {
    passUpToEE = passUpToEE && (*opItr)->exec(_event, outEvent_);
    if (opItr == eePairSel_)
      break;

    ++opItr;
  }

  if (passUpToEE) {
    for (auto& eePair : static_cast<EEPairSelection*>(*eePairSel_)->getEEPairs()) {
      opItr = eePairSel_;
      outEvent_.photons[0] = _event.photons[eePair.first];
      outEvent_.electrons[0] = _event.electrons[eePair.second];

      bool pass(true);
      for (; opItr != operators_.end(); ++opItr)
        pass = pass && (*opItr)->exec(_event, outEvent_);

      if (pass)
        skimOut_->Fill();

      cutsOut_->Fill();
    }
  }
  else {
    for (; opItr != operators_.end(); ++opItr)
      (*opItr)->exec(_event, outEvent_);

    cutsOut_->Fill();
  }
}

ZeeEventSelector::EEPairSelection::EEPairSelection(char const* name) :
  PhotonSelection(name)
{
  unsigned sels[] = {HOverE, Sieie, CHIsoMax, NHIso, PhIso, MIP49, Time, SieieNonzero, NoisyRegion};
  for (unsigned sel : sels) {
    addSelection(true, sel);
    addVeto(true, sel);
  }
  
  addSelection(false, EVeto);
  addVeto(true, EVeto);
}

bool
ZeeEventSelector::EEPairSelection::pass(panda::EventMonophoton const& _event, panda::EventMonophoton& _outEvent)
{
  eePairs_.clear();

  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (!photon.isEB || photon.scRawPt < minPt_)
      continue;

    int selection(selectPhoton(photon));

    if (selection < 0) // vetoed
      break;
    else if (selection == 0)
      continue;

    // A good photon with pixel seed is found. Now we need to find the partner electron.
    // There can be one and only one loose electron that is not matched to the photon in the event,
    // and this has to be the tight electron.

    unsigned iElectron(-1);

    unsigned iE(0);
    for (; iE != _event.electrons.size(); ++iE) {
      auto& electron(_event.electrons[iE]);

      if (!electron.loose || electron.pt() < 10.)
        continue;

      if (electron.dR2(photon) < 0.01)
        continue;

      if (iElectron < _event.electrons.size())
        break;

      if (electron.tight && electron.pt() > 30. && (_event.runNumber == 1 || electron.triggerMatch[panda::Electron::fEl27Loose]))
        iElectron = iE;
      else
        break;
    }
    if (iElectron >= _event.electrons.size() || iE == _event.electrons.size())
      continue;

    eePairs_.emplace_back(iP, iElectron);
  }

  return eePairs_.size() != 0;
}

//--------------------------------------------------------------------
// WlnuSelector
//--------------------------------------------------------------------

void
WlnuSelector::selectEvent(panda::EventMonophoton& _event)
{
  for (auto& parton : _event.partons) {
    if (std::abs(parton.pdgid) == 11)
      return;
  }

  EventSelector::selectEvent(_event);
}

//--------------------------------------------------------------------
// WenuSelector
//--------------------------------------------------------------------

void
WenuSelector::selectEvent(panda::EventMonophoton& _event)
{
  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);
    if (std::abs(parton.pdgid) == 11)
      break;
  }
  if (iP == _event.partons.size())
    return;

  EventSelector::selectEvent(_event);
}

//--------------------------------------------------------------------
// NormalizingSelector
//--------------------------------------------------------------------

void
NormalizingSelector::addOutput_(TFile*& _outputFile)
{
  auto* hSumW(new TH1D("sumW", "", 1, 0., 1.));
  hSumW->Sumw2();
  skimOut_->Draw("0.5>>sumW", "weight * (" + normCut_ + ")", "goff");
  double sumW(hSumW->GetBinContent(1));
  delete hSumW;

  TString outName(_outputFile->GetName());
  TString tmpName(outName);
  tmpName.ReplaceAll(".root", "_normalizing.root");

  auto* trueOutput(TFile::Open(tmpName, "recreate"));
  auto* trueSkim(skimOut_->CloneTree(0));
  double weight(0.);
  trueSkim->SetBranchAddress("weight", &weight);

  printf("check time. \n norm_ = %.2f \n sumW  = %.2f \n", norm_, sumW);

  long iEntry(0);
  while (skimOut_->GetEntry(iEntry++)) {
    weight = norm_ / sumW * outEvent_.weight;
    trueSkim->Fill();
  }

  trueOutput->cd();
  trueSkim->Write();
  auto* trueCuts(cutsOut_->CloneTree(-1, "fast"));
  trueCuts->Write();

  delete trueOutput;

  delete _outputFile;
  // set the pointer to NULL so that finalize() does not delete it again
  _outputFile = 0;

  gSystem->Rename(tmpName, outName);
}

//--------------------------------------------------------------------
// SmearingSelector
//--------------------------------------------------------------------

void
SmearingSelector::selectEvent(panda::EventMonophoton& _event)
{
  if (!func_)
    return;

  // smearing the MET only - total pT will be inconsistent
  double originalMet(_event.t1Met.pt);

  _event.weight /= nSamples_;

  for (unsigned iS(0); iS != nSamples_; ++iS) {
    _event.t1Met.pt = originalMet + func_->GetRandom();
  
    EventSelector::selectEvent(_event);
  }
}

//--------------------------------------------------------------------
// TagAndProbeSelector
//--------------------------------------------------------------------

void
TagAndProbeSelector::setupSkim_(panda::EventMonophoton&, bool)
{
  outEvent_.book(*skimOut_);
}

void
TagAndProbeSelector::selectEvent(panda::EventMonophoton& _event)
{
  outEvent_.init();
  inWeight_ = _event.weight;
  outEvent_.weight = _event.weight;

  Clock::time_point start;

  bool pass(true);
  for (unsigned iO(0); iO != operators_.size(); ++iO) {
    auto& op(*operators_[iO]);

    if (useTimers_)
      start = Clock::now();

    if (!op.exec(_event, outEvent_))
      pass = false;

    if (useTimers_)
      timers_[iO] += Clock::now() - start;
  }

  if (pass)
    skimOut_->Fill();

  cutsOut_->Fill();
}

