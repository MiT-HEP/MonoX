#include "TreeEntries_simpletree.h"

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"

#include <iostream>

void
skimUncleaned(TTree* _input, char const* _outputNameBase, long _nEntries = -1)
{
  enum Skim {
    kHighMet,
    kLowMet,
    //    kZee,
    nSkims
  };
  
  TString skimNames[] = {
    "highmet",
    "lowmet",
    //    "zee"
  };

  simpletree::Event event;
  simpletree::SuperCluster outCluster;
  simpletree::Met outMet("met");

  TTree* outputs[nSkims]{};

  for (unsigned iS(0); iS != nSkims; ++iS) {
    TString outputName(_outputNameBase);
    outputName.ReplaceAll(".root", "_" + skimNames[iS] + ".root");
    auto* outputFile(TFile::Open(outputName, "recreate"));
    outputs[iS] = new TTree("events", "Events");
    event.book(*outputs[iS], {"run", "lumi", "event"});
    outCluster.book(*outputs[iS], "cluster");
    outMet.book(*outputs[iS]);
  }

  // float mZ(0.);
  // outputs[kZee]->Branch("mZ", &mZ, "mZ/F");

  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"t1Met", "superClusters"});

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 0)
      std::cout << iEntry << std::endl;

    auto& clusters(event.superClusters);

    outMet = event.t1Met;

    for (unsigned iC(0); iC != clusters.size(); ++iC) {
      auto& sc(clusters[iC]);

      if (!sc.isEB)
        continue;

      if (sc.rawPt < 175.)
        continue;

      outCluster = sc;

      if (event.t1Met.met > 140.)
        outputs[kHighMet]->Fill();

      if (event.t1Met.met < 40.)
        outputs[kLowMet]->Fill();

      // // trackIso kills electrons
      // // if (sc.trackIso > 10.)
      // //   continue;
      // if (sc.sieie > 0.0102 || sc.sieie < 0.001 || sc.sipip < 0.001)
      //   continue;

      // TLorentzVector p1;
      // p1.SetPtEtaPhiM(sc.rawPt, sc.eta, sc.phi, 0.);

      // for (unsigned iC2(0); iC2 != clusters.size(); ++iC2) {
      //   if (iC2 == iC)
      //     continue;

      //   auto& sc2(clusters[iC2]);

      //   if (!sc2.isEB)
      //     continue;
      //   // if (sc2.trackIso > 10.)
      //   //   continue;
      //   if (sc2.sieie > 0.0102 || sc2.sieie < 0.001 || sc2.sipip < 0.001)
      //     continue;

      //   TLorentzVector p2;
      //   p2.SetPtEtaPhiM(sc2.rawPt, sc2.eta, sc2.phi, 0.);
      //   mZ = (p1 + p2).M();
      //   if (mZ > 61. && mZ < 121.) {
      //     outputs[kZee]->Fill();
      //     break;
      //   }
      // }
    }
  }

  for (unsigned iS(0); iS != nSkims; ++iS) {
    auto* outputFile(outputs[iS]->GetCurrentFile());
    outputFile->cd();
    outputFile->Write();
    delete outputFile;
  }
}
