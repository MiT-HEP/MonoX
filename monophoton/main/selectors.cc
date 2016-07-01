#include "selectors.h"

#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

#include <cstring>

//--------------------------------------------------------------------
// EventSelector
//--------------------------------------------------------------------

void
EventSelector::initialize(char const* _outputPath, simpletree::Event& _event)
{
  auto* outputFile(new TFile(_outputPath, "recreate"));

  skimOut_ = new TTree("events", "Events");
  cutsOut_ = new TTree("cutflow", "cutflow");

  if (_event.getInput()->GetBranch("weight")) { // is MC
    _event.book(*skimOut_, {"run", "lumi", "event", "npv", "partons", "promptFinalStates"}); // branches to be directly copied
    outEvent_.book(*skimOut_, {"weight", "jets", "photons", "electrons", "muons", "taus", "t1Met"});
  }
  else {
    _event.book(*skimOut_, {"run", "lumi", "event", "npv", "metFilters.cschalo"}); // branches to be directly copied
    outEvent_.book(*skimOut_, {"weight", "jets", "photons", "electrons", "muons", "taus", "t1Met"});
  }

  cutsOut_->Branch("run", &_event.run, "run/i");
  cutsOut_->Branch("lumi", &_event.lumi, "lumi/i");
  cutsOut_->Branch("event", &_event.event, "event/i");

  for (auto* op : operators_) {
    op->addBranches(*skimOut_);
    auto* cut(dynamic_cast<Cut*>(op));
    if (cut)
      cut->registerCut(*cutsOut_);
  }
}

void
EventSelector::finalize()
{
  if (!skimOut_)
    return;

  auto* outputFile(skimOut_->GetCurrentFile());
  outputFile->cd();
  skimOut_->Write();
  cutsOut_->Write();

  delete outputFile;
  skimOut_ = 0;
  cutsOut_ = 0;
}

void
EventSelector::selectEvent(simpletree::Event& _event)
{
  if (blindPrescale_ > 1 && _event.run >= blindMinRun_ && _event.event % blindPrescale_ != 0)
    return;

  outEvent_.init();
  outEvent_.weight = _event.weight;

  bool pass(true);
  for (auto* op : operators_) {
    if (!op->exec(_event, outEvent_))
      pass = false;
  }

  if (pass)
    skimOut_->Fill();

  cutsOut_->Fill();
}

Operator*
EventSelector::findOperator(char const* _name) const
{
  for (auto* op : operators_) {
    if (std::strcmp(op->name(), _name) == 0)
      return op;
  }

  return 0;
}

//--------------------------------------------------------------------
// ZeeEventSelector
//--------------------------------------------------------------------

ZeeEventSelector::ZeeEventSelector(char const* name) :
  EventSelector(name)
{
  operators_.push_back(new HLTFilter("HLT_Ele23_WPLoose_Gsf"));
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
ZeeEventSelector::selectEvent(simpletree::Event& _event)
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
  unsigned sels[] = {HOverE, Sieie, CHWorstIso, NHIso, PhIso, MIP49, Time, SieieNonzero, NoisyRegion};
  for (unsigned sel : sels) {
    addSelection(true, sel);
    addVeto(true, sel);
  }
  
  addSelection(false, EVeto);
  addVeto(true, EVeto);
}

bool
ZeeEventSelector::EEPairSelection::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  eePairs_.clear();

  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    if (!photon.isEB || photon.pt < minPt_)
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

      if (!electron.loose || electron.pt < 10.)
        continue;

      if (electron.dR2(photon) < 0.01)
        continue;

      if (iElectron < _event.electrons.size())
        break;

      if (electron.tight && electron.pt > 30. && (_event.run == 1 || electron.matchHLT[simpletree::fEl23Loose]))
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
WlnuSelector::selectEvent(simpletree::Event& _event)
{
  for (auto& parton : _event.partons) {
    if (std::abs(parton.pid) == 11)
      return;
  }

  EventSelector::selectEvent(_event);
}

//--------------------------------------------------------------------
// WenuSelector
//--------------------------------------------------------------------

void
WenuSelector::selectEvent(simpletree::Event& _event)
{
  unsigned iP(0);
  for (; iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);
    if (std::abs(parton.pid) == 11)
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
NormalizingSelector::finalize()
{
  if (!skimOut_)
    return;

  auto* hSumW(new TH1D("sumW", "", 1, 0., 1.));
  hSumW->Sumw2();
  skimOut_->Draw("0.5>>sumW", "weight * (" + normCut_ + ")", "goff");
  double sumW(hSumW->GetBinContent(1));
  delete hSumW;

  auto* outputFile(skimOut_->GetCurrentFile());
  TString outName(outputFile->GetName());
  TString tmpName(outName);
  tmpName.ReplaceAll(".root", "_tmp.root");

  auto* trueOutput(TFile::Open(tmpName, "recreate"));
  auto* trueSkim(skimOut_->CloneTree(0));
  double weight(0.);
  trueSkim->SetBranchAddress("weight", &weight);

  long iEntry(0);
  while (skimOut_->GetEntry(iEntry++)) {
    weight = norm_ / sumW * outEvent_.weight;
    trueSkim->Fill();
  }

  trueOutput->cd();
  trueSkim->Write();
  auto* trueCuts(cutsOut_->CloneTree());
  trueCuts->Write();

  delete trueOutput;
  delete outputFile;

  skimOut_ = 0;
  cutsOut_ = 0;

  gSystem->Rename(tmpName, outName);
}

//--------------------------------------------------------------------
// SmearingSelector
//--------------------------------------------------------------------

void
SmearingSelector::selectEvent(simpletree::Event& _event)
{
  if (!func_)
    return;

  // smearing the MET only - total pT will be inconsistent
  double originalMet(_event.t1Met.met);

  _event.weight /= nSamples_;

  for (unsigned iS(0); iS != nSamples_; ++iS) {
    _event.t1Met.met = originalMet + func_->GetRandom();
  
    EventSelector::selectEvent(_event);
  }
}
