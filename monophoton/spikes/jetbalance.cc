#include "PandaTree/Objects/interface/EventMonophoton.h"

enum Boson {
  bPhoton,
  bZ,
  nBosons
};

void
jetbalance(TTree* _input, TFile* _outputFile, Boson _boson, long _nEntries = -1)
{
  panda::EventMonophoton event;
  event.setReadRunTree(false);

  event.setAddress(*_input);
  float dimu_mass(0.);
  float dimu_pt(0.);
  float dimu_phi(0.);
  if (_boson == bZ) {
    _input->SetBranchAddress("dimu.mass", &dimu_mass);
    _input->SetBranchAddress("dimu.pt", &dimu_pt);
    _input->SetBranchAddress("dimu.phi", &dimu_phi);
  }
  TBranch* bMass(0);
  TBranch* bPt(0);
  TBranch* bPhi(0);

  _outputFile->cd();
  auto* output(_input->CloneTree(0));

  float balance;
  output->Branch("balance", &balance);

  long iEntry(0);
  int iTree(-1);
  while (iEntry != _nEntries && event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    TVector2 vPt;

    if (_boson == bPhoton) {
      if (event.photons.size() != 1)
        continue;

      auto& photon(event.photons[0]);
      vPt.SetMagPhi(photon.scRawPt, photon.phi());
    }
    else {
      if (_input->GetTreeNumber() != iTree) {
        iTree = _input->GetTreeNumber();
        bMass = _input->GetBranch("dimu.mass");
        bPt = _input->GetBranch("dimu.pt");
        bPhi = _input->GetBranch("dimu.phi");
      }
      
      bMass->GetEntry(iEntry - 1);
      bPt->GetEntry(iEntry - 1);
      bPhi->GetEntry(iEntry - 1);

      if (dimu_pt < 175. || dimu_mass < 81. || dimu_mass > 101.)
        continue;

      vPt.SetMagPhi(dimu_pt, dimu_phi);
    }

    if (event.jets.size() == 0)
      continue;

    if (event.jets.size() > 1 && event.jets[1].pt() > 20.)
      continue;

    auto& jet(event.jets[0]);

    if (std::abs(TVector2::Phi_mpi_pi(jet.phi() - vPt.Phi())) < 2.9)
      continue;

    TVector2 jPt;
    jPt.SetMagPhi(jet.pt(), jet.phi());

    balance = vPt.Mod() + (jPt * vPt.Unit());

    output->Fill();
  }

  _outputFile->cd();
  output->Write();
}
