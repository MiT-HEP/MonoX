#include "operators.h"

#include "TH1.h"
#include "TF1.h"

//#include "jer.h"

#include <iostream>
#include <functional>

//--------------------------------------------------------------------
// Base
//--------------------------------------------------------------------

bool
Cut::exec(panda::Event const& _event, panda::Event& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
Modifier::exec(panda::Event const& _event, panda::Event& _outEvent)
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
HLTFilter::initialize(panda::Event& _event)
{
  Ssiz_t pos(0);
  TString path;
  UInt_t token(0);
  
  printf("Triggers to add: %s \n", pathNames_.Data());

  while (pathNames_.Tokenize(path, pos, "_OR_")) {
    token = _event.registerTrigger(path.Data());
    tokens_.push_back(token);
    printf("Added trigger path %s with token %u to tokens vector. \n", path.Data(), token);
  }
}


bool
HLTFilter::pass(panda::Event const& _event, panda::Event&)
{
  for (auto token : tokens_) {
    if (_event.triggerFired(token))
      return true;
  }

  return false;
}

//--------------------------------------------------------------------
// MetFilters
//--------------------------------------------------------------------

void
MetFilters::setEventList(char const* _path, int _decision)
{
  eventLists_.emplace_back(EventList(_path), _decision);
}

bool
MetFilters::pass(panda::Event const& _event, panda::Event&)
{
  bool fired[] = {
    _event.metFilters.globalHalo16,
    _event.metFilters.hbhe,
    _event.metFilters.hbheIso,
    _event.metFilters.badsc,
    _event.metFilters.badTrack,
    _event.metFilters.badMuonTrack
  };

  for (unsigned iF(0); iF != 6; ++iF) {
    if (fired[iF]) {
      if (filterConfig_[iF] == 1)
        return false;
    }
    else {
      if (filterConfig_[iF] == -1)
        return false;
    }
  }

  unsigned iList(0);
  for (auto& eventList : eventLists_) {
    iList++;
    if (eventList.first.inList(_event)) {
      if (eventList.second == 1)
        return false;
    }
    else {
      if (eventList.second == -1)
        return false;
    }
  }

  return true;
}

//--------------------------------------------------------------------
// GenPhotonVeto
//--------------------------------------------------------------------

bool
GenPhotonVeto::pass(panda::Event const& _event, panda::Event&)
{
  for (unsigned iG(0); iG != _event.genParticles.size(); ++iG) {
    auto& part(_event.genParticles[iG]);
    // might need to add a check on if is promptFinalState
    /*
    if (part.statusFlags != "someCondition")
      continue;
    */

    if (part.pdgid != 22)
      continue;

    if (part.pt < minPt_)
      continue;

    unsigned iP(0);
    for (; iP != _event.partons.size(); ++iP) {
      auto& parton(_event.partons[iP]);
      if (parton.dR2(part) < minDR_ * minDR_)
        break;
    }
    if (iP != _event.partons.size())
      continue;

    return false;
  }

  return true;
}

//--------------------------------------------------------------------
// PhotonSelection
//--------------------------------------------------------------------

void
PhotonSelection::registerCut(TTree& cutsTree)
{
  cutsTree.Branch(name_, &nominalResult_, name_ + "/O");

  cutsTree.Branch(name_ + "Bits", cutRes_, name_ + TString::Format("Bits[%d]/O", nSelections));
}

void
PhotonSelection::addBranches(TTree& _skimTree)
{
  // add pt variation branches for simple selections.
  // vetoes are used for control regions, which would not require pt variation systematics studies.
  if (vetoes_.size() == 0) {
    _skimTree.Branch("photons.ptVarUp", ptVarUp_, "ptVarUp[photons.size]/F");
    _skimTree.Branch("photons.ptVarDown", ptVarDown_, "ptVarDown[photons.size]/F");
  }
}

void
PhotonSelection::addSelection(bool _pass, unsigned _s1, unsigned _s2/* = nSelections*/, unsigned _s3/* = nSelections*/)
{
  BitMask sel;
  sel.set(_s1);
  if (_s2 != nSelections)
    sel.set(_s2);
  if (_s3 != nSelections)
    sel.set(_s3);

  selections_.emplace_back(_pass, sel);
}

void
PhotonSelection::removeSelection(unsigned _s1, unsigned _s2/* = nSelections*/, unsigned _s3/* = nSelections*/)
{
  BitMask sel;
  sel.set(_s1);
  if (_s2 != nSelections)
    sel.set(_s2);
  if (_s3 != nSelections)
    sel.set(_s3);

  for (auto&& itr(selections_.begin()); itr != selections_.end(); ++itr) {
    if (itr->second == sel) {
      selections_.erase(itr);
      std::cout << "Removed photon selection " << sel.to_string() << std::endl;
    }
  }
}

void
PhotonSelection::addVeto(bool _pass, unsigned _s1, unsigned _s2/* = nSelections*/, unsigned _s3/* = nSelections*/)
{
  BitMask sel;
  sel.set(_s1);
  if (_s2 != nSelections)
    sel.set(_s2);
  if (_s3 != nSelections)
    sel.set(_s3);

  vetoes_.emplace_back(_pass, sel);
}

void
PhotonSelection::removeVeto(unsigned _s1, unsigned _s2/* = nSelections*/, unsigned _s3/* = nSelections*/)
{
  BitMask sel;
  sel.set(_s1);
  if (_s2 != nSelections)
    sel.set(_s2);
  if (_s3 != nSelections)
    sel.set(_s3);

  for (auto&& itr(vetoes_.begin()); itr != vetoes_.end(); ++itr) {
    if (itr->second == sel) {
      vetoes_.erase(itr);
      std::cout << "Removed photon selection " << sel.to_string() << std::endl;
    }
  }
}

double
PhotonSelection::ptVariation(panda::Photon const& _photon, bool up)
{
  // photon.scRawPt not filled in test sample
  // need to uncomment this part once it's there
  if (up)
    // return _photon.scRawPt * 1.015;
    return _photon.pt * 1.015;
  else
    // return _photon.scRawPt * 0.985;
    return _photon.pt * 0.985;
}

bool
PhotonSelection::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  
  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);
    
    // photon.isEB not filled in test sample
    // need to uncomment this part once it's there
    /*
    if (!photon.isEB)
      continue;
    */
    
    if (vetoes_.size() == 0) {
      // veto is not set -> this is a simple photon selection. Pass if upward variation is above the threshold.
      if (ptVariation(photon, true) < minPt_)
        continue;
    }
    else {
      if (photon.scRawPt < minPt_)
        continue;
    }

    int selection(selectPhoton(photon));

    // printf("Photon %u returned selection %d \n", iP, selection);

    if (selection < 0) {
      // vetoed
      _outEvent.photons.clear();
      break;
    }
    else if (selection > 0) {
      if (vetoes_.size() == 0) {
        ptVarUp_[_outEvent.photons.size()] = ptVariation(photon, true);
        ptVarDown_[_outEvent.photons.size()] = ptVariation(photon, false);
      }
      _outEvent.photons.push_back(photon);
    }
  }
  
  // photon.scRawPt not filled in test sample
  // need to uncomment this part once it's there
  // nominalResult_ = _outEvent.photons.size() != 0 && _outEvent.photons[0].scRawPt > minPt;
  nominalResult_ = _outEvent.photons.size() != 0 && _outEvent.photons[0].pt > minPt_;

  return _outEvent.photons.size() != 0;
}

int
PhotonSelection::selectPhoton(panda::Photon const& _photon)
{
  BitMask cutres;
  cutres[HOverE] = _photon.passHOverE(wp_, 0);
  cutres[Sieie] = _photon.passSieie(wp_, 0);
  cutres[CHIso] = _photon.passCHIsoS15(wp_);
  cutres[NHIso] = _photon.passNHIsoS15(wp_);
  cutres[PhIso] = _photon.passPhIsoS15(wp_);
  cutres[CHIsoMax] = (_photon.chIsoMax < panda::Photon::chIsoCuts[0][0][wp_]);
  cutres[EVeto] = _photon.pixelVeto;
  cutres[CSafeVeto] = _photon.csafeVeto;
  cutres[MIP49] = (_photon.mipEnergy < 4.9);
  cutres[Time] = (std::abs(_photon.time) < 3.);
  cutres[SieieNonzero] = (_photon.sieie > 0.001);
  cutres[SipipNonzero] = (_photon.sipip > 0.001);
  cutres[NoisyRegion] = !(_photon.eta > 0. && _photon.eta < 0.15 && _photon.phi > 0.527580 && _photon.phi < 0.541795);
  cutres[E2E995] = (_photon.emax + _photon.e2nd) / _photon.e33 < 0.95;
  cutres[Sieie12] = (_photon.sieie < 0.012);
  cutres[Sieie15] = (_photon.sieie < 0.015);
  cutres[Sieie20] = (_photon.sieie < 0.020);
  cutres[CHIso11] = (_photon.chIsoS15 < 11.);
  cutres[CHIsoMax11] = (_photon.chIsoMax < 11.);
  cutres[NHIsoLoose] = _photon.passNHIsoS15(0);
  cutres[PhIsoLoose] = _photon.passPhIsoS15(0);
  cutres[NHIsoTight] = _photon.passNHIsoS15(2);
  cutres[PhIsoTight] = _photon.passPhIsoS15(2);
  cutres[Sieie05] = (_photon.sieie < 0.005);
  cutres[Sipip05] = (_photon.sipip < 0.005);
  cutres[NHIsoS16] = _photon.passNHIso(wp_);
  cutres[PhIsoS16] = _photon.passPhIso(wp_);
  cutres[CHIsoS16] = _photon.passCHIso(wp_);
  cutres[CHIsoMaxS16] = (_photon.chIsoMax < panda::Photon::chIsoCuts[1][0][wp_]);
  cutres[NHIsoS16VLoose] = (_photon.nhIso < 50.); // loose WP cut is 42.7 at 1 TeV (22.6 @ 500 GeV)
  cutres[PhIsoS16VLoose] = (_photon.phIso < 11.); // loose WP cut is 8.3 at 1 TeV
  cutres[CHIsoS16VLoose] = (_photon.chIso < 11.); 
  cutres[NHIsoS16Tight] = _photon.passNHIso(2);
  cutres[PhIsoS16Tight] = _photon.passPhIso(2);

  for (unsigned iC(0); iC != nSelections; ++iC) {
    cutRes_[iC] = cutres[iC];
  }

  if (vetoes_.size() != 0) {
    unsigned iV(0);
    for (; iV != vetoes_.size(); ++iV) {
      BitMask& mask(vetoes_[iV].second);

      if (vetoes_[iV].first) { // passing at least one of OR'ed cuts required
        if ((mask & cutres).none()) // but it failed all
          break;
      }
      else { // failing at least one of OR'ed cuts required
        if ((mask & cutres) == mask) // but it passed all
          break;
      }
    }
    if (iV == vetoes_.size()) // all veto requirements matched
      return -1;
  }

  if (selections_.size() != 0) {
    unsigned iS(0);
    for (; iS != selections_.size(); ++iS) {
      BitMask& mask(selections_[iS].second);

      if (selections_[iS].first) {
        if ((mask & cutres).none())
          break;
      }
      else {
        if ((mask & cutres) == mask)
          break;
      }
    }
    if (iS == selections_.size()) // all selection requirements matched
      return 1;
  }
    
  return 0;
}

//--------------------------------------------------------------------
// ElectronVeto
//--------------------------------------------------------------------

bool
ElectronVeto::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  panda::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.muons
  };

  bool hasNonOverlapping(false);
  for (unsigned iE(0); iE != _event.electrons.size(); ++iE) {
    auto& electron(_event.electrons[iE]);
    if (!electron.loose || electron.pt < 10.)
      continue;

    _outEvent.electrons.push_back(electron);

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(electron) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was a matching candidate
        overlap = true;
        break;
      }
    }
    if (!overlap)
      hasNonOverlapping = true;
  }

  return !hasNonOverlapping;
}

//--------------------------------------------------------------------
// MuonVeto
//--------------------------------------------------------------------

bool
MuonVeto::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  panda::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.electrons
  };

  bool hasNonOverlapping(false);
  for (unsigned iM(0); iM != _event.muons.size(); ++iM) {
    auto& muon(_event.muons[iM]);
    if (!muon.loose || muon.pt < 10.)
      continue;

    _outEvent.muons.push_back(muon);

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(muon) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was a matching candidate
        overlap = true;
        break;
      }
    }
    if (!overlap)
      hasNonOverlapping = true;
  }

  return !hasNonOverlapping;
}

//--------------------------------------------------------------------
// TauVeto
//--------------------------------------------------------------------

bool
TauVeto::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  unsigned iTau(0);
  bool hasNonOverlapping(false);
  for (; iTau != _event.taus.size(); ++iTau) {
    auto& tau(_event.taus[iTau]);

    // might not be the right iso variable
    if (!tau.decayMode || tau.isoDeltaBetaCorr > 5.)
      continue;

    unsigned iE(0);
    for (; iE != _event.electrons.size(); ++iE) {
      auto& electron(_event.electrons[iE]);
      if (electron.loose && tau.dR2(electron) < 0.16)
        break;
    }
    if (iE != _event.electrons.size())
      continue;

    unsigned iM(0);
    for (; iM != _event.muons.size(); ++iM) {
      auto& muon(_event.muons[iM]);
      if (muon.loose && tau.dR2(muon) < 0.16)
        break;
    }
    if (iM != _event.muons.size())
      continue;

    _outEvent.taus.push_back(tau);
    hasNonOverlapping = true;
  }

  return !hasNonOverlapping;
}

//--------------------------------------------------------------------
// LeptonMt
//--------------------------------------------------------------------

bool
LeptonMt::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  panda::Lepton const* lepton(0);
  if (flavor_ == kElectron && _outEvent.electrons.size() != 0)
    lepton = &_outEvent.electrons[0];
  else if (flavor_ == kMuon && _outEvent.muons.size() != 0)
    lepton = &_outEvent.muons[0];

  if (!lepton)
    return false;

  double mt2(2. * _event.met.pt * lepton->pt * (1. - std::cos(lepton->phi - _event.met.phi)));

  return mt2 > min_ * min_ && mt2 < max_ * max_;
}

//--------------------------------------------------------------------
// Mass
//--------------------------------------------------------------------

void
Mass::addBranches(TTree& _skimTree)
{
  _skimTree.Branch(prefix_ + ".mass", &mass_, "mass");
}

bool
Mass::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  mass_ = -1.;

  panda::ParticleCollection const* col[2]{};

  for (unsigned ic : {0, 1}) {
    switch (col_[ic]) {
    case kPhotons:
      col[ic] = &_outEvent.photons;
      break;
    case kElectrons:
      col[ic] = &_outEvent.electrons;
      break;
    case kMuons:
      col[ic] = &_outEvent.muons;
      break;
    case kTaus:
      col[ic] = &_outEvent.taus;
      break;
    default:
      break;
    }
  }

  if (!col[0] || !col[1] || col[0]->size() == 0 || col[1]->size() == 0)
    return false;

  if (col[0] == col[1]) {
    if (col[0]->size() == 1)
      return false;

    mass_ = (col[0]->at(0).p4() + col[0]->at(1).p4()).M();
  }
  else
    mass_ = (col[0]->at(0).p4() + col[1]->at(0).p4()).M();

  return mass_ > min_ && mass_ < max_;
}

//--------------------------------------------------------------------
// OppositeSign
//--------------------------------------------------------------------

void
OppositeSign::addBranches(TTree& _skimTree)
{
  _skimTree.Branch(prefix_ + ".oppSign", &oppSign_, "oppSign/O");
}

bool
OppositeSign::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  oppSign_ = 0;

  panda::LeptonCollection const* col[2]{};

  for (unsigned ic : {0, 1}) {
    switch (col_[ic]) {
    case kElectrons:
      col[ic] = &_outEvent.electrons;
      break;
    case kMuons:
      col[ic] = &_outEvent.muons;
      break;
    default:
      break;
    }
  }

  if (!col[0] || !col[1] || col[0]->size() == 0 || col[1]->size() == 0)
    return false;

  if (col[0] == col[1]) {
    if (col[0]->size() == 1)
      return false;

    oppSign_ = ((col[0]->at(0).charge == col[0]->at(1).charge) ? 0 : 1);
  }
  else
    oppSign_ = ((col[0]->at(0).charge == col[1]->at(0).charge) ? 0 : 1);

  return oppSign_;
}

//--------------------------------------------------------------------
// BjetVeto
//--------------------------------------------------------------------

void
BjetVeto::addBranches(TTree& _skimTree)
{
  bjets_.book(_skimTree);
}

bool
BjetVeto::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  panda::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.muons,
    &_outEvent.electrons,
    &_outEvent.taus
  };

  bjets_.clear();
  bool hasNonOverlapping(false);
  for (unsigned iB(0); iB != _event.chsAK4Jets.size(); ++iB) {
    auto& jet(_event.chsAK4Jets[iB]);
    if (jet.csv < 0.800 || jet.pt < 20.)
      continue;

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(jet) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was a matching candidate
        overlap = true;
        break;
      }
    }
    
    if (!overlap) { 
      bjets_.push_back(jet);
      hasNonOverlapping = true;
    }
  }

  return !hasNonOverlapping;
}

//--------------------------------------------------------------------
// PhotonMetDPhi
//--------------------------------------------------------------------

void
PhotonMetDPhi::addBranches(TTree& _skimTree)
{
  if (metSource_ == kInMet) {
    _skimTree.Branch("met.realPhotonDPhi", &dPhi_, "realPhotonDPhi/F");
    _skimTree.Branch("met.realPhotonDPhiJECUp", &dPhiJECUp_, "realPhotonDPhiJECUp/F");
    _skimTree.Branch("met.realPhotonDPhiJECDown", &dPhiJECDown_, "realPhotonDPhiJECDown/F");
    _skimTree.Branch("met.realPhotonDPhiGECUp", &dPhiGECUp_, "realPhotonDPhiGECUp/F");
    _skimTree.Branch("met.realPhotonDPhiGECDown", &dPhiGECDown_, "realPhotonDPhiGECDown/F");
    _skimTree.Branch("met.realPhotonDPhiUnclUp", &dPhiUnclUp_, "realPhotonDPhiUnclUp/F");
    _skimTree.Branch("met.realPhotonDPhiUnclDown", &dPhiUnclDown_, "realPhotonDPhiUnclDown/F");
  }
  else {
    _skimTree.Branch("met.photonDPhi", &dPhi_, "photonDPhi/F");
    _skimTree.Branch("met.photonDPhiJECUp", &dPhiJECUp_, "photonDPhiJECUp/F");
    _skimTree.Branch("met.photonDPhiJECDown", &dPhiJECDown_, "photonDPhiJECDown/F");
    _skimTree.Branch("met.photonDPhiGECUp", &dPhiGECUp_, "photonDPhiGECUp/F");
    _skimTree.Branch("met.photonDPhiGECDown", &dPhiGECDown_, "photonDPhiGECDown/F");
    _skimTree.Branch("met.photonDPhiUnclUp", &dPhiUnclUp_, "photonDPhiUnclUp/F");
    _skimTree.Branch("met.photonDPhiUnclDown", &dPhiUnclDown_, "photonDPhiUnclDown/F");
  }
  // _skimTree.Branch("met.photonDPhiJER", &dPhiJER_, "photonDPhiJER/F");
  // _skimTree.Branch("met.photonDPhiJERUp", &dPhiJERUp_, "photonDPhiJERUp/F");
  // _skimTree.Branch("met.photonDPhiJERDown", &dPhiJERDown_, "photonDPhiJERDown/F");
}

bool
PhotonMetDPhi::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  dPhi_ = 0.;
  if (_outEvent.photons.size() != 0) {
    panda::RecoMet const* met(0);
    if (metSource_ == kInMet)
      met = &_event.met;
    else
      met = &_outEvent.met;

    double metPhiGECUp(0.);
    double metPhiGECDown(0.);
    if (metVar_) {
      metPhiGECUp = metVar_->gecUp().Phi();
      metPhiGECDown = metVar_->gecDown().Phi();
    }

    dPhi_ = std::abs(TVector2::Phi_mpi_pi(met->phi - _outEvent.photons[0].phi));

    dPhiJECUp_ = std::abs(TVector2::Phi_mpi_pi(met->phiCorrUp - _outEvent.photons[0].phi));
    dPhiJECDown_ = std::abs(TVector2::Phi_mpi_pi(met->phiCorrDown - _outEvent.photons[0].phi));
    dPhiUnclUp_ = std::abs(TVector2::Phi_mpi_pi(met->phiUnclUp - _outEvent.photons[0].phi));
    dPhiUnclDown_ = std::abs(TVector2::Phi_mpi_pi(met->phiUnclDown - _outEvent.photons[0].phi));

    if (metVar_) {
      dPhiGECUp_ = std::abs(TVector2::Phi_mpi_pi(metPhiGECUp - _outEvent.photons[0].phi));
      dPhiGECDown_ = std::abs(TVector2::Phi_mpi_pi(metPhiGECDown - _outEvent.photons[0].phi));
      // dPhiJER_ = std::abs(TVector2::Phi_mpi_pi(metVar_->jer().Phi() - _outEvent.photons[0].phi));
      // dPhiJERUp_ = std::abs(TVector2::Phi_mpi_pi(metVar_->jerUp().Phi() - _outEvent.photons[0].phi));
      // dPhiJERDown_ = std::abs(TVector2::Phi_mpi_pi(metVar_->jerDown().Phi() - _outEvent.photons[0].phi));      
    }
  }

  if (invert_)
    nominalResult_ = dPhi_ < 2.;
  else
    nominalResult_ = dPhi_ > 2.;

  // for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_, dPhiJER_, dPhiJERUp_, dPhiJERDown_}) {
  for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_}) {
    if (invert_) {
      if (dPhi > 2.)
        return true;
    }
    else {
      if (dPhi < 2.)
        return true;
    }
  }
  return false;
}

//--------------------------------------------------------------------
// JetMetDPhi
//--------------------------------------------------------------------

void
JetMetDPhi::addBranches(TTree& _skimTree)
{
  if (metSource_ == kInMet) {
    _skimTree.Branch("met.realMinJetDPhi", &dPhi_, "realMinJetDPhi/F");
    _skimTree.Branch("met.realMinJetDPhiJECUp", &dPhiJECUp_, "realMinJetDPhiJECUp/F");
    _skimTree.Branch("met.realMinJetDPhiJECDown", &dPhiJECDown_, "realMinJetDPhiJECDown/F");
    _skimTree.Branch("met.realMinJetDPhiGECUp", &dPhiGECUp_, "realMinJetDPhiGECUp/F");
    _skimTree.Branch("met.realMinJetDPhiGECDown", &dPhiGECDown_, "realMinJetDPhiGECDown/F");
    _skimTree.Branch("met.realMinJetDPhiUnclUp", &dPhiUnclUp_, "realMinJetDPhiUnclUp/F");
    _skimTree.Branch("met.realMinJetDPhiUnclDown", &dPhiUnclDown_, "realMinJetDPhiUnclDown/F");
  }
  else {
    _skimTree.Branch("met.minJetDPhi", &dPhi_, "minJetDPhi/F");
    _skimTree.Branch("met.minJetDPhiJECUp", &dPhiJECUp_, "minJetDPhiJECUp/F");
    _skimTree.Branch("met.minJetDPhiJECDown", &dPhiJECDown_, "minJetDPhiJECDown/F");
    _skimTree.Branch("met.minJetDPhiGECUp", &dPhiGECUp_, "minJetDPhiGECUp/F");
    _skimTree.Branch("met.minJetDPhiGECDown", &dPhiGECDown_, "minJetDPhiGECDown/F");
    _skimTree.Branch("met.minJetDPhiUnclUp", &dPhiUnclUp_, "minJetDPhiUnclUp/F");
    _skimTree.Branch("met.minJetDPhiUnclDown", &dPhiUnclDown_, "minJetDPhiUnclDown/F");
  }
  // _skimTree.Branch("met.minJetDPhiJER", &dPhiJER_, "minJetDPhiJER/F");
  // _skimTree.Branch("met.minJetDPhiJERUp", &dPhiJERUp_, "minJetDPhiJERUp/F");
  // _skimTree.Branch("met.minJetDPhiJERDown", &dPhiJERDown_, "minJetDPhiJERDown/F");
}

bool
JetMetDPhi::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  unsigned nJ(0);
  unsigned nJCorrUp(0);
  unsigned nJCorrDown(0);
  // unsigned nJJER(0);
  // unsigned nJJERUp(0);
  // unsigned nJJERDown(0);

  dPhi_ = 4.;
  dPhiJECUp_ = 4.;
  dPhiJECDown_ = 4.;
  dPhiGECUp_ = 4.;
  dPhiGECDown_ = 4.;
  dPhiUnclUp_ = 4.;
  dPhiUnclDown_ = 4.;
  // dPhiJER_ = 4.;
  // dPhiJERUp_ = 4.;
  // dPhiJERDown_ = 4.;

  panda::RecoMet const* met(0);
  if (metSource_ == kInMet)
    met = &_event.met;
  else
    met = &_outEvent.met;

  double metPhiGECUp(0.);
  double metPhiGECDown(0.);
  if (metVar_) {
    metPhiGECUp = metVar_->gecUp().Phi();
    metPhiGECDown = metVar_->gecDown().Phi();
  }

  for (unsigned iJ(0); iJ != _outEvent.chsAK4Jets.size(); ++iJ) {
    auto& jet(_outEvent.chsAK4Jets[iJ]);

    if (jet.pt > 30. && nJ < 4) {
      ++nJ;
      double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - met->phi)));
      if (dPhi < dPhi_)
        dPhi_ = dPhi;

      if (metVar_) {
        dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - metPhiGECUp));
        if (dPhi < dPhiGECUp_)
          dPhiGECUp_ = dPhi;

        dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - metPhiGECDown));
        if (dPhi < dPhiGECDown_)
          dPhiGECDown_ = dPhi;
      }

      dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - met->phiUnclUp));
      if (dPhi < dPhiUnclUp_)
        dPhiUnclUp_ = dPhi;

      dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - met->phiUnclDown));
      if (dPhi < dPhiUnclDown_)
        dPhiUnclDown_ = dPhi;
    }

    if (jet.ptCorrUp > 30. && nJCorrUp < 4) {
      ++nJCorrUp;
      double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - met->phiCorrUp)));
      if (dPhi < dPhiJECUp_)
        dPhiJECUp_ = dPhi;
    }

    if (jet.ptCorrDown > 30. && nJCorrDown < 4) {
      ++nJCorrDown;
      double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - met->phiCorrDown)));
      if (dPhi < dPhiJECDown_)
        dPhiJECDown_ = dPhi;
    }

    // if (metVar_) {
    //   if (jetCleaning_) {
    //     if (jetCleaning_->ptScaled(iJ) > 30. && nJJER < 4) {
    //       ++nJJER;
    //       double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - metVar_->jer().Phi())));
    //       if (dPhi < dPhiJER_)
    //         dPhiJER_ = dPhi;
    //     }
        
    //     if (jetCleaning_->ptScaledUp(iJ) > 30. && nJJERUp < 4) {
    //       ++nJJERUp;
    //       double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - metVar_->jerUp().Phi())));
    //       if (dPhi < dPhiJERUp_)
    //         dPhiJERUp_ = dPhi;
    //     }
        
    //     if (jetCleaning_->ptScaledDown(iJ) > 30. && nJJERDown < 4) {
    //       ++nJJERDown;
    //       double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - metVar_->jerDown().Phi())));
    //       if (dPhi < dPhiJERDown_)
    //         dPhiJERDown_ = dPhi;
    //     }
    //   }
    // }
  }

  if (passIfIsolated_) {
    nominalResult_ = dPhi_ > 0.5;

    //    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_, dPhiJER_, dPhiJERUp_, dPhiJERDown_}) {
    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_}) {
      if (dPhi > 0.5)
        return true;
    }
    return false;
  }
  else {
    nominalResult_ = dPhi_ < 0.5;

    //    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_, dPhiJER_, dPhiJERUp_, dPhiJERDown_}) {
    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_, dPhiUnclUp_, dPhiUnclDown_}) {
      if (dPhi < 0.5)
        return true;
    }
    return false;
  }
}

//--------------------------------------------------------------------
// LeptonSelection
//--------------------------------------------------------------------
void
LeptonSelection::addBranches(TTree& _skimTree)
{
  if ((nMu_ + nEl_) == 2) {
    zs_.book(_skimTree);
    _skimTree.Branch("z.oppSign", &zOppSign_, "z.oppSign/O");
  }
}


bool
LeptonSelection::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  bool foundTight(false);

  std::vector<panda::ParticleCollection*> cols = {
    &_outEvent.photons
  };

  for (unsigned iM(0); iM != _event.muons.size(); ++iM) {
    auto& muon(_event.muons[iM]);

    if (nMu_ != 0 && muon.tight && muon.pt > 30.)
      foundTight = true;
    
    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
	if ((*col)[iP].dR2(muon) < 0.25)
	  break;
      }
      if (iP != col->size()) {
	// there was a matching candidate
	overlap = true;
	break;
      }
    }
    
    if (overlap)
      continue;
    
    if (muon.loose && muon.pt > 10.)
      _outEvent.muons.push_back(muon);
  }

  cols.push_back(&_outEvent.muons);

  for (unsigned iE(0); iE != _event.electrons.size(); ++iE) {
    auto& electron(_event.electrons[iE]);

    if (nEl_ != 0 && electron.tight && electron.pt > 30.)
      foundTight = true;

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
	if ((*col)[iP].dR2(electron) < 0.25)
	  break;
      }
      if (iP != col->size()) {
	// there was a matching candidate
	overlap = true;
	break;
      }
    }
    
    if (overlap)
      continue;
    
    if (electron.loose && electron.pt > 10.)
      _outEvent.electrons.push_back(electron);
  }

  zs_.clear();
  TLorentzVector pair(0., 0., 0., 0.);

  if (nMu_ == 2) {
    // cannot push back here; resize and use the last element
    zs_.resize(zs_.size() + 1);
    auto& z(zs_.back());
    pair = _outEvent.muons[0].p4() + _outEvent.muons[1].p4();
    zOppSign_ = ( (_outEvent.muons[0].charge == _outEvent.muons[1].charge) ? 0 : 1);
    
    z.pt = pair.Pt();
    z.eta = pair.Eta();
    z.phi = pair.Phi();
    z.mass = pair.M();
  }

  else if (nEl_ == 2) {
    // cannot push back here; resize and use the last element
    zs_.resize(zs_.size() + 1);
    auto& z(zs_.back());
    pair = _outEvent.electrons[0].p4() + _outEvent.electrons[1].p4();
    zOppSign_ = ( (_outEvent.electrons[0].charge == _outEvent.electrons[1].charge) ? 0 : 1);
    
    z.pt = pair.Pt();
    z.eta = pair.Eta();
    z.phi = pair.Phi();
    z.mass = pair.M();
  }

  else if (nMu_ == 1 && nEl_ == 1) {
    // cannot push back here; resize and use the last element
    zs_.resize(zs_.size() + 1);
    auto& z(zs_.back());
    pair = _outEvent.muons[0].p4() + _outEvent.electrons[0].p4();
    zOppSign_ = ( (_outEvent.muons[0].charge == _outEvent.electrons[0].charge) ? 0 : 1);
    
    z.pt = pair.Pt();
    z.eta = pair.Eta();
    z.phi = pair.Phi();
    z.mass = pair.M();
  }

  return foundTight && _outEvent.electrons.size() == nEl_ && _outEvent.muons.size() == nMu_;
}

//--------------------------------------------------------------------
// HighMet
//--------------------------------------------------------------------

bool
HighMet::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  if (metSource_ == kInMet)
    return _event.met.pt > min_;
  else
    return _outEvent.met.pt > min_;
}

//--------------------------------------------------------------------
// MtRange
//--------------------------------------------------------------------

bool
MtRange::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  if (!calc_ || _outEvent.photons.size() == 0)
    return false;

  double mt(calc_->getMt(0));

  return mt > min_ && mt < max_;
}

//--------------------------------------------------------------------
// HighPtJetSelection
//--------------------------------------------------------------------

bool
HighPtJetSelection::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  for (unsigned iJ(0); iJ != _event.chsAK4Jets.size(); ++iJ) {
    auto& jet(_event.chsAK4Jets[iJ]);

    if (std::abs(jet.eta) > 5.)
      continue;

    if (jet.pt < min_)
      continue;
    
    return true;
  }

  return false;
}

//--------------------------------------------------------------------
// PhotonPtTruncator
//--------------------------------------------------------------------

bool
PhotonPtTruncator::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& parton(_event.partons[iP]);

    if (parton.pdgid == 22 && parton.pt > max_)
      return false;
  }

  return true;
}

//--------------------------------------------------------------------
// GenParticleSelection
//--------------------------------------------------------------------

bool
GenParticleSelection::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& part(_event.genParticles[iP]);

    // probably need to add a check if it's prompt final state
    /*
    if (part.statusFlags != "someCondition")
      continue;
    */

    if (std::abs(part.pdgid) != pdgId_)
      continue;

    if (std::abs(part.eta) > maxEta_ || std::abs(part.eta) < minEta_ )
      continue;

    if (part.pt < minPt_ || part.pt > maxPt_)
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
EcalCrackVeto::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);

    if (photon.scRawPt < minPt_)
      continue;

    if (std::abs(photon.eta) > 1.4 && std::abs(photon.eta) < 1.6) {
      ecalCrackVeto_ = false;
      return false;
    }
  }
  
  for (unsigned iJ(0); iJ != _event.chsAK4Jets.size(); ++iJ) {
    auto& jet(_event.chsAK4Jets[iJ]);

    if (jet.pt < minPt_)
      continue;

    if (std::abs(jet.eta) > 1.4 && std::abs(jet.eta) < 1.6) {
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
  zs_("z")
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
  case kMuon:
    tags_ = new panda::MuonCollection("tag");
    break;
  case kElectron:
    tags_ = new panda::ElectronCollection("tag");
    break;
  case kPhoton:
    tags_ = new panda::PhotonCollection("tag");
    break;
  }

  switch (probeSpecies_) {
  case kMuon:
    probes_ = new panda::MuonCollection("probe");
    break;
  case kElectron:
    probes_ = new panda::ElectronCollection("probe");
    break;
  case kPhoton:
    probes_ = new panda::PhotonCollection("probe");
    break;
  }

  zs_.book(_skimTree);
  _skimTree.Branch("z.oppSign", &zOppSign_, "z.oppSign/O");

  tags_->book(_skimTree);
  probes_->book(_skimTree);
}

bool
TagAndProbePairZ::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  panda::LeptonCollection const* inTags(0);
  panda::LeptonCollection const* inProbes(0);
  TLorentzVector tnpPair(0., 0., 0., 0.);

  // OK, object-orientation and virtual methods cannot quite solve the problem at hand (push back the objects with full info).
  // We will cheat.
  std::function<void(panda::Particle const&)> push_back_tag;
  std::function<void(panda::Particle const&)> push_back_probe;

  switch (tagSpecies_) {
  case kMuon:
    inTags = &_event.muons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::MuonCollection*>(this->tags_)->push_back(static_cast<panda::Muon const&>(tag));
    };
    break;
  case kElectron:
    inTags = &_event.electrons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::ElectronCollection*>(this->tags_)->push_back(static_cast<panda::Electron const&>(tag));
    };
    break;
  case kPhoton:
    // inTags = &_event.photons;
    push_back_tag = [this](panda::Particle const& tag) {
      static_cast<panda::PhotonCollection*>(this->tags_)->push_back(static_cast<panda::Photon const&>(tag));
    };
    break;
  }
  
  switch (probeSpecies_) {
  case kMuon:
    inProbes = &_event.muons;
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::MuonCollection*>(this->probes_)->push_back(static_cast<panda::Muon const&>(probe));
    };
    break;
  case kElectron:
    inProbes = &_event.electrons;
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::ElectronCollection*>(this->probes_)->push_back(static_cast<panda::Electron const&>(probe));
    };
    break;
  case kPhoton:
    // inProbes = &_event.photons; 
    push_back_probe = [this](panda::Particle const& probe) {
      static_cast<panda::PhotonCollection*>(this->probes_)->push_back(static_cast<panda::Photon const&>(probe));
    };
    break;
  }

  zs_.clear();
  tags_->clear();
  probes_->clear();
  nUniqueZ_ = 0;

  for (unsigned iT(0); iT != inTags->size(); ++iT) {
    auto& tag = inTags->at(iT);
    
    if ( !(tag.tight && tag.pt > 30.))
      continue;
    
    for (unsigned iP(0); iP != inProbes->size(); ++iP) {
      auto& probe = inProbes->at(iP);
      
      if ( !(probe.loose && probe.pt > 20.))
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
      zs_.resize(zs_.size() + 1);
      auto& z(zs_.back());
      z.pt = tnpPair.Pt();
      z.eta = tnpPair.Eta();
      z.phi = tnpPair.Phi();
      z.mass = mass;
      zOppSign_ = ( (tag.charge == probe.charge) ? 0 : 1);

      // check if other tag-probe pairs match this pair
      unsigned iZ(0);
      for (; iZ != zs_.size() - 1; ++iZ) {
        if ((tag.dR2(tags_->at(iZ)) < 0.09 && probe.dR2(probes_->at(iZ)) < 0.09) ||
            (tag.dR2(probes_->at(iZ)) < 0.09 && probe.dR2(tags_->at(iZ)) < 0.09))
          break;
      }
      // if not, increment unique Z counter
      if (iZ == zs_.size() -1)
        ++nUniqueZ_;
    }
  }

  return zs_.size() != 0;
}

//--------------------------------------------------------------------
// ZJetBackToBack
//--------------------------------------------------------------------

bool
ZJetBackToBack::pass(panda::Event const& _event, panda::Event& _outEvent)
{
  if (tnp_->getNUniqueZ() != 1)
    return false;

  for (unsigned iJ(0); iJ != _outEvent.chsAK4Jets.size(); ++iJ) {
    auto& jet( _outEvent.chsAK4Jets[iJ]);

    if ( jet.pt < minJetPt_)
      continue;

    if ( std::abs(TVector2::Phi_mpi_pi(jet.phi - tnp_->getPhiZ(0))) > dPhiMin_ )
      return true;
  }
  return false;
}

//--------------------------------------------------------------------
// TriggerEfficiency
//--------------------------------------------------------------------

void
TriggerEfficiency::setFormula(char const* formula)
{
  delete formula_;
  formula_ = new TF1("TriggerEfficiency", formula, 0., 6500.);
}

void
TriggerEfficiency::setUpFormula(char const* formula)
{
  delete upFormula_;
  upFormula_ = new TF1("TriggerEfficiencyUp", formula, 0., 6500.);
}

void
TriggerEfficiency::setDownFormula(char const* formula)
{
  delete downFormula_;
  downFormula_ = new TF1("TriggerEfficiencyDown", formula, 0., 6500.);
}

void
TriggerEfficiency::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("weight_" + name_, &weight_, "weight_" + name_ + "/D");
  if (upFormula_)
    _skimTree.Branch("reweight_trigUp", &reweightUp_, "reweight_trigUp/D");
  if (downFormula_)
    _skimTree.Branch("reweight_trigDown", &reweightDown_, "reweight_trigDown/D");
}

void
TriggerEfficiency::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  if (!formula_ || _outEvent.photons.size() == 0)
    return;

  double pt(_outEvent.photons[0].scRawPt);
  if (pt < minPt_)
    return;

  _outEvent.weight *= formula_->Eval(pt);
  if (upFormula_)
    reweightUp_ = upFormula_->Eval(pt);
  if (downFormula_)
    reweightDown_ = downFormula_->Eval(pt);
}

//--------------------------------------------------------------------
// ExtraPhotons
//--------------------------------------------------------------------

void
ExtraPhotons::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  panda::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.electrons,
    &_outEvent.muons,
    &_outEvent.taus
    // &_outEvent.chsAK4Jets
  };

  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);

    if (photon.isEB)
      continue;
    
    if (photon.scRawPt < minPt_)
      continue;

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(photon) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was a matching candidate
        overlap = true;
        break;
      }
    }
    if (overlap)
      continue;

    _outEvent.photons.push_back(photon);
  }
}

//--------------------------------------------------------------------
// JetCleaning
//--------------------------------------------------------------------

JetCleaning::JetCleaning(char const* _name/* = "JetCleaning"*/) :
  Modifier(_name)
{
  cleanAgainst_.set();
}

void
JetCleaning::addBranches(TTree& _skimTree)
{
  // _skimTree.Branch("chsAK4Jets.ptResScaled", ptScaled_, "ptResScaled[chsAK4Jets.size]/F");
  // _skimTree.Branch("chsAK4Jets.ptResScaledUp", ptScaledUp_, "ptResScaledUp[chsAK4Jets.size]/F");
  // _skimTree.Branch("chsAK4Jets.ptResScaledDown", ptScaledDown_, "ptResScaledDown[chsAK4Jets.size]/F");
}

// void
// JetCleaning::setJetResolution(char const* _jerSource)
// {
//   jer_ = new JER(_jerSource);
//   rndm_ = new TRandom3(1234);
// }

void
JetCleaning::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  panda::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.electrons,
    &_outEvent.muons,
    &_outEvent.taus
  };

  auto& genJets(_event.genJets);

  for (unsigned iJ(0); iJ != _event.chsAK4Jets.size(); ++iJ) {
    auto& jet(_event.chsAK4Jets[iJ]);

    // printf("jet %u \n", iJ);

    if (std::abs(jet.eta) > 5.)
      continue;

    // printf(" pass eta cut \n");

    // No JEC info stored in nero right now (at least samples I am using)
    // double maxPt(jet.ptCorrUp);
    double maxPt(jet.pt);

    // if (jer_) {
    //   double res(jer_->resolution(jet.pt, jet.eta, _event.rho));
    //   double sf, dsf;
    //   jer_->scalefactor(jet.eta, sf, dsf);

    //   unsigned iG(0);
    //   for (; iG != genJets.size(); ++iG) {
    //     // matching definition from JetResolution twiki
    //     if (genJets[iG].dR2(jet) < 0.04 && std::abs(genJets[iG].pt - jet.pt) < 3. * res)
    //       break;
    //   }

    //   unsigned iOJ(_outEvent.chsAK4Jets.size());

    //   if (iG != genJets.size()) {
    //     auto& genJet(genJets[iG]);
    //     double dpt(jet.pt - genJet.pt);

    //     ptScaled_[iOJ] = std::max(0., genJet.pt + dpt * sf);
    //     ptScaledUp_[iOJ] = std::max(0., genJet.pt + dpt * (sf + dsf));
    //     ptScaledDown_[iOJ] = std::max(0., genJet.pt + dpt * (sf - dsf));
    //   }
    //   else {
    //     ptScaled_[iOJ] = std::max(0., rndm_->Gaus(jet.pt, std::sqrt(sf * sf - 1.) * res));
    //     ptScaledUp_[iOJ] = std::max(0., rndm_->Gaus(jet.pt, std::sqrt((sf + dsf) * (sf + dsf) - 1.) * res));
    //     ptScaledDown_[iOJ] = std::max(0., rndm_->Gaus(jet.pt, std::sqrt((sf - dsf) * (sf - dsf) - 1.) * res));
    //   }

    //   if (ptScaled_[iOJ] > maxPt)
    //     maxPt = ptScaled_[iOJ];
    //   if (ptScaledUp_[iOJ] > maxPt)
    //     maxPt = ptScaledUp_[iOJ];
    //   if (ptScaledDown_[iOJ] > maxPt)
    //     maxPt = ptScaledDown_[iOJ];
    // }

    if (maxPt < 30.)
      continue;

    // printf(" pass pt selection \n");
   
    unsigned iC(0);
    for (; iC != nCollections; ++iC) {
      if (!cleanAgainst_[iC])
        continue;

      auto& col(*cols[iC]);

      unsigned iP(0);
      for (; iP != col.size(); ++iP) {
        if (jet.dR2(col[iP]) < 0.16)
          break;
      }
      if (iP != col.size())
        break;
    }
    if (iC != nCollections)
      continue;

    // printf(" pass cleaning \n");

    _outEvent.chsAK4Jets.push_back(jet);
    
    // printf(" added \n");
  }
}

//--------------------------------------------------------------------
// PhotonJetDPhi
//--------------------------------------------------------------------

void
PhotonJetDPhi::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("photons.minJetDPhi", minDPhi_, "minJetDPhi[photons.size]/F");
  _skimTree.Branch("photons.minJetDPhiJECUp", minDPhiJECUp_, "minJetDPhiJECUp[photons.size]/F");
  _skimTree.Branch("photons.minJetDPhiJECDown", minDPhiJECDown_, "minJetDPhiJECDown[photons.size]/F");
  _skimTree.Branch("chsAK4Jets.photonDPhi", dPhi_, "photonDPhi[chsAK4Jets.size]/F");
}

void
PhotonJetDPhi::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  unsigned nJ(0);
  unsigned nJCorrUp(0);
  unsigned nJCorrDown(0);

  for (unsigned iP(0); iP != _outEvent.photons.size(); ++iP) {
    auto& photon(_outEvent.photons[iP]);
    
    if ( !(photon.isEB) )
      continue;

    minDPhi_[iP] = 4.;
    minDPhiJECUp_[iP] = 4.;
    minDPhiJECDown_[iP] = 4.;
    
    for (unsigned iJ(0); iJ != _outEvent.chsAK4Jets.size(); ++iJ) {
      auto& jet(_outEvent.chsAK4Jets[iJ]);

      double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - photon.phi)));

      if (iP == 0)
	dPhi_[iJ] = dPhi;
      
      if (jet.pt > 30. && nJ < 4) {
	++nJ;
	
	if (dPhi < minDPhi_[iP])
	  minDPhi_[iP] = dPhi;
      }

      if (metVar_) {
	if (jet.ptCorrUp > 30. && nJCorrUp < 4) {
	  ++nJCorrUp;
	  if (dPhi < minDPhiJECUp_[iP])
	    minDPhiJECUp_[iP] = dPhi;
	}

	if (jet.ptCorrDown > 30. && nJCorrDown < 4) {
	  ++nJCorrDown;
	  if (dPhi < minDPhiJECDown_[iP])
	    minDPhiJECDown_[iP] = dPhi;
	}
      }
    }
  }
}

//--------------------------------------------------------------------
// PhotonMt
//--------------------------------------------------------------------

void
PhotonMt::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("photons.mt", mt_, "mt[photons.size]/F");
}

void
PhotonMt::apply(panda::Event const&, panda::Event& _outEvent)
{
  auto& met(_outEvent.met);
  for (unsigned iP(0); iP != _outEvent.photons.size(); ++iP) {
    auto& photon(_outEvent.photons[iP]);
    mt_[iP] = std::sqrt(2. * met.pt * photon.scRawPt * (1. - std::cos(met.phi - photon.phi)));
  }
}

//--------------------------------------------------------------------
// LeptonRecoil
//--------------------------------------------------------------------

void
LeptonRecoil::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("met.realMet", &realMet_, "realMet/F");
  _skimTree.Branch("met.realPhi", &realPhi_, "realPhi/F");
}

void
LeptonRecoil::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  panda::LeptonCollection* col(0);

  switch (flavor_) {
  case kElectron:
    col = &_outEvent.electrons;
    break;
  case kMuon:
    col = &_outEvent.muons;
    break;
  default:
    return;
  }

  float inMets[] = {
    _event.met.pt,
    _event.met.ptCorrUp,
    _event.met.ptCorrDown,
    _event.met.ptUnclUp,
    _event.met.ptUnclDown
  };
  float inPhis[] = {
    _event.met.phi,
    _event.met.phiCorrUp,
    _event.met.phiCorrDown,
    _event.met.phiUnclUp,
    _event.met.phiUnclDown
  };

  float* outRecoils[] = {
    &_outEvent.met.pt,
    &_outEvent.met.ptCorrUp,
    &_outEvent.met.ptCorrDown,
    &_outEvent.met.ptUnclUp,
    &_outEvent.met.ptUnclDown
  };
  float* outRecoilPhis[] = {
    &_outEvent.met.phi,
    &_outEvent.met.phiCorrUp,
    &_outEvent.met.phiCorrDown,
    &_outEvent.met.phiUnclUp,
    &_outEvent.met.phiUnclDown
  };

  float* realMets[] = {
    &realMet_,
    &realMetCorrUp_,
    &realMetCorrDown_,
    &realMetUnclUp_,
    &realMetUnclDown_
  };
  float* realPhis[] = {
    &realPhi_,
    &realPhiCorrUp_,
    &realPhiCorrDown_,
    &realPhiUnclUp_,
    &realPhiUnclDown_
  };

  for (unsigned iM(0); iM != sizeof(realMets) / sizeof(float*); ++iM) {
    *realMets[iM] = inMets[iM];
    *realPhis[iM] = inPhis[iM];
  }

  double lpx(0.);
  double lpy(0.);
    
  for (unsigned iL(0); iL != col->size(); ++iL) {
    auto& lep = col->at(iL);

    lpx += lep.pt * std::cos(lep.phi);
    lpy += lep.pt * std::sin(lep.phi);
  }

  for (unsigned iM(0); iM != sizeof(realMets) / sizeof(float*); ++iM) {
    double mex(lpx + inMets[iM] * std::cos(inPhis[iM]));
    double mey(lpy + inMets[iM] * std::sin(inPhis[iM]));
    *outRecoils[iM] = std::sqrt(mex * mex + mey * mey);
    *outRecoilPhis[iM] = std::atan2(mey, mex);
  }
  
}

TVector2
LeptonRecoil::realMetCorr(int corr) const
{
  if (corr == 0)
    return realMet();

  TVector2 vec;
  switch (corr) {
  case 1:
    vec.SetMagPhi(realMetCorrUp_, realPhiCorrUp_);
    break;
  case -1:
    vec.SetMagPhi(realMetCorrDown_, realPhiCorrDown_);
    break;
  };

  return vec;
}

TVector2
LeptonRecoil::realMetUncl(int corr) const
{
  if (corr == 0)
    return realMet();

  TVector2 vec;
  switch (corr) {
  case 1:
    vec.SetMagPhi(realMetUnclUp_, realPhiUnclUp_);
    break;
  case -1:
    vec.SetMagPhi(realMetUnclDown_, realPhiUnclDown_);
    break;
  };

  return vec;
}

//--------------------------------------------------------------------
// MetVariations
//--------------------------------------------------------------------

void
MetVariations::addBranches(TTree& _skimTree)
{
  if (photonSel_) {
    if (metSource_ == kInMet) {
      _skimTree.Branch("met.realMetGECUp", &metGECUp_, "realMetGECUp/F");
      _skimTree.Branch("met.realPhiGECUp", &phiGECUp_, "realPhiGECUp/F");
      _skimTree.Branch("met.realMetGECDown", &metGECDown_, "realMetGECDown/F");
      _skimTree.Branch("met.realPhiGECDown", &phiGECDown_, "realPhiGECDown/F");
    }
    else {
      _skimTree.Branch("met.ptGECUp", &metGECUp_, "metGECUp/F");
      _skimTree.Branch("met.phiGECUp", &phiGECUp_, "phiGECUp/F");
      _skimTree.Branch("met.ptGECDown", &metGECDown_, "metGECDown/F");
      _skimTree.Branch("met.phiGECDown", &phiGECDown_, "phiGECDown/F");
    }
  }
  // if (jetCleaning_) {
  //   _skimTree.Branch("met.ptJER", &metJER_, "metJER/F");
  //   _skimTree.Branch("met.phiJER", &phiJER_, "phiJER/F");
  //   _skimTree.Branch("met.ptJERUp", &metJERUp_, "metJERUp/F");
  //   _skimTree.Branch("met.phiJERUp", &phiJERUp_, "phiJERUp/F");
  //   _skimTree.Branch("met.ptJERDown", &metJERDown_, "metJERDown/F");
  //   _skimTree.Branch("met.phiJERDown", &phiJERDown_, "phiJERDown/F");
  // }
}

void
MetVariations::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  metGECUp_ = 0.;
  phiGECUp_ = 0.;
  metGECDown_ = 0.;
  phiGECDown_ = 0.;
  // metJER_ = 0.;
  // phiJER_ = 0.;
  // metJERUp_ = 0.;
  // phiJERUp_ = 0.;
  // metJERDown_ = 0.;
  // phiJERDown_ = 0.;

  if (_outEvent.photons.size() == 0)
    return;

  TVector2 metV;
  if (metSource_ == kInMet)
    metV = _event.met.v();
  else
    metV = _outEvent.met.v();

  if (photonSel_) {
    auto& photon(_outEvent.photons[0]);

    TVector2 nominal;
    nominal.SetMagPhi(photon.scRawPt, photon.phi);

    TVector2 photonUp;
    photonUp.SetMagPhi(photonSel_->ptVariation(photon, true), photon.phi);

    TVector2 photonDown;
    photonDown.SetMagPhi(photonSel_->ptVariation(photon, false), photon.phi);

    TVector2 shiftUp(metV + nominal - photonUp);
    TVector2 shiftDown(metV + nominal - photonDown);

    metGECUp_ = shiftUp.Mod();
    phiGECUp_ = TVector2::Phi_mpi_pi(shiftUp.Phi());
    metGECDown_ = shiftDown.Mod();
    phiGECDown_ = TVector2::Phi_mpi_pi(shiftDown.Phi());
  }

  // if (jetCleaning_) {
  //   TVector2 shiftCentral(metV);
  //   TVector2 shiftUp(metV);
  //   TVector2 shiftDown(metV);

  //   for (unsigned iJ(0); iJ != _outEvent.chsAK4Jets.size(); ++iJ) {
  //     auto& jet(_outEvent.chsAK4Jets[iJ]);

  //     TVector2 nominal;
  //     nominal.SetMagPhi(jet.pt, jet.phi);

  //     if (jetCleaning_->ptScaled(iJ) > 15.) {
  //       TVector2 resShift;
  //       resShift.SetMagPhi(jetCleaning_->ptScaled(iJ), jet.phi);
  //       shiftCentral += nominal - resShift;
  //     }

  //     if (jetCleaning_->ptScaledUp(iJ) > 15.) {
  //       TVector2 resShift;
  //       resShift.SetMagPhi(jetCleaning_->ptScaledUp(iJ), jet.phi);
  //       shiftUp += nominal - resShift;
  //     }

  //     if (jetCleaning_->ptScaledDown(iJ) > 15.) {
  //       TVector2 resShift;
  //       resShift.SetMagPhi(jetCleaning_->ptScaledDown(iJ), jet.phi);
  //       shiftDown += nominal - resShift;
  //     }
  //   }

  //   metJER_ = shiftCentral.Mod();
  //   phiJER_ = TVector2::Phi_mpi_pi(shiftCentral.Phi());
  //   metJERUp_ = shiftUp.Mod();
  //   phiJERUp_ = TVector2::Phi_mpi_pi(shiftUp.Phi());
  //   metJERDown_ = shiftDown.Mod();
  //   phiJERDown_ = TVector2::Phi_mpi_pi(shiftDown.Phi());
  // }
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
// PtWeight
//--------------------------------------------------------------------

PhotonPtWeight::PhotonPtWeight(TObject* _factors, char const* _name/* = "PhotonPtWeight"*/) :
  Modifier(_name),
  nominal_(0)
{
  nominal_ = _factors->Clone(name_ + "_" + _factors->GetName());
  if (nominal_->InheritsFrom(TH1::Class()))
    static_cast<TH1*>(nominal_)->SetDirectory(0);
}

PhotonPtWeight::~PhotonPtWeight()
{
  for (auto& var : variations_)
    delete var.second;

  for (auto& var : varWeights_)
    delete var.second;
}

void
PhotonPtWeight::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("weight_" + name_, &weight_, "weight_" + name_ + "/D");
  for (auto& var : varWeights_)
    _skimTree.Branch("reweight_" + var.first, var.second, "reweight_" + var.first + "/D");
}

void
PhotonPtWeight::addVariation(char const* _suffix, TObject* _corr)
{
  auto* clone(_corr->Clone(name_ + "_" + _corr->GetName()));
  if (clone->InheritsFrom(TH1::Class()))
    static_cast<TH1*>(clone)->SetDirectory(0);
  variations_[_suffix] = clone;
  varWeights_[_suffix] = new double;
}

void
PhotonPtWeight::useErrors(bool _b)
{
  useErrors_ = _b;
  varWeights_[name_ + "Up"] = new double;
  varWeights_[name_ + "Down"] = new double;
}

void
PhotonPtWeight::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  double maxPt(0.);
  switch (photonType_) {
  case kReco:
    for (unsigned iP(0); iP != _outEvent.photons.size(); ++iP) {
      auto& photon( _outEvent.photons[iP]);

      if (photon.scRawPt > maxPt)
        maxPt = photon.scRawPt;
    }
    break;
  case kParton:
    for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
      auto& part( _event.partons[iP]);
      
      if (part.pdgid == 22 && part.pt > maxPt)
        maxPt = part.pt;
    }
    break;
  case kPostShower:
    for (unsigned iP(0); iP != _event.genParticles.size(); ++iP) {
      auto& fs( _event.genParticles[iP]);
      // probably need to add a check if it's prompt final state
      /*
	if (part.statusFlags != "someCondition")
	continue;
      */
      
      if (fs.pdgid == 22 && fs.pt > maxPt)
        maxPt = fs.pt;
    }
    break;
  default:
    return;
  }

  auto calcWeight([maxPt](TObject* source, int var = 0)->double {
      if (source->InheritsFrom(TH1::Class())) {
        TH1* hist(static_cast<TH1*>(source));

        int iX(hist->FindFixBin(maxPt));
        if (iX == 0)
          iX = 1;
        if (iX > hist->GetNbinsX())
          iX = hist->GetNbinsX();

        if (var == 0)
          return hist->GetBinContent(iX);
        else if (var == 1)
          return hist->GetBinContent(iX) + hist->GetBinError(iX);
        else
          return hist->GetBinContent(iX) - hist->GetBinError(iX);
      }
      else if (source->InheritsFrom(TF1::Class())) {
        TF1* func(static_cast<TF1*>(source));

        double x(maxPt);
        if (x < func->GetXmin())
          x = func->GetXmin();
        if (x > func->GetXmax())
          x = func->GetXmax();

        return func->Eval(x);
      }
      else
        return 0.;
    });

  double weight(calcWeight(nominal_));
  weight_ = weight;
  _outEvent.weight *= weight;

  for (auto& var : varWeights_) {
    if (var.first == name_ + "Up")
      *var.second = calcWeight(nominal_, 1) / weight;
    else if (var.first == name_ + "Down")
      *var.second = calcWeight(nominal_, -1) / weight;
    else
      *var.second = calcWeight(variations_[var.first]) / weight;
  }
}

//--------------------------------------------------------------------
// IDSFWeight
//--------------------------------------------------------------------

void
IDSFWeight::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("weight_" + name_, &weight_, "weight_" + name_ + "/D");
  _skimTree.Branch("reweight_" + name_ + "Up", &weightUp_, "reweight_" + name_ + "Up/D");
  _skimTree.Branch("reweight_" + name_ + "Down", &weightDown_, "reweight_" + name_ + "Down/D");
}

void
IDSFWeight::setVariable(Variable vx, Variable vy)
{
  variables_[0] = vx;
  variables_[1] = vy;
}

void
IDSFWeight::applyParticle(unsigned iP, panda::Event const& _event, panda::Event& _outEvent)
{
  // simply consider the leading object. Ignores inefficiency scales etc.
  panda::Particle const* part(0);

  switch (object_) {
  case kPhoton:
    if (_outEvent.photons.size() > iP)
      part = &_outEvent.photons.at(iP);
    break;
  case kElectron:
    if (_outEvent.electrons.size() > iP)
      part = &_outEvent.electrons.at(iP);
    break;
  case kMuon:
    if (_outEvent.muons.size() > iP)
      part = &_outEvent.muons.at(iP);
    break;
  default:
    return;
  };

  if (!part)
    return;

  int iCell(0);

  TAxis* axis(0);
  int rowSize(1);
  for (unsigned iV(0); iV != 2; ++iV) {
    if (variables_[iV] == nVariables)
      break;

    switch (iV) {
    case 0:
      axis = factors_[iP]->GetXaxis();
      break;
    case 1:
      axis = factors_[iP]->GetYaxis();
      break;
    };

    int iBin(0);
    switch (variables_[iV]) {
    case kPt:
      iBin = axis->FindFixBin(part->pt);
      break;
    case kEta:
      iBin = axis->FindFixBin(part->eta);
      break;
    case kAbsEta:
      iBin = axis->FindFixBin(std::abs(part->eta));
      break;
    case kNpv:
      iBin = axis->FindFixBin(_event.npvTrue);
      if (iBin == 0)
	iBin = 1;
      if (iBin > axis->GetNbins())
	iBin = axis->GetNbins();
    default:
      break;
    }

    if (iBin == 0)
      iBin = 1;
    if (iBin > axis->GetNbins())
      iBin = axis->GetNbins();

    iCell += iBin * rowSize;

    rowSize *= axis->GetNbins() + 2;
  }

  double weight(factors_[iP]->GetBinContent(iCell));
  double error(factors_[iP]->GetBinError(iCell));

  weight_ *= weight;
  _outEvent.weight *= weight;

  double relerror = error / weight;

  /* 
  if (relerror > 0.5) {
    printf("relerror %6.4f, weight %6.4f, error %6.4f \n", relerror, weight, error);
    printf("hist: %s, bin %d \n", factors_[iP]->GetDirectory()->GetName(), iCell);
  }
  */

  weightUp_ += relerror;
  weightDown_ -= relerror;
}

void
IDSFWeight::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  // not exactly sure why I need to reset these, but it's definitely necessary to get reasonable results
  weight_ = 1.;
  weightUp_ = 1.;
  weightDown_ = 1.;
    
  for (unsigned iP(0); iP != nParticles_; iP++) {
    applyParticle(iP, _event, _outEvent);
  }
}

//--------------------------------------------------------------------
// NPVWeight
//--------------------------------------------------------------------

void
NPVWeight::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npv));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  _outEvent.weight *= factors_->GetBinContent(iX);
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
PUWeight::apply(panda::Event const& _event, panda::Event& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npvTrue));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  weight_ = factors_->GetBinContent(iX);
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
NNPDFVariation::apply(panda::Event const& _event, panda::Event&)
{
  weightUp_ = 1. + _event.genReweight.pdfDW;
  weightDown_ = 1. - _event.genReweight.pdfDW;
}

//--------------------------------------------------------------------
// GenPhotonDR
//--------------------------------------------------------------------

void
GenPhotonDR::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("genPhotonDR", &minDR_, "genPhotonDR/F");
}

void
GenPhotonDR::apply(panda::Event const& _event, panda::Event&)
{
  minDR_ = -1.;

  for (unsigned iP(0); iP != _event.partons.size(); ++iP) {
    auto& parton( _event.partons[iP]);
    
    if (std::abs(parton.pdgid) != 22)
      continue;

    for (unsigned iP2(0); iP2 != _event.partons.size(); ++iP2) {
      auto& p( _event.partons[iP2]);
      
      if (&p == &parton)
        continue;

      double dR(parton.dR(p));
      if (minDR_ < 0. || dR < minDR_)
        minDR_ = dR;
    }
  }
}
