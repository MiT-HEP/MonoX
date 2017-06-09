#include "selectors.h"

#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

#include <cstring>

//--------------------------------------------------------------------
// EventSelectorBase
//--------------------------------------------------------------------

EventSelectorBase::~EventSelectorBase()
{
  if (ownOperators_) {
    for (auto* op : operators_)
      delete op;
  }
}

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
EventSelectorBase::removeOperator(char const* _name)
{
  for (auto itr(operators_.begin()); itr != operators_.end(); ++itr) {
    if (std::strcmp((*itr)->name(), _name) == 0) {
      operators_.erase(itr);
      break;
    }
  }
}

void
EventSelectorBase::initialize(char const* _outputPath, panda::EventMonophoton& _inEvent, panda::utils::BranchList& _blist, bool _isMC)
{
  if (printLevel_ > 0)
    *stream_ << "Initializing " << className() << "::" << name() << std::endl;

  auto* outputFile(new TFile(_outputPath, "recreate"));

  skimOut_ = new TTree("events", "Events");
  cutsOut_ = new TTree("cutflow", "cutflow");

  skimOut_->Branch("weight_Input", &inWeight_, "weight_Input/D");

  cutsOut_->Branch("runNumber", &_inEvent.runNumber, "runNumber/i");
  cutsOut_->Branch("lumiNumber", &_inEvent.lumiNumber, "lumiNumber/i");
  cutsOut_->Branch("eventNumber", &_inEvent.eventNumber, "eventNumber/i");

  setupSkim_(_inEvent, _isMC);

  if (printLevel_ > 0 && printLevel_ <= INFO) {
    *stream_ << "Operators for selector " << name() << std::endl;
    for (auto* op : operators_) {
      *stream_ << " " << op->expr() << std::endl;
      op->setPrintLevel(printLevel_);
      op->setOutputStream(*stream_);
    }
    *stream_ << std::endl;
  }

  for (auto* op : operators_) {
    op->addInputBranch(_blist);
    op->addBranches(*skimOut_);
    op->initialize(_inEvent);
    op->registerCut(*cutsOut_);
  }

  if (printLevel_ > 0)
    *stream_ << std::endl;

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
    *stream_ << "Operator runtimes for " << name() << " (CPU seconds):" << std::endl;
    for (unsigned iO(0); iO != operators_.size(); ++iO) {
      stream_->flags(std::ios_base::fixed);
      stream_->width(5);
      *stream_ << " " << (std::chrono::duration_cast<std::chrono::nanoseconds>(timers_[iO]).count() * 1.e-9) << " " << operators_[iO]->name() << std::endl;
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
  // Add a prepareFill line below any time a collection branch is added
  panda::utils::BranchList blist{{"runNumber", "lumiNumber", "eventNumber", "npv", "rho", "vertices", "pfCandidates"}};
  if (_isMC)
    blist += {"partons", "genParticles", "genVertex"};
  else
    blist += {"metFilters"};

  _inEvent.book(*skimOut_, blist);

  outEvent_.book(*skimOut_, {"weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"});
}

void
EventSelector::prepareFill_(panda::EventMonophoton& _inEvent)
{
  _inEvent.vertices.prepareFill(*skimOut_);
  _inEvent.pfCandidates.prepareFill(*skimOut_);
  _inEvent.partons.prepareFill(*skimOut_);
  _inEvent.genParticles.prepareFill(*skimOut_);
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

  if (pass) {
    // IMPORTATNT
    // We link these skimOut branches to the input event. Need to refresh the addresses in case
    // collections are resized.
    prepareFill_(_event);

    outEvent_.fill(*skimOut_);
  }

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

      if (pass) {
        // IMPORTATNT
        // We link some of the skimOut branches to the input event. Need to refresh the addresses in case
        // collections are resized.
        prepareFill_(_event);
        
        outEvent_.fill(*skimOut_);
      }

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

      if (electron.tight && electron.pt() > 30. && (_event.runNumber == 1 || electron.triggerMatch[panda::Electron::fEl27Tight]))
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
// PartonSelector
//--------------------------------------------------------------------

void
PartonSelector::selectEvent(panda::EventMonophoton& _event)
{
  bool accepted(acceptedId_ == 0);
  
  if (_event.partons.size() != 0) {
    for (auto& parton : _event.partons) {
      unsigned absId(std::abs(parton.pdgid));
      if (absId == rejectedId_)
        return;
      if (absId == acceptedId_) {
        accepted = true;
        break;
      }
    }
  }
  else {
    for (auto& part : _event.genParticles) {
      unsigned absId(std::abs(part.pdgid));
      if (absId == rejectedId_)
        return;
      if (absId == acceptedId_) {
        accepted = true;
        break;
      }
    }
  }

  if (!accepted)
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
TagAndProbeSelector::setupSkim_(panda::EventMonophoton& _inEvent, bool _isMC)
{
  // Branches to be directly copied from the input tree
  // Add a prepareFill function when a collection branch is added
  panda::utils::BranchList blist{{"runNumber", "lumiNumber", "eventNumber", "isData", "npv", "rho", "t1Met"}};
  if (_isMC)
    blist += {"npvTrue"};

  _inEvent.book(*skimOut_, blist);

  // looseTags will be added by the TPMuonPhoton operator
  outEvent_.book(*skimOut_, {"sample", "tp", "tags", "probes", "jets"});
}

void
TagAndProbeSelector::selectEvent(panda::EventMonophoton& _event)
{
  outEvent_.init();
  outEvent_.copy(_event); // only copies "static" branches
  
  outEvent_.t1Met = _event.t1Met;

  inWeight_ = _event.weight;

  outEvent_.sample = sampleId_;

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
    outEvent_.fill(*skimOut_);

  cutsOut_->Fill();
}
