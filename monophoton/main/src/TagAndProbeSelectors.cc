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

/*static*/
panda::EventTP*
TagAndProbeSelector::makeOutEvent(TPEventType _type)
{
  switch (_type) {
  case kTPEG:
    return new panda::EventTPEG;
    break;
  case kTPEEG:
    return new panda::EventTPEEG;
    break;
  case kTPMG:
    return new panda::EventTPMG;
    break;
  case kTPMMG:
    return new panda::EventTPMMG;
    break;
  case kTP2E:
    return new panda::EventTP2E;
    break;
  case kTP2M:
    return new panda::EventTP2M;
    break;
  case kTPEM:
    return new panda::EventTPEM;
    break;
  case kTPME:
    return new panda::EventTPME;
    break;
  default:
    throw std::runtime_error("Out event type not set");
  }
}

TagAndProbeSelector::TagAndProbeSelector(char const* _name, TPEventType _type) :
  EventSelectorBase(_name, kEventMonophoton, makeOutEvent(_type)),
  outEvent_(*static_cast<panda::EventTP*>(outEventBase_)),
  outType_(_type)
{
}

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

panda::utils::BranchList
TagAndProbeSelector::directCopyBranches_(bool _isMC)
{
  panda::utils::BranchList blist = {"runNumber", "lumiNumber", "eventNumber", "isData", "npv", "rho", "t1Met"};
  if (_isMC)
    blist += {"npvTrue"};

  return blist;
}

panda::utils::BranchList
TagAndProbeSelector::processedBranches_(bool _isMC) const
{
  panda::utils::BranchList blist = {"weight", "sample", "tp", "tags", "probes", "jets"};
  if (outType_ == kTPEEG || outType_ == kTPMMG) // looseTags will be added by the TPMuonPhoton operator
    blist += {"looseTags"};

  return blist;
}

void
TagAndProbeSelector::selectEvent()
{
  outEvent_.init();

  // copy EventBase members
  static_cast<panda::EventBase&>(outEvent_) = *inEvent_;

  outEvent_.npv = inEvent_->npv;
  outEvent_.npvTrue = inEvent_->npvTrue;
  outEvent_.rho = inEvent_->rho;
  outEvent_.t1Met = inEvent_->t1Met;

  inWeight_ = inEvent_->weight;

  outEvent_.sample = sampleId_;

  bool pass(runOperators_());

  fillEvent_(pass);
}
