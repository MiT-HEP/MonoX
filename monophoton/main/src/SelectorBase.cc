#include "SelectorBase.h"

#include "Operator.h"
#include "photon_extra.h"

#include "PandaTree/Objects/interface/EventMonophoton.h"
#include "PandaTree/Objects/interface/EventTP.h"
#include "PandaTree/Objects/interface/EventSV.h"

#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

#include <cstring>

//--------------------------------------------------------------------
// EventSelectorBase
//--------------------------------------------------------------------

std::mutex EventSelectorBase::mutex;

EventSelectorBase::EventSelectorBase(char const* _name, InputEventType _inputType, panda::EventBase* _outEvent) :
  name_(_name),
  inputType_(_inputType),
  outEventBase_(_outEvent)
{
}

EventSelectorBase::~EventSelectorBase()
{
  if (ownOperators_) {
    for (auto* op : operators_)
      delete op;
  }

  delete outEventBase_;
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
EventSelectorBase::initialize(char const* _outputPath, std::array<panda::EventBase*, nInputEventTypes>& _inEvents, panda::utils::BranchList& _blist, bool _isMC)
{
  if (printLevel_ > 0)
    *stream_ << "Initializing " << className() << "::" << name() << std::endl;

  if (_inEvents[inputType_] == nullptr) {
    switch (inputType_) {
    case kEventBase:
      _inEvents[inputType_] = new panda::EventBase;
      break;
    case kEventMonophoton:
      _inEvents[inputType_] = new panda::EventMonophoton;
      _blist += {"photons", "superClusters", "rho"};
      break;
    case kEventTP:
      _inEvents[inputType_] = new panda::EventTP;
      break;
    case kEventSV:
      _inEvents[inputType_] = new panda::EventSV;
      break;
    default:
      break;
    }
  }

  inEventBase_ = _inEvents[inputType_];
  castInEvent_();

  auto* outputFile(new TFile(_outputPath, "recreate"));

  skimOut_ = new TTree("events", "Events");
  cutsOut_ = new TTree("cutflow", "cutflow");

  skimOut_->Branch("weight_Input", &inWeight_, "weight_Input/D");

  cutsOut_->Branch("runNumber", &inEventBase_->runNumber, "runNumber/i");
  cutsOut_->Branch("lumiNumber", &inEventBase_->lumiNumber, "lumiNumber/i");
  cutsOut_->Branch("eventNumber", &inEventBase_->eventNumber, "eventNumber/i");

  auto blistDirect(directCopyBranches_(_isMC));
  inEventBase_->book(*skimOut_, blistDirect);
  outEventBase_->book(*skimOut_, processedBranches_(_isMC));

  _blist += blistDirect;

  setupSkim_(_isMC);

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
    op->initialize(*inEventBase_);
    auto* cut(dynamic_cast<CutMixin*>(op));
    if (cut != nullptr)
      cut->registerCut(*cutsOut_);
  }

  if (printLevel_ > 0)
    *stream_ << std::endl;

  passes_.resize(operators_.size(), 0);

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
  skimOut_ = nullptr;
  cutsOut_ = nullptr;

  if (printLevel_ > 0 && printLevel_ <= INFO) {
    *stream_ << "Cut results:" << std::endl;
    for (unsigned iO(0); iO != operators_.size(); ++iO) {
      auto* op(operators_[iO]);
      if (dynamic_cast<CutMixin*>(op) != nullptr)
        *stream_ << " " << op->expr() << " " << passes_[iO] << std::endl;
    }
    *stream_ << std::endl;
  }

  if (useTimers_) {
    *stream_ << "Operator runtimes for " << name() << " (CPU seconds):" << std::endl;
    for (unsigned iO(0); iO != operators_.size(); ++iO) {
      stream_->flags(std::ios_base::fixed);
      stream_->width(5);
      *stream_ << " " << (std::chrono::duration_cast<std::chrono::nanoseconds>(timers_[iO]).count() * 1.e-9) << " " << operators_[iO]->name() << std::endl;
    }
  }
}

void
EventSelectorBase::selectEvent()
{
  if (blindPrescale_ > 1 && inEventBase_->runNumber >= blindMinRun_ && inEventBase_->eventNumber % blindPrescale_ != 0)
    return;

  outEventBase_->init();
  inWeight_ = inEventBase_->weight;
  outEventBase_->weight = inEventBase_->weight;

  bool pass(runOperators_());

  fillEvent_(pass);
}

panda::utils::BranchList
EventSelectorBase::directCopyBranches_(bool _isMC)
{
  panda::utils::BranchList blist = {"runNumber", "lumiNumber", "eventNumber", "isData", "npv"};
  if (_isMC) {
    blist += {"npvTrue", "partons", "genVertex"}; // , "genMet"};
    needPrepareFill_(inEventBase_->partons);
  }

  return blist;
}

panda::utils::BranchList
EventSelectorBase::processedBranches_(bool _isMC) const
{
  panda::utils::BranchList blist = {"weight"};

  return blist;
}

bool
EventSelectorBase::runOperators_(OperatorVector::iterator& _oItr, OperatorVector::iterator const& _stop)
{
  Clock::time_point start;
  auto begin(operators_.begin());

  bool pass(true);
  for (; _oItr != _stop; ++_oItr) {
    if (useTimers_)
      start = Clock::now();

    if ((*_oItr)->exec(*inEventBase_, *outEventBase_))
      ++passes_[_oItr - begin];
    else
      pass = false;

    if (useTimers_)
      timers_[_oItr - begin] += Clock::now() - start;
  }

  return pass;
}

void
EventSelectorBase::prepareFill_()
{
  for (auto* coll : directCopyCollections_)
    coll->prepareFill(*skimOut_);
}

void
EventSelectorBase::fillEvent_(bool _pass)
{
  cutsOut_->Fill();

  if (_pass) {
    std::lock_guard<std::mutex> lock(EventSelectorBase::mutex);

    // IMPORTATNT
    // We link these skimOut branches to the input event. Need to refresh the addresses in case
    // collections are resized.
    prepareFill_();
          
    outEventBase_->fill(*skimOut_);
  }
}

/*static*/
void
EventSelectorBase::prepareEvent(unsigned _type, panda::Event const& _inEvent, panda::EventBase& _outEvent, bool _isData)
{
  switch (_type) {
  case kEventMonophoton:
    {
      panda::EventMonophoton& outEvent(static_cast<panda::EventMonophoton&>(_outEvent));
      
      outEvent.copy(_inEvent);

      if (outEvent.run.runNumber != _inEvent.run.runNumber)
        outEvent.run = _inEvent.run;

      for (unsigned iPh(0); iPh != _inEvent.photons.size(); ++iPh)
        panda::photon_extra(outEvent.photons[iPh], _inEvent.photons[iPh], _inEvent.rho, _isData ? nullptr : &outEvent.genParticles);
    }
    break;
  default:
    {
      // copy most of the event content
      _outEvent = _inEvent;

      if (_outEvent.run.runNumber != _inEvent.run.runNumber)
        _outEvent.run = _inEvent.run;
    }
    break;
  }
}
