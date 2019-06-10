#include "PandaSelectors.h"

void
PandaEventSelector::addOperator(Operator* _op, unsigned _idx/* = -1*/)
{
  if (!dynamic_cast<Operator*>(_op) && !dynamic_cast<BaseOperator*>(_op))
    throw std::runtime_error(TString::Format("Cannot add operator %s to PandaEventSelector", _op->name()).Data());

  if (_idx >= operators_.size())
    operators_.push_back(_op);
  else
    operators_.insert(operators_.begin() + _idx, _op);
}

void
PandaEventSelector::setupSkim_(panda::EventMonophoton& _inEvent, bool _isMC)
{
  // Branches to be directly copied from the input tree
  // Add a prepareFill line below any time a collection branch is added
  panda::utils::BranchList blist{{"runNumber", "lumiNumber", "eventNumber", "npv", "rho", "vertices"}};
  if (_isMC)
    blist += {"npvTrue", "partons", "genParticles", "genVertex"}; // , "genMet"};
  else
    blist += {"metFilters"};

  _inEvent.book(*skimOut_, blist);

  blist = {"weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"};
  if (_isMC)
    blist += {"genJets"}; // filled only if AddGenJets operator is run

  outEvent_.book(*skimOut_, blist);
}

void
PandaEventSelector::prepareFill_(panda::EventMonophoton& _inEvent)
{
  _inEvent.vertices.prepareFill(*skimOut_);
  // _inEvent.pfCandidates.prepareFill(*skimOut_);
  _inEvent.partons.prepareFill(*skimOut_);
  _inEvent.genParticles.prepareFill(*skimOut_);
}

void
PandaEventSelector::selectEvent(panda::EventMonophoton& _event)
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

  cutsOut_->Fill();

  if (pass) {
    // IMPORTATNT
    // We link these skimOut branches to the input event. Need to refresh the addresses in case
    // collections are resized.

    // It would be clearer / more elegant to factor this operation out to a serial part, have
    // selectEvent take an EventMonophoton const& as an argument, and return pass, but cases
    // like ZeePandaEventSelector doesn't allow an easy factorization.

    std::lock_guard<std::mutex> lock(PandaEventSelectorBase::mutex);

    prepareFill_(_event);

    outEvent_.fill(*skimOut_);
  }
}
