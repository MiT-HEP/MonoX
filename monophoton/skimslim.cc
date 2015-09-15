#include "TFile.h"
#include "TChain.h"
#include "TTree.h"
#include "TLorentzVector.h"
#include "TString.h"

#include "NeroProducer/Core/interface/BareEvent.hpp"
#include "NeroProducer/Core/interface/BareJets.hpp"
#include "NeroProducer/Core/interface/BareLeptons.hpp"
#include "NeroProducer/Core/interface/BareMet.hpp"
#include "NeroProducer/Core/interface/BarePhotons.hpp"
#include "NeroProducer/Core/interface/BareTaus.hpp"
#include "NeroProducer/Core/interface/BareMonteCarlo.hpp"

#include <iostream>

void
skimslim(TTree* _cutTree, TTree* _input, TFile* _outputFile)
{
  bool isMC(_input->GetBranch("mcWeight") != 0);

  _outputFile->cd();
  auto* output(new TTree("events", "events"));
  
  BareEvent event;
  BareJets jets;
  BareLeptons leptons;
  BareMet met;
  BarePhotons photons;
  BareTaus taus;
  BareMonteCarlo mc;
  
  // if we want to slim more we'll need to define branches "a la carte"
  event.defineBranches(output);
  jets.defineBranches(output);
  leptons.defineBranches(output);
  met.defineBranches(output);
  photons.defineBranches(output);
  taus.defineBranches(output);
  if (isMC)
    mc.defineBranches(output);

  event.setBranchAddresses(_input);
  jets.setBranchAddresses(_input);
  leptons.setBranchAddresses(_input);
  met.setBranchAddresses(_input);
  photons.setBranchAddresses(_input);
  taus.setBranchAddresses(_input);
  if (isMC)
    mc.setBranchAddresses(_input);

  _cutTree->SetBranchStatus("*", 0);
  _cutTree->SetBranchStatus("lepP4", 1);
  _cutTree->SetBranchStatus("lepSelBits", 1);
  _cutTree->SetBranchStatus("photonP4", 1);

  leptons.setBranchAddresses(_cutTree);
  photons.setBranchAddresses(_cutTree);

  long iEntry(0);
  while (_cutTree->GetEntry(iEntry++) > 0) {
    unsigned iL(0);
    for (; iL != leptons.size(); ++iL) {
      if ((leptons.passSelection(iL, BareLeptons::LepLoose)))
        break;
    }
    if (iL != leptons.size())
      continue;

    unsigned nLoose(0);
    unsigned iMedium(-1);
    for (unsigned iP(0); iP != photons.size(); ++iP) {
      if (photons.pt(iP) < 15.)
        continue;
      ++nLoose;

      //      if (photons.pt(iP) > 180. && photons.mediumid->at(iP) == 1)
      if (photons.pt(iP) > 180.)
        iMedium = iP;
    }

    if (nLoose > 1)
      continue;

    if (iMedium > photons.size())
      continue;

    _input->GetEntry(iEntry - 1);

    output->Fill();
  }

  _outputFile->cd();
  output->Write();
  delete output;
}
