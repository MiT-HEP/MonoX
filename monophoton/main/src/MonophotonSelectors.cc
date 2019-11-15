#include "MonophotonSelectors.h"

#include "MonophotonOperators.h"
#include "CommonOperators.h"

#include "TSystem.h"

EventSelector::EventSelector(char const* _name) :
  EventSelectorBase(_name, kEventMonophoton, new panda::EventMonophoton()),
  outEvent_(*static_cast<panda::EventMonophoton*>(outEventBase_))
{
}

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

panda::utils::BranchList
EventSelector::directCopyBranches_(bool _isMC)
{
  auto blist{EventSelectorBase::directCopyBranches_(_isMC)};
  
  blist += {"rho", "vertices"};
  needPrepareFill_(inEvent_->vertices);

  if (_isMC) {
    blist += {"genParticles"};
    needPrepareFill_(inEvent_->genParticles);
  }
  else
    blist += {"metFilters"};

  return blist;
}

panda::utils::BranchList
EventSelector::processedBranches_(bool _isMC) const
{
  panda::utils::BranchList blist = {"weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"};
  if (_isMC)
    blist += {"genJets"}; // filled only if AddGenJets operator is run

  return blist;
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

  auto oItr(operators_.begin());
  bool passUpToLS(runOperators_(oItr, leptonSelection_));

  if (passUpToLS && outEvent_.photons.size() > 1) {
    // Assumption: Photon selector is run
    panda::XPhotonCollection photonsTmp(outEvent_.photons);

    for (auto& photon : photonsTmp) {
      outEvent_.electrons.clear();
      outEvent_.photons.clear();
      outEvent_.photons.push_back(photon);

      bool pass(runOperators_(oItr, operators_.end()));

      fillEvent_(pass);
    }
  }
  else {
    // just run the remaining operators

    bool pass(runOperators_(oItr, operators_.end()));

    fillEvent_(passUpToLS && pass);
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
