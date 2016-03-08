#include "operators.h"

#include "TH1.h"
#include "TF1.h"

//--------------------------------------------------------------------
// Base
//--------------------------------------------------------------------

bool
Cut::exec(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
Modifier::exec(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  apply(_event, _outEvent);
  return true;
}

//--------------------------------------------------------------------
// MetFilters
//--------------------------------------------------------------------

bool
MetFilters::pass(simpletree::Event const& _event, simpletree::Event&)
{
  bool fired[] = {
    _event.metFilters.cschalo,
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
  cutres[NoisyRegion] = !(_photon.eta > 0. && _photon.eta < 0.15 && _photon.phi > 0.527580 && _photon.phi < 0.541795);
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
  _skimTree.Branch("t1Met.photonDPhiJECUp", &dPhiJECUp_, "photonDPhiJECUp/F");
  _skimTree.Branch("t1Met.photonDPhiJECDown", &dPhiJECDown_, "photonDPhiJECDown/F");
  _skimTree.Branch("t1Met.photonDPhiGECUp", &dPhiGECUp_, "photonDPhiGECUp/F");
  _skimTree.Branch("t1Met.photonDPhiGECDown", &dPhiGECDown_, "photonDPhiGECDown/F");
}

bool
PhotonMetDPhi::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  dPhi_ = 0.;
  if (_outEvent.photons.size() != 0) {
    dPhi_ = std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phi - _outEvent.photons[0].phi));

    if (metVar_) {
      dPhiJECUp_ = std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phiCorrUp - _outEvent.photons[0].phi));
      dPhiJECDown_ = std::abs(TVector2::Phi_mpi_pi(_outEvent.t1Met.phiCorrDown - _outEvent.photons[0].phi));
      dPhiGECUp_ = std::abs(TVector2::Phi_mpi_pi(metVar_->gecUp().Phi() - _outEvent.photons[0].phi));
      dPhiGECDown_ = std::abs(TVector2::Phi_mpi_pi(metVar_->gecDown().Phi() - _outEvent.photons[0].phi));
    }
  }

  for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_}) {
    if (dPhi > 2.)
      return true;
  }
  return false;
}

//--------------------------------------------------------------------
// JetMetDPhi
//--------------------------------------------------------------------

void
JetMetDPhi::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("t1Met.minJetDPhi", &dPhi_, "minJetDPhi/F");
  _skimTree.Branch("t1Met.minJetDPhiJECUp", &dPhiJECUp_, "minJetDPhiJECUp/F");
  _skimTree.Branch("t1Met.minJetDPhiJECDown", &dPhiJECDown_, "minJetDPhiJECDown/F");
  _skimTree.Branch("t1Met.minJetDPhiGECUp", &dPhiGECUp_, "minJetDPhiGECUp/F");
  _skimTree.Branch("t1Met.minJetDPhiGECDown", &dPhiGECDown_, "minJetDPhiGECDown/F");
}

bool
JetMetDPhi::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  unsigned nJ(0);
  unsigned nJCorrUp(0);
  unsigned nJCorrDown(0);

  dPhi_ = 4.;
  dPhiJECUp_ = 4.;
  dPhiJECDown_ = 4.;
  dPhiGECUp_ = 4.;
  dPhiGECDown_ = 4.;

  for (unsigned iJ(0); iJ != _outEvent.jets.size(); ++iJ) {
    auto& jet(_outEvent.jets[iJ]);

    if (jet.pt > 30. && nJ < 4) {
      ++nJ;
      double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phi)));
      if (dPhi < dPhi_)
        dPhi_ = dPhi;

      if (metVar_) {
        dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - metVar_->gecUp().Phi()));
        if (dPhi < dPhiGECUp_)
          dPhiGECUp_ = dPhi;

        dPhi = std::abs(TVector2::Phi_mpi_pi(jet.phi - metVar_->gecDown().Phi()));
        if (dPhi < dPhiGECDown_)
          dPhiGECDown_ = dPhi;
      }
    }

    if (metVar_) {
      if (jet.ptCorrUp > 30. && nJCorrUp < 4) {
        ++nJCorrUp;
        double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phiCorrUp)));
        if (dPhi < dPhiJECUp_)
          dPhiJECUp_ = dPhi;
      }

      if (jet.ptCorrDown > 30. && nJCorrDown < 4) {
        ++nJCorrDown;
        double dPhi(std::abs(TVector2::Phi_mpi_pi(jet.phi - _outEvent.t1Met.phiCorrDown)));
        if (dPhi < dPhiJECDown_)
          dPhiJECDown_ = dPhi;
      }
    }
  }

  if (passIfIsolated_) {
    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_}) {
      if (dPhi > 0.5)
        return true;
    }
    return false;
  }
  else {
    for (double dPhi : {dPhi_, dPhiJECUp_, dPhiJECDown_, dPhiGECUp_, dPhiGECDown_}) {
      if (dPhi < 0.5)
        return true;
    }
    return false;
  }
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
// LeptonRecoil
//--------------------------------------------------------------------

void
LeptonRecoil::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("t1Met.recoil", &recoil_, "recoil/F");
  _skimTree.Branch("t1Met.recoilPhi", &recoilPhi_, "recoilPhi/F");
}

bool
LeptonRecoil::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  simpletree::LeptonCollection* col(0);

  switch (collection_) {
  case kElectrons:
    col = &_outEvent.electrons;
    break;
  case kMuons:
    col = &_outEvent.muons;
    break;
  default:
    return false;
  }

  double mex(_event.t1Met.met * std::cos(_event.t1Met.phi));
  double mey(_event.t1Met.met * std::sin(_event.t1Met.phi));
    
  for (auto& lep : *col) {
    mex += lep.pt * std::cos(lep.phi);
    mey += lep.pt * std::sin(lep.phi);
  }

  recoil_ = std::sqrt(mex * mex + mey * mey);
  recoilPhi_ = std::atan2(mey, mex);

  return recoil_ > min_;
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
// HighPtJetSelection
//--------------------------------------------------------------------

bool
HighPtJetSelection::pass(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  for (auto& jet : _outEvent.jets) {
    if (std::abs(jet.eta) > 5.)
      continue;

    if (jet.pt < min_)
      continue;
    
    return true;
  }

  return false;
}

//--------------------------------------------------------------------
// MetVariations
//--------------------------------------------------------------------

void
MetVariations::addBranches(TTree& _skimTree)
{
  if (photonSel_) {
    _skimTree.Branch("t1Met.metGECUp", &metGECUp_, "metGECUp/F");
    _skimTree.Branch("t1Met.phiGECUp", &phiGECUp_, "phiGECUp/F");
    _skimTree.Branch("t1Met.metGECDown", &metGECDown_, "metGECDown/F");
    _skimTree.Branch("t1Met.phiGECDown", &phiGECDown_, "phiGECDown/F");
  }
}

void
MetVariations::apply(simpletree::Event const&, simpletree::Event& _outEvent)
{
  metGECUp_ = 0.;
  phiGECUp_ = 0.;
  metGECDown_ = 0.;
  phiGECDown_ = 0.;

  if (_outEvent.photons.size() == 0)
    return;

  if (photonSel_) {
    TVector2 metV(_outEvent.t1Met.v());
    
    auto& photon(_outEvent.photons[0]);

    TVector2 nominal;
    nominal.SetMagPhi(photon.pt, photon.phi);

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
}

//--------------------------------------------------------------------
// ConstantWeight
//--------------------------------------------------------------------

void
ConstantWeight::addBranches(TTree& _skimTree)
{
  if (weightUncertUp_ != 0.)
    _skimTree.Branch("reweight_" + name_ + "Up", &weightUncertUp_, "reweight_" + name_ + "Up/D");
  if (weightUncertDown_ != 0.)
    _skimTree.Branch("reweight_" + name_ + "Down", &weightUncertDown_, "reweight_" + name_ + "Down/D");
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
PhotonPtWeight::apply(simpletree::Event const& _event, simpletree::Event& _outEvent)
{
  double maxPt(0.);
  switch (photonType_) {
  case kReco:
    for (auto& photon : _outEvent.photons) {
      if (photon.pt > maxPt)
        maxPt = photon.pt;
    }
    break;
  case kParton:
    for (auto& part : _event.partons) {
      if (part.pid == 22 && part.status == 1 && part.pt > maxPt)
        maxPt = part.pt;
    }
    break;
  case kPostShower:
    for (auto& fs : _event.promptFinalStates) {
      if (fs.pid == 22 && fs.pt > maxPt)
        maxPt = fs.pt;
    }
    break;
  default:
    return;
  }

  auto calcWeight([maxPt](TObject* source)->double {
      if (source->InheritsFrom(TH1::Class())) {
        TH1* hist(static_cast<TH1*>(source));

        int iX(hist->FindFixBin(maxPt));
        if (iX == 0)
          iX = 1;
        if (iX > hist->GetNbinsX())
          iX = hist->GetNbinsX();

        return hist->GetBinContent(iX);
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
  _outEvent.weight *= weight;

  for (auto& var : varWeights_)
    *var.second = calcWeight(variations_[var.first]) / weight;
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
