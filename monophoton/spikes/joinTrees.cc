#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TVector2.h"

#include <tuple>
#include <map>
#include <iostream>

void
joinTrees(TTree* _mainInput, TTree* _scInput, TTree* _output, long _nEntries = -1)
{
  typedef std::tuple<unsigned, unsigned, unsigned> EventID;
  std::map<EventID, long> entriesMap;

  simpletree::Event event;
  event.setStatus(*_scInput, false, {"*"});
  event.setAddress(*_scInput, {"run", "lumi", "event"});

  std::cout << "Extracting event IDs" << std::endl;

  long iEntry(0);
  while (_scInput->GetEntry(iEntry) > 0) {
    entriesMap.emplace(std::make_tuple(event.run, event.lumi, event.event), iEntry);
    ++iEntry;
  }

  std::cout << "Done. " << entriesMap.size() << " events in uncleaned SC input" << std::endl;

  event.setStatus(*_scInput, false, {"*"});

  event.setAddress(*_mainInput);
  event.book(*_output);
  simpletree::SuperClusterCollection clusters("superClusters");
  clusters.setAddress(*_scInput);
  clusters.setName("uncleanedClusters");
  clusters.book(*_output);
  bool hasUncleanedClusters(false);
  short matched[simpletree::Particle::array_data::NMAX];
  float time[simpletree::Particle::array_data::NMAX];
  _output->Branch("hasUncleanedClusters", &hasUncleanedClusters, "hasUncleanedClusters/O");
  _output->Branch("photons.matchedUC", matched, "matchedUC[photons.size]/S");
  _output->Branch("photons.uncleanedTime", time, "uncleanedTime[photons.size]/F");

  iEntry = 0;
  while (iEntry != _nEntries && _mainInput->GetEntry(iEntry++) > 0) {
    for (unsigned iPh(0); iPh != event.photons.size(); ++iPh) {
      matched[iPh] = -1;
      time[iPh] = 0.;
    }

    auto eItr(entriesMap.find(std::make_tuple(event.run, event.lumi, event.event)));
    if (eItr == entriesMap.end()) {
      hasUncleanedClusters = false;
      clusters.resize(0);
    }
    else {
      hasUncleanedClusters = true;
      _scInput->GetEntry(eItr->second);

      for (unsigned iPh(0); iPh != event.photons.size(); ++iPh) {
        auto& photon(event.photons[iPh]);
        for (matched[iPh] = 0; matched[iPh] != clusters.size(); ++matched[iPh]) {
          auto& cluster(clusters[matched[iPh]]);
          double dEta(photon.eta - cluster.eta);
          double dPhi(TVector2::Phi_mpi_pi(photon.phi - cluster.phi));
          if (dEta * dEta + dPhi * dPhi < 0.04) {
            time[iPh] = cluster.time;
            break;
          }
        }
        if (matched[iPh] == clusters.size())
          matched[iPh] = -1;
      }
    }

    _output->Fill();
  }
}
