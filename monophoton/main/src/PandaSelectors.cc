#include "PandaSelectors.h"
#include "CommonOperators.h"

PandaEventSelector::PandaEventSelector(char const* _name) :
  EventSelectorBase(_name, kEvent, new panda::Event()),
  outEvent_(*static_cast<panda::Event*>(outEventBase_))
{
}

void
PandaEventSelector::addOperator(Operator* _op, unsigned _idx/* = -1*/)
{
  if (!dynamic_cast<CommonOperator*>(_op))
    throw std::runtime_error(TString::Format("Cannot add operator %s to PandaEventSelector", _op->name()).Data());

  if (_idx >= operators_.size())
    operators_.push_back(_op);
  else
    operators_.insert(operators_.begin() + _idx, _op);
}

panda::utils::BranchList
PandaEventSelector::directCopyBranches_(bool _isMC)
{
  panda::utils::BranchList blist(EventSelectorBase::directCopyBranches_(_isMC));
  blist += {"rho", "vertices"};
  needPrepareFill_(inEvent_->vertices);

  if (!_isMC)
    blist += {"metFilters"};

  return blist;
}
