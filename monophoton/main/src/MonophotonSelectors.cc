#include "MonophotonSelectors.h"

#include "MonophotonOperators.h"
#include "CommonOperators.h"

#include "TSystem.h"

//--------------------------------------------------------------------
// EventSelector
//--------------------------------------------------------------------

void
EventSelector::addOperator(Operator* _op, unsigned _idx/* = -1*/)
{
  if (!dynamic_cast<MonophotonOperator*>(_op) && !dynamic_cast<CommonOperator*>(_op))
    throw std::runtime_error(TString::Format("Cannot add operator %s to EventSelector", _op->name()).Data());

  if (_idx >= operators_.size())
    operators_.push_back(_op);
  else
    operators_.insert(operators_.begin() + _idx, _op);
}

void
EventSelector::setupSkim_(bool _isMC)
{
  // Branches to be directly copied from the input tree
  // Add a prepareFill line below any time a collection branch is added
  panda::utils::BranchList blist{{"runNumber", "lumiNumber", "eventNumber", "npv", "rho", "vertices"}};
  if (_isMC)
    blist += {"npvTrue", "partons", "genParticles", "genVertex"}; // , "genMet"};
  else
    blist += {"metFilters"};

  inEvent_->book(*skimOut_, blist);

  blist = {"weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"};
  if (_isMC)
    blist += {"genJets"}; // filled only if AddGenJets operator is run

  outEvent_.book(*skimOut_, blist);
}

void
EventSelector::prepareFill_()
{
  inEvent_->vertices.prepareFill(*skimOut_);
  // inEvent_->pfCandidates.prepareFill(*skimOut_);
  inEvent_->partons.prepareFill(*skimOut_);
  inEvent_->genParticles.prepareFill(*skimOut_);
}

void
EventSelector::selectEvent()
{
  if (blindPrescale_ > 1 && inEvent_->runNumber >= blindMinRun_ && inEvent_->eventNumber % blindPrescale_ != 0)
    return;

  outEvent_.init();
  inWeight_ = inEvent_->weight;
  outEvent_.weight = inEvent_->weight;

  Clock::time_point start;

  bool pass(true);
  for (unsigned iO(0); iO != operators_.size(); ++iO) {
    auto& op(*operators_[iO]);
    
    if (useTimers_)
      start = Clock::now();

    if (!op.exec(*inEvent_, outEvent_))
      pass = false;

    if (useTimers_)
      timers_[iO] += Clock::now() - start;
  }

  cutsOut_->Fill();

  if (pass) {
    // IMPORTATNT
    // We link these skimOut branches to the input event. Need to refresh the addresses in case
    // collections are resized.

    // It would be clearer / more elegant to factor this operation out to a serial part, have
    // selectEvent take an EventMonophoton const& as an argument, and return pass, but cases
    // like ZeeEventSelector doesn't allow an easy factorization.

    std::lock_guard<std::mutex> lock(EventSelectorBase::mutex);

    prepareFill_();

    outEvent_.fill(*skimOut_);
  }
}

//--------------------------------------------------------------------
// ZeeEventSelector
//--------------------------------------------------------------------

void
ZeeEventSelector::setupSkim_(bool _isMC)
{
  EventSelector::setupSkim_(_isMC);

  for (leptonSelection_ = operators_.begin(); leptonSelection_ != operators_.end(); ++leptonSelection_) {
    if (dynamic_cast<LeptonSelection*>(*leptonSelection_))
      break;
  }
}

void
ZeeEventSelector::selectEvent()
{
  outEvent_.init();
  inWeight_ = inEvent_->weight;
  outEvent_.weight = inEvent_->weight;

  Clock::time_point start;

  bool passUpToLS(true);
  unsigned iO(0);
  for (auto itr(operators_.begin()); itr != leptonSelection_; ++itr) {
    auto& op(**itr);
    
    if (useTimers_)
      start = Clock::now();

    if (!op.exec(*inEvent_, outEvent_))
      passUpToLS = false;

    if (useTimers_)
      timers_[iO] += Clock::now() - start;

    ++iO;
  }

  if (passUpToLS && outEvent_.photons.size() > 1) {
    // Assumption: Photon selector is run
    panda::XPhotonCollection photonsTmp(outEvent_.photons);

    for (auto& photon : photonsTmp) {
      outEvent_.electrons.clear();
      outEvent_.photons.clear();
      outEvent_.photons.push_back(photon);

      bool pass(true);

      unsigned iOPair(iO);
      for (auto itr(leptonSelection_); itr != operators_.end(); ++itr) {
        auto& op(**itr);

        if (useTimers_)
          start = Clock::now();

        if (!op.exec(*inEvent_, outEvent_))
          pass = false;

        if (useTimers_)
          timers_[iOPair] += Clock::now() - start;

        ++iOPair;
      }

      cutsOut_->Fill();

      if (pass) {
        std::lock_guard<std::mutex> lock(EventSelectorBase::mutex);

        prepareFill_();
          
        outEvent_.fill(*skimOut_);
      }
    }
  }
  else {
    // just run the remaining operators

    bool pass(passUpToLS);

    for (auto itr(leptonSelection_); itr != operators_.end(); ++itr) {
      auto& op(**itr);

      if (useTimers_)
        start = Clock::now();

      if (!op.exec(*inEvent_, outEvent_))
        pass = false;

      if (useTimers_)
        timers_[iO] += Clock::now() - start;

      ++iO;
    }

    cutsOut_->Fill();

    if (pass) {
      std::lock_guard<std::mutex> lock(EventSelectorBase::mutex);

      prepareFill_();
          
      outEvent_.fill(*skimOut_);
    }
  }
}

//--------------------------------------------------------------------
// PartonSelector
//--------------------------------------------------------------------

PartonSelector::PartonSelector(char const* _name) :
  EventSelector(_name),
  flavor_(new PartonFlavor())
{
  operators_.push_back(flavor_);
}

PartonSelector::~PartonSelector()
{
  if (!ownOperators_) {
    // we need to take care of the first operator which we created
    delete flavor_;
    operators_.erase(operators_.begin());
  }
}

void
PartonSelector::selectEvent()
{
  if (!flavor_->exec(*inEvent_, outEvent_))
    return;

  EventSelector::selectEvent();
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
SmearingSelector::selectEvent()
{
  if (!func_)
    return;

  // smearing the MET only - total pT will be inconsistent
  double originalMet(inEvent_->t1Met.pt);

  inEvent_->weight /= nSamples_;

  for (unsigned iS(0); iS != nSamples_; ++iS) {
    inEvent_->t1Met.pt = originalMet + func_->GetRandom();
  
    EventSelector::selectEvent();
  }
}
