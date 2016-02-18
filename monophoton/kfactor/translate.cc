#include "TTree.h"
#include "TFile.h"

#include <algorithm>
#include <iostream>

enum GenMode {
  kLHE,
  kPostShower
};

void
translate(TTree* _input, char const* _outputName, GenMode _mode)
{
  unsigned partonSize;
  unsigned size;
  int partonPid[64];
  int pid[512];
  float pt[512];
  float eta[512];
  float phi[512];
  short status[512];
  unsigned short ancestor[512];

  if (_mode == kLHE) {
    _input->SetBranchAddress("partons.size", &size);
    _input->SetBranchAddress("partons.pid", pid);
    _input->SetBranchAddress("partons.status", status);
    _input->SetBranchAddress("partons.pt", pt);
    _input->SetBranchAddress("partons.eta", eta);
    _input->SetBranchAddress("partons.phi", phi);
  }
  else {
    _input->SetBranchAddress("partonFinalStates.size", &size);
    _input->SetBranchAddress("partonFinalStates.pid", pid);
    _input->SetBranchAddress("partonFinalStates.pt", pt);
    _input->SetBranchAddress("partonFinalStates.eta", eta);
    _input->SetBranchAddress("partonFinalStates.phi", phi);

    _input->SetBranchAddress("partonFinalStates.ancestor", ancestor);
    _input->SetBranchAddress("partons.size", &partonSize);
    _input->SetBranchAddress("partons.pid", partonPid);

    std::fill_n(status, 512, 1);
  }

  auto* outputFile(TFile::Open(_outputName, "recreate"));
  auto* output(new TTree("events", "gen photon kinematics"));

  float outPt;
  float outEta;
  float outPhi;

  output->Branch("pt", &outPt, "pt/F");
  output->Branch("eta", &outEta, "eta/F");
  output->Branch("phi", &outPhi, "phi/F");

  long nMiss(0);

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    unsigned iP(0);
    for (; iP != size; ++iP) {
      if (status[iP] != 1 || pid[iP] != 22)
        continue;

      if (_mode == kPostShower && partonPid[ancestor[iP]] != 22)
        continue;

      outPt = pt[iP];
      outEta = eta[iP];
      outPhi = phi[iP];

      break;
    }

    if (iP == size)
      ++nMiss;
    else
      output->Fill();
  }

  std::cout << nMiss << " events did not have a photon" << std::endl;

  outputFile->cd();
  output->Write();
  delete outputFile;
}
