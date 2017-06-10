#include "PandaTree/Objects/interface/Event.h"
#include "PandaTree/Objects/interface/EventMonophoton.h"

#include "TFile.h"
#include "TTree.h"
#include "TLeaf.h"

#include "../misc/photon_extra.h"

#include <iostream>

void
skimUncleaned(TTree* _input, TFile* _outputFile, long _nEntries = -1)
{
  // Skim the input tree for off-time (-15 < t < -10 ns) super clusters and write an EventMonophoton output

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
  unsigned short photonType[NMAX]; // 0 -> SC replaced, 1 -> SC unchanged, 2 -> created
  //mkbranch
  panda::EventMonophoton outEvent;

  _outputFile->cd();
  auto* output(new TTree("events", "Events"));
  outEvent.book(*output, {"runNumber", "lumiNumber", "eventNumber", "npv", "vertices", "weight", "jets", "photons", "electrons", "muons", "taus", "superClusters", "t1Met"});
  output->Branch("photons.type", photonType, "type[photons.size]/s");

  event.setStatus(*_input, {"*"});
  event.setAddress(*_input, {"*"});

  auto hltToken(event.registerTrigger("HLT_Photon165_HE10"));

  _input->SetBranchAddress("superClustersFT.size", &size);
  _input->SetBranchAddress("superClustersFT.rawPt", rawPt);
  _input->SetBranchAddress("superClustersFT.eta", eta);
  _input->SetBranchAddress("superClustersFT.phi", phi);
  _input->SetBranchAddress("superClustersFT.sieie", sieie);
  _input->SetBranchAddress("superClustersFT.sipip", sipip);
  _input->SetBranchAddress("superClustersFT.emax", emax);
  _input->SetBranchAddress("superClustersFT.e2nd", e2nd);
  _input->SetBranchAddress("superClustersFT.e4", e4);
  _input->SetBranchAddress("superClustersFT.time", time);
  _input->SetBranchAddress("superClustersFT.timeSpan", timeSpan);
  _input->SetBranchAddress("superClustersFT.mipEnergy", mipEnergy);

  TBranch* sizeBranch(0);
  TBranch* rawPtBranch(0);
  TBranch* timeBranch(0);

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
      sizeBranch = _input->GetBranch("superClustersFT.size");
      rawPtBranch = _input->GetBranch("superClustersFT.rawPt");
      timeBranch = _input->GetBranch("superClustersFT.time");
    }

    sizeBranch->GetEntry(localEntry);
    if (size == 0)
      continue;

    rawPtBranch->GetEntry(localEntry);
    timeBranch->GetEntry(localEntry);

    unsigned iC(0);
    for (; iC != size; ++iC) {
      if (rawPt[iC] > 170. && time[iC] > -15. && time[iC] < -10.)
        break;
    }

    if (iC == size)
      continue;

    event.getEntry(*_input, iEntry - 1);

    if (!event.triggerFired(hltToken))
      continue;

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
    outEvent.t1Met = event.pfMet;
    outEvent.rawMet = event.rawMet;
    outEvent.caloMet = event.caloMet;
    outEvent.metMuOnlyFix = event.metMuOnlyFix;
    outEvent.metNoFix = event.metNoFix;
    outEvent.metFilters = event.metFilters;

    for (iC = 0; iC != size; ++iC) {
      auto& sc(outEvent.superClusters.create_back());
      sc.rawPt = rawPt[iC];
      sc.eta = eta[iC];
      sc.phi = phi[iC];
    }

    std::vector<bool> used(size, false);

    outEvent.electrons.resize(event.electrons.size());
    for (unsigned iE(0); iE != event.electrons.size(); ++iE) {
      auto& lhs(outEvent.electrons[iE]);
      auto& rhs(event.electrons[iE]);

      lhs = rhs;

      auto& ec(*rhs.superCluster);
      for (iC = 0; iC != size; ++iC) {
        double dEta(ec.eta - eta[iC]);
        double dPhi(TVector2::Phi_mpi_pi(ec.phi - phi[iC]));
        if (dEta * dEta + dPhi * dPhi < 0.04) {
          lhs.superCluster.idx() = iC;
          used[iC] = true;
          break;
        }
      }
    }

    outEvent.photons.resize(event.photons.size());
    for (unsigned iP(0); iP != event.photons.size(); ++iP) {
      auto& lhs(outEvent.photons[iP]);
      auto& rhs(event.photons[iP]);

      static_cast<panda::Photon&>(lhs) = rhs;

      panda::photon_extra(lhs, rhs, event.rho);

      auto& ec(*rhs.superCluster);
      iC = 0;
      for (; iC != size; ++iC) {
        double dEta(ec.eta - eta[iC]);
        double dPhi(TVector2::Phi_mpi_pi(ec.phi - phi[iC]));
        if (dEta * dEta + dPhi * dPhi < 0.04) {
          lhs.superCluster.idx() = iC;
          lhs.scRawPt = rawPt[iC];
          lhs.scEta = eta[iC];

          lhs.sieie = sieie[iC];
          lhs.sipip = sipip[iC];
          lhs.emax = emax[iC];
          lhs.e2nd = e2nd[iC];
          lhs.e4 = e4[iC];
          lhs.time = time[iC];
          lhs.timeSpan = timeSpan[iC];

          photonType[iP] = 0;

          used[iC] = true;
          break;
        }
      }

      if (iC == size)
        photonType[iP] = 1;
    }

    for (iC = 0; iC != size; ++iC) {
      if (used[iC])
        continue;

      // now make up a photon for each unused FT SC

      photonType[outEvent.photons.size()] = 2;

      auto& photon(outEvent.photons.create_back());

      photon.setPtEtaPhiM(rawPt[iC], eta[iC], phi[iC], 0.);

      photon.superCluster.idx() = iC;
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
    }

    output->Fill();
  }

  std::cout << "Processed " << iEntry << " events" << std::endl;

  _outputFile->cd();
  output->Write();
}
