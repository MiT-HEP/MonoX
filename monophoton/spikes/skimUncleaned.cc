#include "PandaTree/Objects/interface/Event.h"
#include "PandaTree/Objects/interface/EventMonophoton.h"

#include "TFile.h"
#include "TTree.h"
#include "TLeaf.h"
#include "TBranch.h"
#include "TString.h"

#include "../misc/photon_extra.h"

#include <iostream>
#include <vector>
#include <bitset>

void
skimUncleaned(TTree* _input, char const* _outputNameBase, bool _triggeringPhotons, long _nEntries = -1)
{
  // Skim the input tree for off-time (-15 < t < -10 ns) or narrow (sieie < 0.001 || sipip < 0.001 || (sieie < 0.008 && sipip < 0.008)) super clusters and write an EventMonophoton output

  panda::Event event;
  unsigned const NMAX(256);

  //mkbranch
  unsigned size;
  float rawPt[NMAX];
  float eta[NMAX];
  float phi[NMAX];
  float sieie[NMAX];
  float sipip[NMAX];
  float emax[NMAX];
  float e2nd[NMAX];
  float e4[NMAX];
  float time[NMAX];
  float timeSpan[NMAX];
  float mipEnergy[NMAX];
  float trackIso[NMAX];
  float metPhotonDPhi;
  float metMinJetDPhi;
  //mkbranch

  float outTrackIso[NMAX];
  unsigned short photonType[NMAX]; // 0 -> SC replaced, 1 -> SC unchanged, 2 -> created
  panda::EventMonophoton outEvent;
  panda::RecoMet origMet("origMet");
  bool pass165(false);
  bool pass135(false);
  bool pass120(false);

  enum OutputClass {
    kOfftime,
    kNarrow,
    kOfftimeAltTrig,
    kNarrowAltTrig,
    nOutputClasses
  };

  TString outputSuffix[nOutputClasses] = {
    "offtime",
    "narrow",
    "offtimealt",
    "narrowalt"
  };

  TString outputNameBase(_outputNameBase);
  TTree* output[nOutputClasses];

  for (unsigned iO(0); iO != nOutputClasses; ++iO) {
    if (!_triggeringPhotons && (iO == kOfftimeAltTrig || iO == kNarrowAltTrig))
      continue;

    auto* outputFile(TFile::Open(outputNameBase + "_" + outputSuffix[iO] + ".root", "recreate"));

    output[iO] = new TTree("events", "Events");
    outEvent.book(*output[iO], {"runNumber", "lumiNumber", "eventNumber", "npv", "vertices", "weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"});
    origMet.book(*output[iO]);
    output[iO]->Branch("photons.trackIso", outTrackIso, "trackIso[photons.size]/F");
    output[iO]->Branch("photons.type", photonType, "type[photons.size]/s");
    output[iO]->Branch("t1Met.photonDPhi", &metPhotonDPhi, "photonDPhi/F");
    output[iO]->Branch("t1Met.minJetDPhi", &metMinJetDPhi, "minJetDPhi/F");
    output[iO]->Branch("HLT_Photon165_HE10", &pass165, "HLT_Photon165_HE10/O");
    output[iO]->Branch("HLT_Photon135_PFMET100", &pass135, "HLT_Photon135_PFMET100/O");
    output[iO]->Branch("HLT_Photon120_R9Id90_HE10_IsoM", &pass120, "HLT_Photon120_R9Id90_HE10_IsoM/O");
  }

  panda::utils::BranchList branchList = {
    "!*",
    "runNumber",
    "lumiNumber",
    "eventNumber",
    "isData",
    "weight",
    "npv",
    "rho",
    "rhoCentralCalo",
    "triggers",
    "vertices",
    "superClusters",
    "electrons",
    "muons",
    "taus",
    "photons",
    "chsAK4Jets",
    "!chsAK4Jets.constituents_",
    "pfMet",
    "metFilters"
  };

  event.setAddress(*_input, branchList);

  unsigned hlt165(0);
  unsigned hlt135(0);
  unsigned hlt120(0);
  if (_triggeringPhotons) {
    hlt165 = event.registerTrigger("HLT_Photon165_HE10");
    hlt135 = event.registerTrigger("HLT_Photon135_PFMET100");
    hlt120 = event.registerTrigger("HLT_Photon120_R9Id90_HE10_IsoM");
  }

  struct MyBranch {
    MyBranch(char const* _n, void* _a) : name(_n), addr(_a) {}
    TString name;
    void* addr;
    TBranch* branch{0};
  };

  enum BranchIndex {
    bSize,
    bRawPt,
    bTime,
    bEta,
    bSieie,
    bSipip,
    nBranchIndices
  };

  std::vector<MyBranch> extraBranches;
  // order in BranchIndices
  extraBranches.emplace_back("superClustersFT.size", &size);
  extraBranches.emplace_back("superClustersFT.rawPt", rawPt);
  extraBranches.emplace_back("superClustersFT.time", time);
  extraBranches.emplace_back("superClustersFT.eta", eta);
  extraBranches.emplace_back("superClustersFT.sieie", sieie);
  extraBranches.emplace_back("superClustersFT.sipip", sipip);

  extraBranches.emplace_back("superClustersFT.phi", phi);
  extraBranches.emplace_back("superClustersFT.emax", emax);
  extraBranches.emplace_back("superClustersFT.e2nd", e2nd);
  extraBranches.emplace_back("superClustersFT.e4", e4);
  extraBranches.emplace_back("superClustersFT.timeSpan", timeSpan);
  extraBranches.emplace_back("superClustersFT.mipEnergy", mipEnergy);
  extraBranches.emplace_back("superClustersFT.trackIso", trackIso);

  for (auto& b : extraBranches)
    _input->SetBranchAddress(b.name, b.addr);

  auto RawPtGreater([](panda::Element const& _p1, panda::Element const& _p2)->bool {
      return static_cast<panda::XPhoton const&>(_p1).scRawPt > static_cast<panda::XPhoton const&>(_p2).scRawPt;
    });

  std::bitset<nOutputClasses> matchClass;

  long iEntry(0);
  int iTree(-1);
  while (iEntry != _nEntries) {
    if (iEntry % 100000 == 0)
      std::cout << iEntry << std::endl;

    long localEntry(_input->LoadTree(iEntry++));
    if (localEntry < 0)
      break;

    if (_input->GetTreeNumber() != iTree) {
      iTree = _input->GetTreeNumber();

      for (auto& b : extraBranches)
        b.branch = _input->GetBranch(b.name);
    }

    extraBranches[bSize].branch->GetEntry(localEntry);
    if (size == 0)
      continue;

    for (unsigned b : {bRawPt, bTime, bEta, bSieie, bSipip})
      extraBranches[b].branch->GetEntry(localEntry);

    matchClass.reset();

    for (unsigned iC(0); iC != size; ++iC) {
      if (_triggeringPhotons && rawPt[iC] < 110.)
        continue;
      if (rawPt[iC] < 20.)
        continue;
      if (std::abs(eta[iC]) > 1.4442)
        continue;

      if (time[iC] > -15. && time[iC] < -10.)
        matchClass.set(kOfftime);
      if (sieie[iC] < 0.001 || sipip[iC] < 0.001 || (sieie[iC] < 0.008 && sipip[iC] < 0.008))
        matchClass.set(kNarrow);
    }

    if (matchClass.none())
      continue;

    event.getEntry(*_input, localEntry, true);

    pass165 = false;
    pass135 = false;
    pass120 = false;

    if (_triggeringPhotons) {
      pass165 = event.triggerFired(hlt165);
      pass135 = event.triggerFired(hlt135);
      pass120 = event.triggerFired(hlt120);

      if (!pass165 && !pass135 && !pass120)
        continue;
    }

    if (matchClass[kOfftime]) {
      if (!pass165)
        matchClass.reset(kOfftime);
      if (pass135 || pass120)
        matchClass.set(kOfftimeAltTrig);
    }

    if (matchClass[kNarrow]) {
      if (!pass165)
        matchClass.reset(kNarrow);
      if (pass135 || pass120)
        matchClass.set(kNarrowAltTrig);
    }

    for (unsigned iB(nBranchIndices); iB != extraBranches.size(); ++iB)
      extraBranches[iB].branch->GetEntry(localEntry);

    outEvent.runNumber = event.runNumber;
    outEvent.lumiNumber = event.lumiNumber;
    outEvent.eventNumber = event.eventNumber;
    outEvent.isData = event.isData;
    outEvent.weight = event.weight;
    outEvent.triggers = event.triggers;
    outEvent.npv = event.npv;
    outEvent.rho = event.rho;
    outEvent.rhoCentralCalo = event.rhoCentralCalo;
    outEvent.vertices = event.vertices;
    outEvent.muons = event.muons;
    outEvent.taus = event.taus;
    outEvent.jets = event.chsAK4Jets;

    outEvent.metFilters = event.metFilters;

    origMet = event.pfMet;

    for (unsigned iC(0); iC != size; ++iC) {
      auto& sc(outEvent.superClusters.create_back());
      sc.rawPt = rawPt[iC];
      sc.eta = eta[iC];
      sc.phi = phi[iC];
    }

    TVector2 metCorr;

    std::vector<bool> used(size, false);
    std::vector<bool> removed(event.superClusters.size(), false);

    outEvent.electrons.resize(event.electrons.size());
    for (unsigned iE(0); iE != event.electrons.size(); ++iE) {
      auto& lhs(outEvent.electrons[iE]);
      auto& rhs(event.electrons[iE]);

      lhs = rhs;

      auto& ec(*rhs.superCluster);
      for (unsigned iC(0); iC != size; ++iC) {
        double dEta(ec.eta - eta[iC]);
        double dPhi(TVector2::Phi_mpi_pi(ec.phi - phi[iC]));
        if (dEta * dEta + dPhi * dPhi < 0.04) {
          lhs.superCluster.idx() = iC;
          used[iC] = true;

          if (!removed[rhs.superCluster.idx()]) {
            metCorr += TVector2(ec.rawPt * std::cos(ec.phi), ec.rawPt * std::sin(ec.phi));
            metCorr -= TVector2(rawPt[iC] * std::cos(phi[iC]), rawPt[iC] * std::sin(phi[iC]));
            removed[rhs.superCluster.idx()] = true;
          }

          break;
        }
      }
    }

    float outTrackIsoTmp[NMAX];
    unsigned short photonTypeTmp[NMAX];

    outEvent.photons.resize(event.photons.size());
    for (unsigned iP(0); iP != event.photons.size(); ++iP) {
      auto& lhs(outEvent.photons[iP]);
      auto& rhs(event.photons[iP]);

      static_cast<panda::Photon&>(lhs) = rhs;

      panda::photon_extra(lhs, rhs, event.rho);

      auto& ec(*rhs.superCluster);
      unsigned iC(0);
      for (; iC != size; ++iC) {
        double dEta(ec.eta - eta[iC]);
        double dPhi(TVector2::Phi_mpi_pi(ec.phi - phi[iC]));
        if (dEta * dEta + dPhi * dPhi < 0.04) {
          lhs.superCluster.idx() = iC;
          lhs.scRawPt = rawPt[iC];
          lhs.scEta = eta[iC];

          lhs.hOverE = rhs.hOverE * ec.rawPt * std::cosh(ec.eta) / rawPt[iC] / std::cosh(eta[iC]);
          lhs.sieie = sieie[iC];
          lhs.sipip = sipip[iC];
          lhs.emax = emax[iC];
          lhs.e2nd = e2nd[iC];
          lhs.e4 = e4[iC];
          lhs.time = time[iC];
          lhs.timeSpan = timeSpan[iC];
          outTrackIsoTmp[iP] = trackIso[iC];

          photonTypeTmp[iP] = 0;

          used[iC] = true;

          if (!removed[rhs.superCluster.idx()]) {
            metCorr += TVector2(ec.rawPt * std::cos(ec.phi), ec.rawPt * std::sin(ec.phi));
            metCorr -= TVector2(rawPt[iC] * std::cos(phi[iC]), rawPt[iC] * std::sin(phi[iC]));
            removed[rhs.superCluster.idx()] = true;
          }

          break;
        }
      }

      if (iC == size)
        photonTypeTmp[iP] = 1;
    }

    // now make up a photon for each unused out-of-time FT SC

    for (unsigned iC(0); iC != size; ++iC) {
      if (used[iC] || rawPt[iC] < 15.)
        continue;

      auto& photon(outEvent.photons.create_back());

      photon.setPtEtaPhiM(rawPt[iC], eta[iC], phi[iC], 0.);

      photon.superCluster.idx() = iC;
      photon.isEB = std::abs(eta[iC]) < 1.4442;
      photon.scRawPt = rawPt[iC];
      photon.scEta = eta[iC];

      photon.sieie = sieie[iC];
      photon.sipip = sipip[iC];
      photon.emax = emax[iC];
      photon.e2nd = e2nd[iC];
      photon.e4 = e4[iC];
      photon.time = time[iC];
      photon.timeSpan = timeSpan[iC];
      photon.mipEnergy = mipEnergy[iC];
      outTrackIsoTmp[outEvent.photons.size() - 1] = trackIso[iC];

      // all original superclusters must be removed by now but just to make sure
      unsigned iO(0);
      for (; iO != event.superClusters.size(); ++iO) {
        if (removed[iO])
          continue;

        auto& oc(event.superClusters[iO]);
        double dEta(oc.eta - eta[iC]);
        double dPhi(TVector2::Phi_mpi_pi(oc.phi - phi[iC]));
        if (dEta * dEta + dPhi * dPhi < 0.04) {
          metCorr += TVector2(oc.rawPt * std::cos(oc.phi), oc.rawPt * std::sin(oc.phi));
          break;
        }
      }

      metCorr -= TVector2(rawPt[iC] * std::cos(phi[iC]), rawPt[iC] * std::sin(phi[iC]));

      photonTypeTmp[outEvent.photons.size() - 1] = 2;
    }

    // correct the MET with FT - default SC differences
    auto metV(event.pfMet.v() + metCorr);
    outEvent.t1Met.setXY(metV.X(), metV.Y());

    std::vector<unsigned> originalIndices(outEvent.photons.sort(RawPtGreater));
    for (unsigned iOut(0); iOut != outEvent.photons.size(); ++iOut) {
      unsigned iOrig(originalIndices[iOut]);
      outTrackIso[iOut] = outTrackIsoTmp[iOrig];
      photonType[iOut] = photonTypeTmp[iOrig];
    }

    if (outEvent.photons.size() != 0)
      metPhotonDPhi = std::abs(TVector2::Phi_mpi_pi(outEvent.t1Met.phi - outEvent.photons[0].phi()));
    else
      metPhotonDPhi = 0.;
    
    metMinJetDPhi = 4.;
    for (unsigned iJ(0); iJ != 4 && iJ != outEvent.jets.size(); ++iJ) {
      auto& jet(outEvent.jets[iJ]);
      double dPhi(std::abs(TVector2::Phi_mpi_pi(outEvent.t1Met.phi - jet.phi())));
      if (dPhi < metMinJetDPhi)
        metMinJetDPhi = dPhi;
    }

    for (unsigned iO(0); iO != nOutputClasses; ++iO) {
      if (matchClass[iO])
        output[iO]->Fill();
    }
  }

  std::cout << "Processed " << iEntry << " events" << std::endl;

  for (unsigned iO(0); iO != nOutputClasses; ++iO) {
    if (!_triggeringPhotons && (iO == kOfftimeAltTrig || iO == kNarrowAltTrig))
      continue;

    auto* outputFile(output[iO]->GetCurrentFile());
    outputFile->cd();
    output[iO]->Write();
    delete outputFile;
  }
}
