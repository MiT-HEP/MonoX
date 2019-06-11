#include "TagAndProbeSelectors.h"

#include "TagAndProbeOperators.h"
#include "CommonOperators.h"

//--------------------------------------------------------------------
// TagAndProbeSelector
//--------------------------------------------------------------------

#include "PandaTree/Objects/interface/EventTPEG.h"
#include "PandaTree/Objects/interface/EventTPEEG.h"
#include "PandaTree/Objects/interface/EventTPMG.h"
#include "PandaTree/Objects/interface/EventTPMMG.h"
#include "PandaTree/Objects/interface/EventTP2E.h"
#include "PandaTree/Objects/interface/EventTP2M.h"
#include "PandaTree/Objects/interface/EventTPEM.h"
#include "PandaTree/Objects/interface/EventTPME.h"

void
TagAndProbeSelector::addOperator(Operator* _op, unsigned _idx/* = -1*/)
{
  if (!dynamic_cast<TPOperator*>(_op) && !dynamic_cast<CommonOperator*>(_op))
    throw std::runtime_error(TString::Format("Cannot add operator %s to TagAndProbeSelector", _op->name()).Data());

  if (_idx >= operators_.size())
    operators_.push_back(_op);
  else
    operators_.insert(operators_.begin() + _idx, _op);
}

void
TagAndProbeSelector::setupSkim_(bool _isMC)
{
  switch (outType_) {
  case kTPEG:
    outEvent_ = new panda::EventTPEG;
    break;
  case kTPEEG:
    outEvent_ = new panda::EventTPEEG;
    break;
  case kTPMG:
    outEvent_ = new panda::EventTPMG;
    break;
  case kTPMMG:
    outEvent_ = new panda::EventTPMMG;
    break;
  case kTP2E:
    outEvent_ = new panda::EventTP2E;
    break;
  case kTP2M:
    outEvent_ = new panda::EventTP2M;
    break;
  case kTPEM:
    outEvent_ = new panda::EventTPEM;
    break;
  case kTPME:
    outEvent_ = new panda::EventTPME;
    break;
  default:
    throw std::runtime_error("Out event type not set");
  }

  // Branches to be directly copied from the input tree
  // Add a prepareFill function when a collection branch is added
  panda::utils::BranchList blist{{"runNumber", "lumiNumber", "eventNumber", "isData", "npv", "rho", "t1Met"}};
  if (_isMC)
    blist += {"npvTrue"};

  inEvent_->book(*skimOut_, blist);

  // looseTags will be added by the TPMuonPhoton operator
  blist = {"weight", "sample", "tp", "tags", "probes", "jets"};
  if (outType_ == kTPEEG || outType_ == kTPMMG)
    blist += {"looseTags"};

  outEvent_->book(*skimOut_, blist);
}

void
TagAndProbeSelector::selectEvent()
{
  outEvent_->init();

  // copy EventBase members
  static_cast<panda::EventBase&>(*outEvent_) = *inEvent_;

  outEvent_->npv = inEvent_->npv;
  outEvent_->npvTrue = inEvent_->npvTrue;
  outEvent_->rho = inEvent_->rho;
  outEvent_->t1Met = inEvent_->t1Met;

  inWeight_ = inEvent_->weight;

  outEvent_->sample = sampleId_;

  Clock::time_point start;

  bool pass(true);
  for (unsigned iO(0); iO != operators_.size(); ++iO) {
    auto& op(*operators_[iO]);

    if (useTimers_)
      start = Clock::now();

    if (!op.exec(*inEvent_, *outEvent_))
      pass = false;

    if (useTimers_)
      timers_[iO] += Clock::now() - start;
  }

  cutsOut_->Fill();

  if (pass) {
    std::lock_guard<std::mutex> lock(EventSelectorBase::mutex);
    outEvent_->fill(*skimOut_);
  }
}
