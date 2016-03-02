#include "operators.h"

//--------------------------------------------------------------------
// Base
//--------------------------------------------------------------------

bool
Cut::operator()(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
Modifier::operator()(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  apply(_event, _outEvent);
  return true;
}

//--------------------------------------------------------------------
// PhotonSelection
//--------------------------------------------------------------------

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

double
PhotonSelection::ptVariation(simpletree::Photon const& _photon, bool up)
{
  if (up)
    return _photon.pt * 1.015;
  else
    return _photon.pt * 0.985;
}

bool
PhotonSelection::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  for (unsigned iP(0); iP != _event.photons.size(); ++iP) {
    auto& photon(_event.photons[iP]);

    if (!photon.isEB)
      continue;
    
    if (vetoes_.size() == 0) {
      // veto is not set -> this is a simple photon selection. Pass if upward variation is above the threshold.
      if (ptVariation(photon, true) < minPt_)
        continue;
    }
    else {
      if (photon.pt < minPt_)
        continue;
    }

    int selection(selectPhoton(photon));

    if (selection < 0) {
      // vetoed
      _outEvent.photons.clear();
      break;
    }
    else if (selection > 0)
      _outEvent.photons.push_back(photon);
  }

  return _outEvent.photons.size() != 0;
}

int
PhotonSelection::selectPhoton(simpletree::Photon const& _photon)
{
  BitMask cutres;
  cutres[HOverE] = _photon.passHOverE(wp_);
  cutres[Sieie] = _photon.passSieie(wp_);
  cutres[CHIso] = _photon.passCHIso(wp_);
  cutres[NHIso] = _photon.passNHIso(wp_);
  cutres[PhIso] = _photon.passPhIso(wp_);
  cutres[EVeto] = _photon.pixelVeto;
  cutres[MIP49] = _photon.mipEnergy < 4.9;
  cutres[Time] = std::abs(_photon.time) < 3.;
  cutres[SieieNonzero] = _photon.sieie > 0.001;
  cutres[NoisyRegion] = !(_photon.eta > 0. && _photon.eta < 0.14 && _photon.phi > 0.527580 && _photon.phi < 0.541795);
  cutres[Sieie12] = (_photon.sieie < 0.012);
  cutres[Sieie15] = (_photon.sieie < 0.015);
  cutres[CHIso11] = (_photon.chIso < 11.);
  cutres[NHIso11] = (_photon.nhIso < 11.);
  cutres[PhIso3] = (_photon.phIso < 3.);
  cutres[NHIsoTight] = _photon.passNHIso(2);
  cutres[PhIsoTight] = _photon.passPhIso(2);
  cutres[CHWorstIso] = (_photon.chWorstIso < simpletree::Photon::chIsoCuts[0][wp_]);
  cutres[CHWorstIso11] = (_photon.chWorstIso < 11.);

  // Wisconsin denominator def
  // if (photon.passHOverE(wp_) && photon.pixelVeto && photon.sieie > 0.001 && photon.mipEnergy < 4.9 && std::abs(photon.time) < 3. &&
  //     photon.nhIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::nhIsoCuts[0][0]) &&
  //     photon.phIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::phIsoCuts[0][0]) &&
  //     photon.chIso < std::min(0.2 * photon.pt, 5. * simpletree::Photon::chIsoCuts[0][0])) {
  //   unsigned nPass(0);
  //   if (photon.passCHIso(0))
  //     ++nPass;
  //   if (photon.passNHIso(0))
  //     ++nPass;
  //   if (photon.passPhIso(0))
  //     ++nPass;

  //   if (nPass == 3)
  //     break;

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
ElectronVeto::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  simpletree::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.muons
  };

  unsigned iE(0);
  for (; iE != _event.electrons.size(); ++iE) {
    auto& electron(_event.electrons[iE]);
    if (!electron.loose || electron.pt < 10.)
      continue;

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

    break;
  }

  // no electron matched the veto condition
  return iE == _event.electrons.size();
}

//--------------------------------------------------------------------
// MuonVeto
//--------------------------------------------------------------------

bool
MuonVeto::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  simpletree::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.electrons
  };

  unsigned iM(0);
  for (; iM != _event.muons.size(); ++iM) {
    auto& muon(_event.muons[iM]);
    if (!muon.loose || muon.pt < 10.)
      continue;

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

    break;
  }

  // no muon matched the veto condition
  return iM == _event.muons.size();
}

//--------------------------------------------------------------------
// TauVeto
//--------------------------------------------------------------------

bool
TauVeto::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned iTau(0);
  for (; iTau != _event.taus.size(); ++iTau) {
    auto& tau(_event.taus[iTau]);

    if (!tau.decayMode || tau.combIso > 5.)
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

    break;
  }

  return iTau == _event.taus.size();
}

//--------------------------------------------------------------------
// PhotonMetDPhi
//--------------------------------------------------------------------

void
PhotonMetDPhi::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("t1Met.photonDPhi", &dPhi_, "photonDPhi/F");
}

bool
PhotonMetDPhi::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  dPhi_ = 0.;
  if (_outEvent.photons.size() != 0)
    dPhi_ = std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi));

  return dPhi_ > 2.;
}

//--------------------------------------------------------------------
// JetMetDPhi
//--------------------------------------------------------------------

void
JetMetDPhi::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("t1Met.minJetDPhi", &dPhi_, "minJetDPhi/F");
  _skimTree.Branch("t1Met.minJetDPhiCorrUp", &dPhiCorrUp_, "minJetDPhiCorrUp/F");
  _skimTree.Branch("t1Met.minJetDPhiCorrDown", &dPhiCorrDown_, "minJetDPhiCorrDown/F");
}

bool
JetMetDPhi::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned nJ(0);
  unsigned nJCorrUp(0);
  unsigned nJCorrDown(0);

  dPhi_ = 4.;
  dPhiCorrUp_ = 4.;
  dPhiCorrDown_ = 4.;
  for (unsigned iJ(0); iJ != _outEvent.jets.size(); ++iJ) {
    auto& jet(_outEvent.jets[iJ]);
    double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phi)));
    double dPhiCorrUp(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phiCorrUp)));
    double dPhiCorrDown(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phiCorrDown)));

    if (jet.pt > 30. && nJ < 4) {
      ++nJ;
      if (dPhi < dPhi_)
        dPhi_ = dPhi;
    }
    if (jet.ptCorrUp > 30. && nJCorrUp < 4) {
      ++nJCorrUp;
      if (dPhiCorrUp < dPhiCorrUp_)
        dPhiCorrUp_ = dPhiCorrUp;
    }
    if (jet.ptCorrDown > 30. && nJCorrDown < 4) {
      ++nJCorrDown;
      if (dPhiCorrDown < dPhiCorrDown_)
        dPhiCorrDown_ = dPhiCorrDown;
    }
  }

  if (passIfIsolated_)
    return dPhi_ > 0.5 || dPhiCorrUp_ > 0.5 || dPhiCorrDown_ > 0.5;
  else
    return dPhi_ < 0.5 || dPhiCorrUp_ < 0.5 || dPhiCorrDown_ < 0.5;
}

//--------------------------------------------------------------------
// LeptonSelection
//--------------------------------------------------------------------

bool
LeptonSelection::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  bool foundTight(false);

  for (auto& electron : _event.electrons) {
    if (nEl_ != 0 && electron.tight && electron.pt > 30. && (_event.run == 1 || electron.matchHLT27Loose))
      foundTight = true;
    if (electron.loose && electron.pt > 10.)
      _outEvent.electrons.push_back(electron);
  }

  for (auto& muon : _event.muons) {
    if (nMu_ != 0 && muon.tight && muon.pt > 30. && (_event.run == 1 || muon.matchHLT27))
      foundTight = true;
    if (muon.loose && muon.pt > 10.)
      _outEvent.muons.push_back(muon);
  }

  return foundTight && _outEvent.electrons.size() == nEl_ && _outEvent.muons.size() == nMu_;
}

//--------------------------------------------------------------------
// JetCleaning
//--------------------------------------------------------------------

void
JetCleaning::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  simpletree::ParticleCollection* cols[] = {
    &_outEvent.photons,
    &_outEvent.electrons,
    &_outEvent.muons,
    &_outEvent.taus
  };

  for (auto& jet : _event.jets) {
    if (std::abs(jet.eta) > 5.)
      continue;

    if (jet.ptCorrUp < 30.)
      continue;
   
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

    _outEvent.jets.push_back(jet);
  }
}

//--------------------------------------------------------------------
// LeptonRecoil
//--------------------------------------------------------------------

void
LeptonRecoil::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("t1Met.realMet", &realMet_, "realMet/F");
  _skimTree.Branch("t1Met.realPhi", &realPhi_, "realPhi/F");
}

void
LeptonRecoil::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  realMet_ = _event.t1Met.met;
  realPhi_ = _event.t1Met.phi;

  simpletree::LeptonCollection* col(0);

  switch (collection_) {
  case kElectrons:
    col = &_outEvent.electrons;
    break;
  case kMuons:
    col = &_outEvent.muons;
    break;
  default:
    return;
  }

  double mex(_event.t1Met.met * std::cos(_event.t1Met.phi));
  double mey(_event.t1Met.met * std::sin(_event.t1Met.phi));
    
  for (auto& lep : *col) {
    mex += lep.pt * std::cos(lep.phi);
    mey += lep.pt * std::sin(lep.phi);
  }

  _outEvent.t1Met.met = std::sqrt(mex * mex + mey * mey);
  _outEvent.t1Met.phi = std::atan2(mey, mex);
}

//--------------------------------------------------------------------
// UniformWeight
//--------------------------------------------------------------------

void
UniformWeight::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("delta" + name_, &weightUncert_, "delta" + name_ + "/D");
}

//--------------------------------------------------------------------
// PtWeight
//--------------------------------------------------------------------

void
PtWeight::addBranches(TTree& _skimTree)
{
  if (uncertUp_)
    _skimTree.Branch("delta" + name_ + "Up", &weightUncertUp_, "delta" + name_ + "Up/D");
  if (uncertDown_)
    _skimTree.Branch("delta" + name_ + "Down", &weightUncertDown_, "delta" + name_ + "Down/D");
}

void
PtWeight::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  int iPt(factors_->GetXaxis()->FindFixBin(_outEvent.photons[0].pt));
  if (iPt == 0)
    iPt = 1;
  if (iPt > factors_->GetNbinsX())
    iPt = factors_->GetNbinsX();

  double weight(factors_->GetBinContent(iPt));
  _outEvent.weight *= weight;

  if (uncertUp_)
    weightUncertUp_ = uncertUp_->GetBinContent(iPt) - weight;
  if (uncertDown_)
    weightUncertDown_ = uncertDown_->GetBinContent(iPt) - weight;
}

//--------------------------------------------------------------------
// IDSFWeight
//--------------------------------------------------------------------

void
IDSFWeight::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  // simply consider the leading object. Ignores inefficiency scales etc.
  simpletree::Particle const* part(0);

  switch (object_) {
  case kPhoton:
    if (_outEvent.photons.size() != 0)
      part = &_outEvent.photons.at(0);
    break;
  case kElectron:
    if (_outEvent.electrons.size() != 0)
      part = &_outEvent.electrons.at(0);
    break;
  case kMuon:
    if (_outEvent.muons.size() != 0)
      part = &_outEvent.muons.at(0);
    break;
  default:
    return;
  };

  if (!part)
    return;

  int iPt(factors_->GetXaxis()->FindFixBin(part->pt));
  int iEta(factors_->GetYaxis()->FindFixBin(part->eta));

  if (iPt == 0)
    iPt = 1;
  if (iPt > factors_->GetXaxis()->GetNbins())
    iPt = factors_->GetXaxis()->GetNbins();

  if (iEta == 0)
    iEta = 1;
  if (iEta > factors_->GetYaxis()->GetNbins())
    iEta = factors_->GetYaxis()->GetNbins();

  _outEvent.weight *= factors_->GetBinContent(factors_->GetBin(iPt, iEta));
}

//--------------------------------------------------------------------
// NPVWeight
//--------------------------------------------------------------------

void
NPVWeight::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  int iX(factors_->FindFixBin(_event.npv));
  if (iX == 0)
    iX = 1;
  if (iX > factors_->GetNbinsX())
    iX = factors_->GetNbinsX();

  _outEvent.weight *= factors_->GetBinContent(iX);
}

//--------------------------------------------------------------------
// KFactorCorrection
//--------------------------------------------------------------------

void
KFactorCorrection::setCorrection(TH1* _corr)
{
  kfactors_.clear();

  for (int iX(1); iX <= _corr->GetNbinsX(); ++iX)
    kfactors_.emplace_back(_corr->GetXaxis()->GetBinLowEdge(iX), _corr->GetBinContent(iX));
}

void
KFactorCorrection::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  double maxPt(0.);
  for (auto& fs : _event.promptFinalStates) {
    if (fs.pid != 22)
      continue;

    if (fs.pt > maxPt)
      maxPt = fs.pt;
  }

  if (maxPt > 0.) {
    // what if the gen photon is out of eta acceptance?
    unsigned iBin(0);
    while (iBin != kfactors_.size() && maxPt >= kfactors_[iBin].first)
      ++iBin;

    if (iBin > 0)
      iBin -= 1;

    _outEvent.weight *= kfactors_[iBin].second;
  }
}
