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
Cut::exec(panda::EventMonophoton const& _event, panda::EventBase& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
Modifier::exec(panda::EventMonophoton const& _event, panda::EventBase& _outEvent)
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
HLTFilter::initialize(panda::EventMonophoton& _event)
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
HLTFilter::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
EventVeto::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
// MetFilters
//--------------------------------------------------------------------

bool
MetFilters::pass(panda::EventMonophoton const& _event, panda::EventBase&)
{
  if (!_event.metFilters.hbhe && !_event.metFilters.hbheIso && !_event.metFilters.ecalDeadCell && !_event.metFilters.goodVertices && !_event.metFilters.badsc && !_event.metFilters.badMuons && !_event.metFilters.duplicateMuons && !_event.metFilters.badPFMuons && !_event.metFilters.badChargedHadrons) {
    if (halo_) 
      return true;
    else {
      if (!_event.metFilters.globalHalo16)
	return true;
      else
	return false;
    }
  }
  else 
    return false;
}

//--------------------------------------------------------------------
// GenPhotonVeto
//--------------------------------------------------------------------

bool
GenPhotonVeto::pass(panda::EventMonophoton const& _event, panda::EventBase&)
{
  for (unsigned iG(0); iG != _event.genParticles.size(); ++iG) {
    auto& part(_event.genParticles[iG]);

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
PartonKinematics::apply(panda::EventMonophoton const& _event, panda::EventBase&)
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
PartonFlavor::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
GenPhotonPtTruncator::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
GenHtTruncator::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
GenBosonPtTruncator::pass(panda::EventMonophoton const& _event, panda::EventBase&)
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
GenParticleSelection::pass(panda::EventMonophoton const& _event, panda::EventBase&)
{
  for (unsigned iP(0); iP != _event.genParticles.size(); ++iP) {
    auto& part(_event.genParticles[iP]);

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
// EcalCrackVeto
//--------------------------------------------------------------------

void
EcalCrackVeto::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("ecalCrackVeto", &ecalCrackVeto_, "ecalCrackVeto/O");
}

bool
EcalCrackVeto::pass(panda::EventMonophoton const& _event, panda::EventBase&)
{
  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);

    if (photon.scRawPt < minPt_)
      continue;

    if (std::abs(photon.eta()) > 1.4 && std::abs(photon.eta()) < 1.6) {
      ecalCrackVeto_ = false;
      return false;
    }
  }
  
  for (unsigned iJ(0); iJ != _event.jets.size(); ++iJ) {
    auto& jet(_event.jets[iJ]);

    if (jet.pt() < minPt_)
      continue;

    if (std::abs(jet.eta()) > 1.4 && std::abs(jet.eta()) < 1.6) {
      ecalCrackVeto_ = false;
      return false;
    }
  }

  ecalCrackVeto_ = true;
  return true;
}

//--------------------------------------------------------------------
// TagAndProbePairZ
//--------------------------------------------------------------------

TagAndProbePairZ::TagAndProbePairZ(char const* name) :
  Cut(name),
  tp_("tp")
{
}

TagAndProbePairZ::~TagAndProbePairZ()
{
  delete tags_;
  delete probes_;
}

void
TagAndProbePairZ::addBranches(TTree& _skimTree)
{
  switch (tagSpecies_) {
  case cMuons:
    tags_ = new panda::MuonCollection("tag");
    break;
  case cElectrons:
    tags_ = new panda::ElectronCollection("tag");
    break;
  case cPhotons:
    tags_ = new panda::XPhotonCollection("tag");
    break;
  default:
    throw runtime_error("Invalid tag species");
  }

  switch (probeSpecies_) {
  case cMuons:
    probes_ = new panda::MuonCollection("probe");
    break;
  case cElectrons:
    probes_ = new panda::ElectronCollection("probe");
    break;
  case cPhotons:
    probes_ = new panda::XPhotonCollection("probe");
    break;
  default:
    throw runtime_error("Invalid tag species");
  }

  tp_.book(_skimTree);
  _skimTree.Branch("tp.oppSign", &zOppSign_, "tp.oppSign/O");

  tags_->book(_skimTree);
  probes_->book(_skimTree);
}

bool
TagAndProbePairZ::pass(panda::EventMonophoton const& _event, panda::EventBase&)
{
  panda::LeptonCollection const* inTags(0);
  panda::LeptonCollection const* inProbes(0);
  TLorentzVector tnpPair(0., 0., 0., 0.);

  // OK, object-orientation and virtual methods cannot quite solve the problem at hand (push back the objects with full info).
  // We will cheat.
  std::function<void(panda::Particle const&)> push_back_tag;
  std::function<void(panda::Particle const&)> push_back_probe;

  switch (tagSpecies_) {
  case cMuons:
    inTags = &_event.muons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::MuonCollection*>(this->tags_)->push_back(static_cast<panda::Muon const&>(tag));
    };
    break;
  case cElectrons:
    inTags = &_event.electrons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::ElectronCollection*>(this->tags_)->push_back(static_cast<panda::Electron const&>(tag));
    };
    break;
  case cPhotons:
    // inTags = &_event.photons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::XPhotonCollection*>(this->tags_)->push_back(static_cast<panda::XPhoton const&>(tag));
    };
    break;
  default:
    throw runtime_error("Invalid tag species");
  }
  
  switch (probeSpecies_) {
  case cMuons:
    inProbes = &_event.muons;
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::MuonCollection*>(this->probes_)->push_back(static_cast<panda::Muon const&>(probe));
    };
    break;
  case cElectrons:
    inProbes = &_event.electrons;
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::ElectronCollection*>(this->probes_)->push_back(static_cast<panda::Electron const&>(probe));
    };
    break;
  case cPhotons:
    // inProbes = &_event.photons; 
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::XPhotonCollection*>(this->probes_)->push_back(static_cast<panda::XPhoton const&>(probe));
    };
    break;
  default:
    throw runtime_error("Invalid tag species");
  }

  tp_.clear();
  tags_->clear();
  probes_->clear();
  nUniqueZ_ = 0;

  for (unsigned iT(0); iT != inTags->size(); ++iT) {
    auto& tag = inTags->at(iT);
    
    if ( !(tag.tight && tag.pt() > 30.))
      continue;
    
    for (unsigned iP(0); iP != inProbes->size(); ++iP) {
      auto& probe = inProbes->at(iP);
      
      if ( !(probe.loose && probe.pt() > 20.))
	continue;

      // don't want the same object in case the tag and probe collections are the same
      // currently going with dR < 0.3, maybe change?
      if (tag.dR2(probe) < 0.09 ) 
	continue;

      tnpPair = (tag.p4() + probe.p4());
      double mass(tnpPair.M());
      // tighter mass range was just so I could use cutresult to debug, switched backed
      if ( !(mass > 60. && mass < 120.))
	continue;

      push_back_tag(tag);
      push_back_probe(probe);

      // cannot push back here; resize and use the last element
      tp_.resize(tp_.size() + 1);
      auto& z(tp_.back());
      z.setPtEtaPhiM(tnpPair.Pt(), tnpPair.Eta(), tnpPair.Phi(), tnpPair.M());
      zOppSign_ = ( (tag.charge == probe.charge) ? 0 : 1);

      // check if other tag-probe pairs match this pair
      unsigned iZ(0);
      for (; iZ != tp_.size() - 1; ++iZ) {
        if ((tag.dR2(tags_->at(iZ)) < 0.09 && probe.dR2(probes_->at(iZ)) < 0.09) ||
            (tag.dR2(probes_->at(iZ)) < 0.09 && probe.dR2(tags_->at(iZ)) < 0.09))
          break;
      }
      // if not, increment unique Z counter
      if (iZ == tp_.size() -1)
        ++nUniqueZ_;
    }
  }

  return tp_.size() != 0;
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
// NPVWeight
//--------------------------------------------------------------------

void
NPVWeight::apply(panda::EventMonophoton const& _event, panda::EventBase& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npv));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  _outEvent.weight *= factors_->GetBinContent(iX);
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
NNPDFVariation::apply(panda::EventMonophoton const& _event, panda::EventBase&)
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
GJetsDR::apply(panda::EventMonophoton const& _event, panda::EventBase&)
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
PUWeight::apply(panda::EventMonophoton const& _event, panda::EventBase& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npvTrue));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  weight_ = factors_->GetBinContent(iX);

  _outEvent.weight *= weight_;
}
