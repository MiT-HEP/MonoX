#include "SelectorBase.h"

#include "BaseOperators.h"

#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

#include <cstring>

//--------------------------------------------------------------------
// EventSelectorBase
//--------------------------------------------------------------------

std::mutex EventSelectorBase::mutex;

EventSelectorBase::~EventSelectorBase()
{
  if (ownOperators_) {
    for (auto* op : operators_)
      delete op;
  }
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

unsigned
EventSelectorBase::index(char const* _name) const
{
  unsigned idx(0);
  for (; idx != operators_.size(); ++idx) {
    if (std::strcmp(operators_[idx]->name(), _name) == 0)
      break;
  }

  return idx;
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
EventSelectorBase::initialize(char const* _outputPath, panda::EventBase& _inEvent, panda::utils::BranchList& _blist, bool _isMC)
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
    if (dynamic_cast<Cut*>(op))
      static_cast<Cut*>(op)->registerCut(*cutsOut_);
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
