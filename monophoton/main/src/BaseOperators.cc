#include "BaseOperators.h"

#include "TH1.h"
#include "TF1.h"
#include "TGraph.h"

#include <iostream>
#include <functional>
#include <fstream>

//--------------------------------------------------------------------
// Base
//--------------------------------------------------------------------

bool
Cut::exec(panda::EventBase const& _event, panda::EventBase& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
Modifier::exec(panda::EventBase const& _event, panda::EventBase& _outEvent)
{
  apply(_event, _outEvent);
  return true;
}

//--------------------------------------------------------------------
// HLTFilter
//--------------------------------------------------------------------

HLTFilter::HLTFilter(char const* name) :
  Cut(name)
{
  pathNames_ = name;
}

HLTFilter::~HLTFilter()
{
  tokens_.clear();
}

void
HLTFilter::initialize(panda::EventBase& _event)
{
  Ssiz_t pos(0);
  TString path;
  UInt_t token(0);

  if (printLevel_ > 0)
    *stream_ << "Triggers to add: " << pathNames_ << std::endl;

  while (pathNames_.Tokenize(path, pos, "_OR_")) {
    token = _event.registerTrigger(path.Data());
    tokens_.push_back(token);
    if (printLevel_ > 0)
      *stream_ << "Added trigger path " << path << " with token " << token << " to tokens vector." << std::endl;
  }
}

void
HLTFilter::addBranches(TTree& _skimTree)
{
  _skimTree.Branch(pathNames_, &pass_, pathNames_ + "/O");
}

bool
HLTFilter::pass(panda::EventBase const& _event, panda::EventBase&)
{
  // make sure a trigger menu exists; will return a human readable error if not
  _event.run.triggerMenu();

  pass_ = false;

  for (auto& token : tokens_) {
    if (_event.triggerFired(token)) {
      pass_ = true;
      break;
    }
  }
  
  return pass_;
}

//--------------------------------------------------------------------
// EventVeto
//--------------------------------------------------------------------

void
EventVeto::addSource(char const* _path)
{
  std::ifstream input(_path);
  std::string line;

  while (true) {
    std::getline(input, line);
    if (!input.good())
      break;

    unsigned run(std::atoi(line.substr(0, line.find(":")).c_str()));
    unsigned lumi(std::atoi(line.substr(line.find(":") + 1, line.rfind(":")).c_str()));
    unsigned event(std::atoi(line.substr(line.rfind(":") + 1).c_str()));

    list_[run][lumi].insert(event);
  }
}

void
EventVeto::addEvent(unsigned run, unsigned lumi, unsigned event)
{
  list_[run][lumi].insert(event);
}

bool
EventVeto::pass(panda::EventBase const& _event, panda::EventBase&)
{
  auto rItr(list_.find(_event.runNumber));
  if (rItr == list_.end())
    return true;

  auto lItr(rItr->second.find(_event.lumiNumber));
  if (lItr == rItr->second.end())
    return true;

  auto eItr(lItr->second.find(_event.eventNumber));
  return eItr == lItr->second.end();
}

//--------------------------------------------------------------------
// GenPhotonVeto
//--------------------------------------------------------------------

bool
GenPhotonVeto::pass(panda::EventBase const& _event, panda::EventBase&)
{
  auto& genParticles(*_event.genParticleCollection());
  
  for (unsigned iG(0); iG != genParticles.size(); ++iG) {
    auto& part(genParticles[iG]);

    if (!part.finalState)
      continue;

    if (part.pdgid != 22)
      continue;

    if (part.pt() < minPt_)
      continue;

    unsigned iP(0);
    for (; iP != _event.partons.size(); ++iP) {
      auto& parton(_event.partons[iP]);
      if (parton.dR2(part) < minPartonDR2_)
        break;
    }
    if (iP != _event.partons.size())
      continue;

    return false;
  }

  return true;
}

//--------------------------------------------------------------------
// PartonKinematics
//--------------------------------------------------------------------

void
PartonKinematics::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("genPhoton.pt", &phoPt_, "genPhoton.pt/F");
  _skimTree.Branch("genPhoton.eta", &phoEta_, "genPhoton.eta/F");
  _skimTree.Branch("genPhoton.phi", &phoPhi_, "genPhoton.phi/F");

  _skimTree.Branch("genMet.pt", &metPt_, "genMet.pt/F");
  _skimTree.Branch("genMet.phi", &metPhi_, "genMet.phi/F");
}

void
PartonKinematics::apply(panda::EventBase const& _event, panda::EventBase&)
{
  phoPt_ = -1;
  phoEta_ = -1;
  phoPhi_ = -1;

  metPt_ = -1;
  metPhi_ = -1;

  long absid(0.);
  double mpx(0.);
  double mpy(0.);

  for (auto& parton : _event.partons) {
    absid = std::abs(parton.pdgid);
    if (absid == 22 && parton.pt() > phoPt_) {
      phoPt_ = parton.pt();
      phoEta_ = parton.eta();
      phoPhi_ = parton.phi();
    }
    
    else if (absid == 12 || absid == 14 || absid == 16 || absid == 51 || absid == 52 || absid == 53 || absid == 1000012 || absid == 2000012 || absid == 3000012) {
      mpx += parton.pt() * std::cos(parton.phi());
      mpy += parton.pt() * std::sin(parton.phi());
    }
  }

  metPt_ = std::sqrt(mpx * mpx + mpy * mpy);
  metPhi_ = std::atan2(mpy, mpx);
}


//--------------------------------------------------------------------
// PartonFlavor
//--------------------------------------------------------------------

bool
PartonFlavor::pass(panda::EventBase const& _event, panda::EventBase&)
{
  if (_event.partons.size() == 0)
    return false;

  for (auto& parton : _event.partons) {
    unsigned absId(std::abs(parton.pdgid));
    if (absId == rejectedId_)
      return false;
    if (absId == requiredId_)
      return true;
  }

  // if requiredId is set, reaching here means the event does not have the target parton -> false
  // if requiredId is not set, we return true.
  return requiredId_ == 0;
}

//--------------------------------------------------------------------
// GenPhotonPtTruncator
//--------------------------------------------------------------------

bool
GenPhotonPtTruncator::pass(panda::EventBase const& _event, panda::EventBase&)
{
  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);

    if (parton.pdgid == 22 && (parton.pt() < min_ || parton.pt() > max_))
      return false;
  }

  return true;
}

//--------------------------------------------------------------------
// GenHtTruncator
//--------------------------------------------------------------------

void
GenHtTruncator::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("genHt", &ht_, "genHt/F");
}

bool
GenHtTruncator::pass(panda::EventBase const& _event, panda::EventBase&)
{
  ht_ = 0.; // ht is an additive quantity; need to start with 0.
  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);

    if ( !(parton.pdgid == 21 || std::abs(parton.pdgid) < 6))
      continue;

    ht_ += parton.pt();
  }

  if (ht_ < min_ || ht_ > max_)
      return false;

  return true;
}

//--------------------------------------------------------------------
// GenBosonPtTruncator
//--------------------------------------------------------------------

void
GenBosonPtTruncator::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("genBosonPt", &pt_, "genBosonPt/F");
}

bool
GenBosonPtTruncator::pass(panda::EventBase const& _event, panda::EventBase&)
{
  pt_ = -1.;
  unsigned nLep = 0;
  TLorentzVector genBoson(0., 0., 0., 0.);

  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);

    // don't run on diboson samples for now
    if (nLep > 2)
      break;

    if ( (std::abs(parton.pdgid) < 11) || (std::abs(parton.pdgid) > 16) )
      continue;

    genBoson += parton.p4();
    nLep++;
  }

  if (nLep == 2)
    pt_ = genBoson.Pt();

  if (pt_ < min_ || pt_ > max_)
      return false;

  return true;
}

//--------------------------------------------------------------------
// GenParticleSelection
//--------------------------------------------------------------------

bool
GenParticleSelection::pass(panda::EventBase const& _event, panda::EventBase&)
{
  auto& genParticles(*_event.genParticleCollection());
  
  for (unsigned iP(0); iP != genParticles.size(); ++iP) {
    auto& part(genParticles[iP]);

    if (std::abs(part.pdgid) != pdgId_)
      continue;

    if (std::abs(part.eta()) > maxEta_ || std::abs(part.eta()) < minEta_ )
      continue;

    if (part.pt() < minPt_ || part.pt() > maxPt_)
      continue;

    return true;
  }

  return false;
}

//--------------------------------------------------------------------
// ConstantWeight
//--------------------------------------------------------------------

void
ConstantWeight::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("weight_" + name_, &weight_, "weight_" + name_ + "/D");
  if (weightUp_ >= 0.)
    _skimTree.Branch("reweight_" + name_ + "Up", &weightUp_, "reweight_" + name_ + "Up/D");
  if (weightDown_ >= 0.)
    _skimTree.Branch("reweight_" + name_ + "Down", &weightDown_, "reweight_" + name_ + "Down/D");
}

//--------------------------------------------------------------------
// NNPDFVariation
//--------------------------------------------------------------------

void
NNPDFVariation::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("reweight_pdfUp", &weightUp_, "reweight_pdfUp/D");
  _skimTree.Branch("reweight_pdfDown", &weightDown_, "reweight_pdfDown/D");
}

void
NNPDFVariation::apply(panda::EventBase const& _event, panda::EventBase&)
{
  // need to implement new version of pdf weights
  weightUp_ = 1.; // + _event.genReweight.pdfDW * rescale_;
  weightDown_ = 1.; // - _event.genReweight.pdfDW * rescale_;
}

//--------------------------------------------------------------------
// GJetsDR
//--------------------------------------------------------------------

void
GJetsDR::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("genPhotonDR", &minDR_, "genPhotonDR/F");
}

void
GJetsDR::apply(panda::EventBase const& _event, panda::EventBase&)
{
  minDR_ = -1.;

  for (auto& photon : _event.partons) {
    if (std::abs(photon.pdgid) != 22)
      continue;

    for (auto& parton : _event.partons) {
      if (&parton == &photon)
        continue;

      unsigned absId(std::abs(parton.pdgid));
      if (!(absId == 21 || absId < 7))
        continue;

      double dR(photon.dR(parton));
      if (minDR_ < 0. || dR < minDR_)
        minDR_ = dR;
    }
  }
}

//--------------------------------------------------------------------
// PUWeight
//--------------------------------------------------------------------

void
PUWeight::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("weight_" + name_, &weight_, "weight_" + name_ + "/D");
}

void
PUWeight::apply(panda::EventBase const& _event, panda::EventBase& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npvTrue));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  weight_ = factors_->GetBinContent(iX);

  _outEvent.weight *= weight_;
}
