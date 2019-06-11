#include "TPOperators.h"

#include "PandaTree/Objects/interface/EventTPEG.h"
#include "PandaTree/Objects/interface/EventTPEEG.h"
#include "PandaTree/Objects/interface/EventTPMG.h"
#include "PandaTree/Objects/interface/EventTPMMG.h"
#include "PandaTree/Objects/interface/EventTP2E.h"
#include "PandaTree/Objects/interface/EventTP2M.h"
#include "PandaTree/Objects/interface/EventTPEM.h"
#include "PandaTree/Objects/interface/EventTPME.h"

//--------------------------------------------------------------------
// Base
//--------------------------------------------------------------------

panda::ParticleCollection*
TPOperator::getLooseTags(panda::EventTP& _outEvent) const
{
  switch (eventType_) {
  case kTPEEG:
    return &static_cast<panda::EventTPEEG&>(_outEvent).looseTags;
  case kTPMMG:
    return &static_cast<panda::EventTPMMG&>(_outEvent).looseTags;
  default:
    throw std::runtime_error("Incompatible event type in getLooseTag");
  }
}

panda::ParticleCollection*
TPOperator::getTags(panda::EventTP& _outEvent) const
{
  switch (eventType_) {
  case kTPEEG:
  case kTPEG:
    return &static_cast<panda::EventTPEG&>(_outEvent).tags;
  case kTPMMG:
  case kTPMG:
    return &static_cast<panda::EventTPMG&>(_outEvent).tags;
  case kTP2E:
    return &static_cast<panda::EventTP2E&>(_outEvent).tags;
  case kTP2M:
    return &static_cast<panda::EventTP2M&>(_outEvent).tags;
  case kTPEM:
    return &static_cast<panda::EventTPEM&>(_outEvent).tags;
  case kTPME:
    return &static_cast<panda::EventTPME&>(_outEvent).tags;
  default:
    throw std::runtime_error("Incompatible event type in getTag");
  }
}

panda::ParticleCollection*
TPOperator::getProbes(panda::EventTP& _outEvent) const
{
  switch (eventType_) {
  case kTPEEG:
  case kTPEG:
    return &static_cast<panda::EventTPEG&>(_outEvent).probes;
  case kTPMMG:
  case kTPMG:
    return &static_cast<panda::EventTPMG&>(_outEvent).probes;
  case kTP2E:
    return &static_cast<panda::EventTP2E&>(_outEvent).probes;
  case kTP2M:
    return &static_cast<panda::EventTP2M&>(_outEvent).probes;
  case kTPEM:
    return &static_cast<panda::EventTPEM&>(_outEvent).probes;
  case kTPME:
    return &static_cast<panda::EventTPME&>(_outEvent).probes;
  default:
    throw std::runtime_error("Incompatible event type in getProbe");
  }
}

bool
TPCut::tpexec(panda::EventMonophoton const& _event, panda::EventTP& _outEvent)
{
  result_ = pass(_event, _outEvent);
  return ignoreDecision_ || result_;
}

bool
TPModifier::tpexec(panda::EventMonophoton const& _event, panda::EventTP& _outEvent)
{
  apply(_event, _outEvent);
  return true;
}

//--------------------------------------------------------------------
// TPLeptonPhoton
//--------------------------------------------------------------------

void
TPLeptonPhoton::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("probes.chargedPFVeto", chargedPFVeto_, "chargedPFVeto[probes.size]/O");
  _skimTree.Branch("probes.hasCollinearL", hasCollinearL_, "hasCollinearL[probes.size]/O");
  _skimTree.Branch("probes.ptdiff", ptdiff_, "ptdiff[probes.size]/F");
}

void
TPLeptonPhoton::addInputBranch(panda::utils::BranchList& _blist)
{
  _blist += {"pfCandidates"};
}

bool
TPLeptonPhoton::pass(panda::EventMonophoton const& _inEvent, panda::EventTP& _outEvent)
{
  panda::LeptonCollection const* leptons(0);
  double tagMaxEta(0.);
  switch (eventType_) {
  case kTPEG:
  case kTPEEG:
    leptons = &_inEvent.electrons;
    tagMaxEta = 2.5;
    break;
  case kTPMG:
  case kTPMMG:
    leptons = &_inEvent.muons;
    tagMaxEta = 2.1;
    break;
  default:
    throw runtime_error("Incompatible event type in TPLeptonPhoton");
  }

  std::vector<panda::PFCand const*> chargedCands;

  for (auto& cand : _inEvent.pfCandidates) {
    if (cand.q() != 0)
      chargedCands.push_back(&cand);
  }

  for (auto& photon : _inEvent.photons) {
    if (!photon.isEB || photon.scRawPt < minProbePt_)
      continue;

    bool chargedPFMatch(false);

    for (auto* cand : chargedCands) {
      double dr(cand->dR(photon));
      if (dr > chargedPFDR_)
        continue;

      double relPt(cand->pt() / photon.scRawPt);
      if (relPt > chargedPFRelPt_) {
        chargedPFMatch = true;
        break;
      }
    }

    auto&& pg(photon.p4());

    for (auto& lepton : *leptons) {
      if (!lepton.tight)
        continue;

      if (lepton.pt() < minTagPt_ || std::abs(lepton.eta()) > tagMaxEta)
        continue;

      // see discussion on lepton veto below for the choice of the cone size
      if (photon.dR2(lepton) < 0.09)
        continue;

      if (eventType_ == kTPMG || eventType_ == kTPMMG) {
        auto& muon(static_cast<panda::Muon const&>(lepton));
        if (muon.combIso() / muon.pt() > 0.15)
          continue;
      }

      bool hasCollinearL(false);

      if (eventType_ == kTPEEG || eventType_ == kTPMMG) {
        for (auto& looseLepton : *leptons) {
          if (&looseLepton == &lepton)
            continue;

          if (!looseLepton.loose || looseLepton.pt() < 2.)
            continue;

          // we do need to allow loose leptons pretty close to the photon
          // since the bulk of FSR events exist in that phase space
          if (photon.dR2(looseLepton) < 0.01) {
            hasCollinearL = true;
            continue;
          }

          TLorentzVector pll(lepton.p4() + looseLepton.p4());
          double mllg((pg + pll).M());

          if (mllg < 20. || mllg > 160.)
            continue;

          auto& tp(_outEvent.tp.create_back());
          tp.mass = mllg;
          tp.mass2 = pll.M();

          if (eventType_ == kTPEEG) {
            auto& outEvent(static_cast<panda::EventTPEEG&>(_outEvent));
            outEvent.looseTags.push_back(static_cast<panda::Electron const&>(looseLepton));
            outEvent.tags.push_back(static_cast<panda::Electron const&>(lepton));
            outEvent.probes.push_back(photon);
          }
          else {
            auto& outEvent(static_cast<panda::EventTPMMG&>(_outEvent));
            outEvent.looseTags.push_back(static_cast<panda::Muon const&>(looseLepton));
            outEvent.tags.push_back(static_cast<panda::Muon const&>(lepton));
            outEvent.probes.push_back(photon);
          }

          chargedPFVeto_[_outEvent.tp.size() - 1] = !chargedPFMatch;
        }
      }
      else {
	auto&& pl(lepton.p4());
        double mlg((pg + pl).M());
	
	// calculate expected pt using z mass 
	TLorentzVector ug;
	ug.SetPtEtaPhiM(1., photon.eta(), photon.phi(), 0.);
	float ptdiff = (91.2 * 91.2) / (2 * ug.Dot(pl)) - photon.scRawPt;
	
        // if (mlg < 20. || mlg > 160.)
        //   continue;

        // veto additional loose leptons
        unsigned iVeto(0);
        for (; iVeto != leptons->size(); ++iVeto) {
          auto& veto((*leptons)[iVeto]);

          if (&veto == &lepton)
            continue;

          if (eventType_ == kTPEG) {
            if (!static_cast<panda::Electron const&>(veto).veto)
              continue;
          }
          else {
            if (!veto.loose)
              continue;
          }

          if (veto.pt() < 10.)
            continue;

          // Our electron veto does not reject photons overlapping with e/mu
          // Cases:
          // 1. One electron radiates hard, gets deflected by a large angle
          //   -> The radiation is a photon, and the deflected electron is an additional
          //   lepton. Veto the event.
          // 2. One electron radiates hard but stays collinear with the radiation
          //   -> This is an electron faking a photon. The event should be included
          //   in the "eg" sample of the tag & probe fit.
          //
          // Large angle is defined by the isolation cone of the electron, which defines
          // what object can be considered an independent electron.
          if (photon.dR2(veto) < 0.09) {
            hasCollinearL = true;
            continue;
          }

          break;
        }
        if (iVeto != leptons->size())
          continue;

        auto& tp(_outEvent.tp.create_back());
        tp.mass = mlg;

        if (eventType_ == kTPEG) {
          auto& outEvent(static_cast<panda::EventTPEG&>(_outEvent));
          outEvent.tags.push_back(static_cast<panda::Electron const&>(lepton));
          outEvent.probes.push_back(photon);
        }
        else {
          auto& outEvent(static_cast<panda::EventTPMG&>(_outEvent));
          outEvent.tags.push_back(static_cast<panda::Muon const&>(lepton));
          outEvent.probes.push_back(photon);
        }

        chargedPFVeto_[_outEvent.tp.size() - 1] = !chargedPFMatch;
        hasCollinearL_[_outEvent.tp.size() - 1] = hasCollinearL;
	ptdiff_[_outEvent.tp.size() - 1] = ptdiff;
      }
    }
  }
  
  return _outEvent.tp.size() != 0;
}

//--------------------------------------------------------------------
// TPDilepton
//--------------------------------------------------------------------

void
TPDilepton::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("probes.matchedGenId", probeGenId_, "matchedGenId[probes.size]/I");
}

bool
TPDilepton::pass(panda::EventMonophoton const& _inEvent, panda::EventTP& _outEvent)
{
  panda::LeptonCollection const* leptons(0);
  double maxEta(0.);
  switch (eventType_) {
  case kTP2E:
    leptons = &_inEvent.electrons;
    maxEta = 2.5;
    break;
  case kTP2M:
    leptons = &_inEvent.muons;
    maxEta = 2.1;
    break;
  default:
    throw runtime_error("Incompatible event type in TPDilepton");
  }

  for (auto& tag : *leptons) {
    if (!tag.tight || tag.pt() < minTagPt_ || std::abs(tag.eta()) > maxEta)
      continue;

    if (eventType_ == kTP2M && tag.combIso() / tag.pt() > 0.15)
      continue;

    for (auto& probe : *leptons) {
      if (&probe == &tag)
        continue;

      double mll((tag.p4() + probe.p4()).M());

      if (mll < 20. || mll > 160.)
        continue;

      auto& tp(_outEvent.tp.create_back());
      tp.mass = mll;

      if (eventType_ == kTP2E) {
        auto& outEvent(static_cast<panda::EventTP2E&>(_outEvent));
        outEvent.tags.push_back(static_cast<panda::Electron const&>(tag));
        outEvent.probes.push_back(static_cast<panda::Electron const&>(probe));
      }
      else {
        auto& outEvent(static_cast<panda::EventTP2M&>(_outEvent));
        outEvent.tags.push_back(static_cast<panda::Muon const&>(tag));
        outEvent.probes.push_back(static_cast<panda::Muon const&>(probe));
      }

      if(probe.matchedGen.isValid())
        probeGenId_[_outEvent.tp.size() - 1] = probe.matchedGen->pdgid;
      else
        probeGenId_[_outEvent.tp.size() - 1] = 0;
    }
  }
  
  return _outEvent.tp.size() != 0;
}

//--------------------------------------------------------------------
// TPOFLepton
//--------------------------------------------------------------------

void
TPOFLepton::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("probes.matchedGenId", probeGenId_, "matchedGenId[probes.size]/I");
}

bool
TPOFLepton::pass(panda::EventMonophoton const& _inEvent, panda::EventTP& _outEvent)
{
  panda::LeptonCollection const* tags(0);
  panda::LeptonCollection const* probes(0);
  double tagMaxEta(0.);
  double probeMaxEta(0.);
  switch (eventType_) {
  case kTPEM:
    tags = &_inEvent.electrons;
    probes = &_inEvent.muons;
    tagMaxEta = 2.5;
    probeMaxEta = 2.4;
    break;
  case kTPME:
    tags = &_inEvent.muons;
    probes = &_inEvent.electrons;
    tagMaxEta = 2.4;
    probeMaxEta = 2.5;
    break;
  default:
    throw runtime_error("Incompatible event type in TPOFLepton");
  }

  for (auto& tag : *tags) {
    if (!tag.tight || tag.pt() < minTagPt_ || std::abs(tag.eta()) > tagMaxEta)
      continue;

    if (eventType_ == kTPME && tag.combIso() / tag.pt() > 0.15)
      continue;

    for (auto& probe : *probes) {
      double mll((tag.p4() + probe.p4()).M());

      auto& tp(_outEvent.tp.create_back());
      tp.mass = mll;

      if (eventType_ == kTPEM) {
        auto& outEvent(static_cast<panda::EventTPEM&>(_outEvent));
        outEvent.tags.push_back(static_cast<panda::Electron const&>(tag));
        outEvent.probes.push_back(static_cast<panda::Muon const&>(probe));
      }
      else {
        auto& outEvent(static_cast<panda::EventTPME&>(_outEvent));
        outEvent.tags.push_back(static_cast<panda::Muon const&>(tag));
        outEvent.probes.push_back(static_cast<panda::Electron const&>(probe));
      }

      if(probe.matchedGen.isValid())
        probeGenId_[_outEvent.tp.size() - 1] = probe.matchedGen->pdgid;
      else
        probeGenId_[_outEvent.tp.size() - 1] = 0;
    }
  }
  
  return _outEvent.tp.size() != 0;
}

//--------------------------------------------------------------------
// TPLeptonVeto
//--------------------------------------------------------------------

void
TPLeptonVeto::addBranches(TTree& _skimTree)
{
  _skimTree.Branch("electrons.size", &nElectrons_, "size/i");
  _skimTree.Branch("muons.size", &nMuons_, "size/i");
}

bool
TPLeptonVeto::pass(panda::EventMonophoton const& _inEvent, panda::EventTP& _outEvent)
{
  // veto condition: loose, pt > 10 GeV, no matching candidate photon / lepton

  std::vector<panda::ParticleCollection const*> cols;
  if (eventType_ == kTPEEG || eventType_ == kTPMMG)
    cols.emplace_back(getLooseTags(_outEvent));
  cols.emplace_back(getTags(_outEvent));
  cols.emplace_back(getProbes(_outEvent));
    
  nMuons_ = 0;
  
  std::vector<panda::Muon const*> goodMuons;

  for (auto& muon : _inEvent.muons) {
    if (!muon.loose || muon.pt() < 10.)
      continue;

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(muon) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was an overlappin particle
        overlap = true;
        break;
      }
    }

    if (!overlap) {
      goodMuons.push_back(&muon);
      ++nMuons_;
    }
  }

  nElectrons_ = 0;

  for (auto& electron : _inEvent.electrons) {
    if (!electron.loose || electron.pt() < 10.)
      continue;

    bool overlap(false);
    for (auto* col : cols) {
      unsigned iP(0);
      for (; iP != col->size(); ++iP) {
        if ((*col)[iP].dR2(electron) < 0.25)
          break;
      }
      if (iP != col->size()) {
        // there was an overlappin particle
        overlap = true;
        break;
      }
    }

    if (overlap)
      continue;

    unsigned iP(0);
    for (; iP != goodMuons.size(); ++iP) {
      if (goodMuons[iP]->dR2(electron) < 0.25)
        break;
    }
    if (iP == goodMuons.size())
      ++nElectrons_;
  }

  bool result(true);
  if (vetoElectrons_ && nElectrons_ != 0)
    result = false;
  if (vetoMuons_ && nMuons_ != 0)
    result = false;

  return result;
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
TagAndProbePairZ::pass(panda::EventMonophoton const& _event, panda::EventTP&)
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
// TPJetCleaning
//--------------------------------------------------------------------

void
TPJetCleaning::apply(panda::EventMonophoton const& _event, panda::EventTP& _outEvent)
{
  std::vector<std::pair<panda::ParticleCollection const*, bool>> cols;
  bool leadingProbeOnly(false);
  switch (eventType_) {
  case kTPEEG:
  case kTPMMG:
    cols.emplace_back(getLooseTags(_outEvent), false);
    //fallthrough
  case kTPEG:
  case kTPMG:
    leadingProbeOnly = true;
    break;
  default:
    break;
  }

  cols.emplace_back(getTags(_outEvent), false);
  cols.emplace_back(getProbes(_outEvent), leadingProbeOnly);

  for (auto& jet : _event.jets) {
    if (jet.pt() < minPt_ || std::abs(jet.eta()) > 5.)
      continue;

    bool overlap(false);
    for (auto& col : cols) {
      // For TPXG probes, we only want to clean overlaps wrt the leading candidate
      unsigned nP(col.second ? std::min(unsigned(1), col.first->size()) : col.first->size());

      unsigned iP(0);
      for (; iP != nP; ++iP) {
        if (jet.dR2((*col.first)[iP]) < 0.16)
          break;
      }
      if (iP != nP) {
        overlap = true;
        break;
      }
    }
    if (overlap)
      continue;

    _outEvent.jets.push_back(jet);
  }
}

//--------------------------------------------------------------------
// TPTriggerMatch
//--------------------------------------------------------------------

void
TPTriggerMatch::initialize(panda::EventMonophoton& _event)
{
  _event.run.setLoadTrigger(true);
  for (auto& name : filterNames_)
    _event.registerTriggerObjects(name);
}

void
TPTriggerMatch::addInputBranch(panda::utils::BranchList& _blist)
{
  _blist += {"triggerObjects"};
}

void
TPTriggerMatch::addBranches(TTree& _skimTree)
{
  if (candidate_ == kProbe)
    _skimTree.Branch("probes.hltmatch" + name_, matchResults_, "hltmatch" + name_ + "[probes.size]/O");
  else
    _skimTree.Branch("tags.hltmatch" + name_, matchResults_, "hltmatch" + name_ + "[tags.size]/O");
}

void
TPTriggerMatch::apply(panda::EventMonophoton const& _event, panda::EventTP& _outEvent)
{
  typedef std::vector<panda::HLTObject const*> HLTObjectVector;

  std::fill_n(matchResults_, NMAX_PARTICLES, false);

  bool any(false);
  std::vector<std::pair<HLTObjectVector const*, double>> filterObjects;
  for (auto& name : filterNames_) {
    //    std::cout << "Looking for objects for filter " << name << std::endl;
    auto& objects(_event.triggerObjects.filterObjects(name));
    if (objects.size() != 0)
      any = true;

    //    std::cout << "Found: size " << objects.size() << std::endl;
    double dR(name.Index("hltL1s") == 0 ? 0.3 : 0.15);
    filterObjects.emplace_back(&objects, dR);
  }

  if (!any)
    return;

  auto& candidates(candidate_ == kProbe ? *getProbes(_outEvent) : *getTags(_outEvent));

  //  std::cout << "now match against candidates: size " << candidates.size() << std::endl;

  for (unsigned iP(0); iP != candidates.size(); ++iP) {
    auto& cand(candidates[iP]);

    for (auto& pair : filterObjects) {
      auto& objects(*pair.first);
      double dR(pair.second);

      unsigned iO(0);
      for (; iO != objects.size(); ++iO) {
        if (cand.dR(*objects[iO]) < dR) {
          matchResults_[iP] = true;
          break;
        }
      }
      if (iO != objects.size())
        break;
    }
  }
}
